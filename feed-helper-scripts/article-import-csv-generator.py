"""
Article CSV Generator for Bulk Import
Processes Word documents and matches images to generate a CSV for article import.
"""

import os
from dotenv import load_dotenv
load_dotenv()
import csv
import shutil
import zipfile
import argparse
import antiword
from pathlib import Path
from docx import Document
from datetime import datetime, timedelta
from collections import Counter
import ghl_api

# Try to import spaCy for entity extraction (optional)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    print("⚠ spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")
    print("  Entity extraction will be skipped.\n")



import subprocess
def convert_word_to_html(input_path, tmp_dir):
    """
    Converts a .doc or .docx file to HTML using soffice (LibreOffice CLI).
    Returns the path to the generated HTML file.
    """
    html_name = Path(input_path).stem + '.html'
    html_path = os.path.join(tmp_dir, html_name)
    if os.path.exists(html_path):
        os.remove(html_path)
    cmd = [
        'soffice',
        '--headless',
        '--convert-to', 'html',
        '--outdir', tmp_dir,
        input_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"LibreOffice conversion failed for {input_path}: {e}")
        return None
    if not os.path.exists(html_path):
        print(f"HTML not created for {input_path}")
        return None
    return html_path

def extract_html_from_word(word_path, tmp_dir):
    """
    Converts .doc or .docx to HTML and returns HTML string.
    """
    html_path = convert_word_to_html(word_path, tmp_dir)
    if not html_path:
        return '', []
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Only use the contents of the <body> tag if present
    body = soup.body
    if body:
        content_soup = BeautifulSoup(str(body), 'html.parser')
        body.unwrap()  # Remove the <body> tag itself
    else:
        content_soup = soup
    # Remove all <style> tags, unwrap <font> tags, and remove inline style attributes
    for style_tag in content_soup.find_all('style'):
        style_tag.decompose()
    for font_tag in content_soup.find_all('font'):
        font_tag.unwrap()
    for tag in content_soup.find_all(True):
        if tag.has_attr('style'):
            del tag['style']
        if tag.has_attr('face'):
            del tag['face']
        if tag.has_attr('size'):
            del tag['size']
        if tag.has_attr('align'):
            del tag['align']
    # Remove the first heading (title) if present, else use the first <p> as the title
    title_text = None
    import re
    first_heading = content_soup.find(['h1', 'h2', 'h3'])
    if first_heading:
        # Use separator=' ' to insert a space for each tag boundary
        raw_title = first_heading.get_text(separator=' ', strip=True)
        # Collapse all whitespace to a single space
        title_text = re.sub(r'\s+', ' ', raw_title).strip()
        first_heading.decompose()
    else:
        first_para = content_soup.find('p')
        if first_para:
            raw_title = first_para.get_text(separator=' ', strip=True)
            title_text = re.sub(r'\s+', ' ', raw_title).strip()
            first_para.decompose()
    

    # Attempt to extract author from the first 3 <p> tags after title removal
    author_name = None
    import re
    p_tags = content_soup.find_all('p', limit=3)
    for p in p_tags:
        para_text = p.get_text(separator=' ', strip=True)
        # Match patterns like 'By John Doe', 'by: Jane Smith', etc.
        match = re.match(r'by[:\s]+([\w\-\'\"\.\s]+)', para_text, re.IGNORECASE)
        if match:
            # Normalize whitespace and strip
            author_name = re.sub(r'\s+', ' ', match.group(1)).strip(' .,:;\'\"')
            p.decompose()
            break

    # Remove empty <p> tags
    for p in content_soup.find_all('p'):
        if not p.get_text(strip=True):
            p.decompose()

    # Get cleaned HTML
    cleaned_html = str(content_soup)
    # Write beautified HTML for debugging
    try:
        pretty_html = content_soup.prettify()
        base_name = os.path.splitext(os.path.basename(word_path))[0]
        beautified_path = os.path.join(tmp_dir, base_name + '.beautified.html')
        with open(beautified_path, 'w', encoding='utf-8') as f:
            f.write(pretty_html)
    except Exception as e:
        print(f"Could not write beautified HTML: {e}")
    # For meta/description/tags, extract plain text
    text_paragraphs = [p.get_text(strip=True) for p in content_soup.find_all(['p', 'h1', 'h2', 'h3'])]
    return cleaned_html, text_paragraphs, title_text, author_name


def find_matching_images(article_name, image_files, match_length=10):
    """
    Find images where the first ~10 characters of the image filename
    are contained in the article filename.
    """
    article_prefix = article_name[:match_length].lower()
    matching_images = []
    
    for img_file in image_files:
        img_name = Path(img_file).stem.lower()
        # Check if first characters of image are in article name
        if img_name[:match_length] in article_name.lower():
            matching_images.append(img_file)
    
    return matching_images


from entity_extraction import extract_entities


def get_next_sunday(date_obj):
    """Return the next Sunday (or the same day if already Sunday) for a given date object."""
    days_ahead = 6 - date_obj.weekday() if date_obj.weekday() != 6 else 0
    return date_obj + timedelta(days=days_ahead)


def process_directory(input_dir, output_csv, ghl_parent_id=None, category_value=None, author_value=None):
    """Process all Word documents and images in a directory."""
    input_path = Path(input_dir)
    # Use rglob for recursive search
    docx_files = list(input_path.rglob("*.docx")) + list(input_path.rglob("*.doc"))
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.rglob(f"*{ext}"))
        image_files.extend(input_path.rglob(f"*{ext.upper()}"))
    image_files = [str(f) for f in image_files]
    
    print(f"Found {len(docx_files)} Word documents")
    print(f"Found {len(image_files)} images")
    
    # Prepare CSV data
    articles = []
    # Get publish_date_mode from function attribute (default to 'null')
    publish_date_mode = getattr(process_directory, 'publish_date_mode', 'null')
    uploaded_images = {}
    tmp_dir = os.path.join(os.getcwd(), '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        for docx_file in docx_files:
            article_name = docx_file.stem
            # Skip files whose name ends with 'caption' (case-insensitive)
            if article_name.lower().endswith('caption'):
                print(f"Skipping file ending with 'Caption': {docx_file}")
                continue
            print(f"\nProcessing: {article_name}")
            html_content, paragraphs, title_text, extracted_author = extract_html_from_word(str(docx_file), tmp_dir)
            import re
            if title_text:
                # Remove newlines and collapse multiple spaces
                clean_title = re.sub(r'\\s+', ' ', title_text).strip()
            else:
                clean_title = paragraphs[0] if paragraphs else article_name
            title = clean_title
            matching_images = find_matching_images(article_name, image_files)
            featured_image = ""
            if not getattr(process_directory, 'no_image_upload', False):
                # Upload and get GHL URL for the first matching image
                if matching_images:
                    img_path = matching_images[0]
                    if img_path not in uploaded_images:
                        try:
                            img_size = os.path.getsize(img_path)
                            print(f"Uploading image: {img_path} ({img_size} bytes)...")
                        except Exception as e:
                            print(f"Could not get size for {img_path}: {e}")
                            img_size = 'unknown'
                        ghl_url = ghl_api.upload_media(img_path, parent_id=ghl_parent_id)
                        print(f"Upload result for {img_path}: {ghl_url}")
                        uploaded_images[img_path] = ghl_url['url'] if ghl_url and 'url' in ghl_url else Path(img_path).name
                    else:
                        print(f"Image already uploaded this run: {img_path}")
                    featured_image = uploaded_images[img_path]
                else:
                    print(f"No matching images found for article: {article_name}")
            else:
                if matching_images:
                    print(f"(No upload) Would use image: {matching_images[0]}")
            print(f"  - Title: {title[:50]}...")
            print(f"  - Content length: {len(html_content)} chars")
            print(f"  - Matching images: {len(matching_images)}")
            if matching_images and not getattr(process_directory, 'no_image_upload', False):
                print(f"    - Featured: {Path(matching_images[0]).name}")
            meta_desc = paragraphs[2][:160] if len(paragraphs) > 2 else (paragraphs[1][:160] if len(paragraphs) > 1 else title[:160])
            full_text = ' '.join(paragraphs)
            entity_tags = extract_entities(full_text)
            if entity_tags:
                print(f"  - Extracted tags: {entity_tags}")
            # Determine publish date
            if publish_date_mode == 'modified':
                file_date = datetime.fromtimestamp(docx_file.stat().st_mtime)
                publish_date = get_next_sunday(file_date).strftime('%Y-%m-%d')
            else:
                publish_date = ''
            # Generate URL slug from title: remove articles/prepositions, normalize, limit to 72 chars
            def normalize_slug(text):
                import re
                # List of articles and common prepositions to remove
                stopwords = set([
                    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
                    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'with', 'as', 'from', 'into', 'like', 'near', 'off', 'over', 'past', 'per', 'than', 'till', 'upon', 'via', 'with', 'without', 'about', 'after', 'against', 'along', 'among', 'around', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'during', 'except', 'inside', 'onto', 'outside', 'since', 'through', 'toward', 'under', 'underneath', 'until', 'within', 'without'
                ])
                # Remove punctuation, lowercase, split int words
                words = re.sub(r'[^a-z0-9\- ]+', '', text.lower()).split()
                # Remove stopwords
                filtered = [w for w in words if w not in stopwords]
                # Join with hyphens
                slug = '-'.join(filtered)
                # Collapse multiple hyphens
                slug = re.sub(r'-+', '-', slug)
                # Truncate to 72 chars, strip trailing hyphens
                return slug[:72].rstrip('-')
            url_slug = normalize_slug(title)
            article = {
                'URL Slug': url_slug,
                'Publish Date': publish_date,
                'Scheduled Date': '',
                'Blog Post Title': title,
                'Meta description': meta_desc,
                'Meta Image': featured_image,
                'Meta Image Alt text': title,
                'Author': (extracted_author if extracted_author else (author_value or '')),
                'Category ': category_value or '',
                'Blog Post Tags': entity_tags,
                'Blog Post Content': html_content
            }
            articles.append(article)
    finally:
        pass
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    # Write to CSV
    if articles:
        # Match exact column names from sample CSV (note the space in "Category ")
        fieldnames = [
            'URL Slug', 'Publish Date', 'Scheduled Date', 'Blog Post Title',
            'Meta description', 'Meta Image', 'Meta Image Alt text', 'Author',
            'Category ', 'Blog Post Tags', 'Blog Post Content'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)
        
        print(f"\n✓ CSV created: {output_csv}")
        print(f"  Total articles: {len(articles)}")
        if SPACY_AVAILABLE:
            print(f"\n✓ Entity extraction enabled - tags auto-generated")
        print(f"\nNote: URL Slug, Author, and Category are empty.")
        print(f"      These can be filled in manually or the system will auto-generate.")
    else:
        print("\n✗ No articles found to process")


def process_zip(zip_path, output_csv, ghl_parent_id=None, category_value=None, author_value=None):
    """Extract and process a zip file."""
    extract_dir = Path(zip_path).parent / "temp_extract"
    extract_dir.mkdir(exist_ok=True)
    
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Pass through publish_date_mode if set
    if hasattr(process_directory, 'publish_date_mode'):
        process_directory.publish_date_mode = getattr(process_directory, 'publish_date_mode')
    process_directory(extract_dir, output_csv, ghl_parent_id=ghl_parent_id, category_value=category_value, author_value=author_value)
    
    # Optional: Clean up extracted files
    shutil.rmtree(extract_dir)


def main():
    parser = argparse.ArgumentParser(
        description='Generate CSV for bulk article import from Word docs and images'
    )
    parser.add_argument('input', help='Input directory or zip file')
    parser.add_argument('--no-image-upload', action='store_true', help='Do not upload images, leave Meta Image empty (for testing)')
    parser.add_argument('-o', '--output', default='articles_import.csv',
                       help='Output CSV file path')
    parser.add_argument('-m', '--match-length', type=int, default=10,
                       help='Number of characters to match between filenames')
    parser.add_argument('--publish-date', choices=['null', 'modified'], default='null',
                       help='Set Publish Date to null (default) or file modified date')
    parser.add_argument('--ghl-parent-id', default=None, help='GHL Media Storage parentId (folder)')
    parser.add_argument('--category', default=None, help='Category to use for all articles (Category column)')
    parser.add_argument('--author', default=None, help='Author to use for all articles (Author column)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    # Set the publish_date_mode and no_image_upload as attributes for process_directory
    process_directory.publish_date_mode = args.publish_date
    process_directory.no_image_upload = args.no_image_upload
    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return
    if input_path.suffix == '.zip':
        process_zip(args.input, args.output, ghl_parent_id=args.ghl_parent_id, category_value=args.category, author_value=args.author)
    elif input_path.is_dir():
        process_directory(args.input, args.output, ghl_parent_id=args.ghl_parent_id, category_value=args.category, author_value=args.author)
    else:
        print("Error: Input must be a directory or zip file")


if __name__ == "__main__":
    main()
