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


def extract_text_from_docx(docx_path):
    """
    Extract text content from a Word document, preserving bold, italic, underline, and hyperlinks.
    Returns: title, subtitle (if exists), html_content, plain_paragraphs
    """
    try:
        doc = Document(docx_path)
        paragraphs = []
        html_paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                # Build HTML for paragraph with formatting
                html_text = ""
                for run in para.runs:
                    run_text = run.text
                    if not run_text:
                        continue
                    # Formatting
                    if run.bold:
                        run_text = f"<b>{run_text}</b>"
                    if run.italic:
                        run_text = f"<i>{run_text}</i>"
                    if run.underline:
                        run_text = f"<u>{run_text}</u>"
                    html_text += run_text
                # Hyperlinks (python-docx does not natively support hyperlinks in runs)
                # Try to extract hyperlinks from relationships
                # Fallback: If paragraph has a hyperlink, add it
                # This is a best-effort; true hyperlink support requires lxml or docx2python
                if hasattr(para, 'hyperlink') and para.hyperlink:
                    html_text = f'<a href="{para.hyperlink}">{html_text}</a>'
                paragraphs.append({
                    'text': para.text.strip(),
                    'style': para.style.name if para.style else 'Normal'
                })
                html_paragraphs.append(html_text)
        if not paragraphs:
            return "", "", "", []
        title = paragraphs[0]['text']
        subtitle = ""
        body_start_idx = 1
        if len(paragraphs) > 1:
            second_para = paragraphs[1]['text']
            if len(second_para) < 150 and len(paragraphs) > 2:
                subtitle = second_para
                body_start_idx = 2
        html_content = ""
        if subtitle:
            html_content += f"<h2>{subtitle}</h2>\n\n"
        for i, para in enumerate(paragraphs[body_start_idx:], start=body_start_idx):
            text = para['text']
            html_text = html_paragraphs[i]
            if len(text) < 80 and (text.isupper() or 'Heading' in para['style']):
                html_content += f"<h3>{html_text}</h3>\n\n"
            else:
                html_content += f"<p>{html_text}</p>\n\n"
        plain_paragraphs = [p['text'] for p in paragraphs]
        return title, subtitle, html_content.strip(), plain_paragraphs
    except Exception as e:
        print(f"Error reading {docx_path} as docx: {e}")
        # Try to load as .doc using antiword Python module if available
        try:
            import antiword
            text = antiword.get_text(docx_path)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                return "", "", "", []
            title = lines[0]
            subtitle = lines[1] if len(lines) > 1 and len(lines[1]) < 150 else ""
            body_start_idx = 2 if subtitle else 1
            html_content = ""
            if subtitle:
                html_content += f"<h2>{subtitle}</h2>\n\n"
            for line in lines[body_start_idx:]:
                if len(line) < 80 and line.isupper():
                    html_content += f"<h3>{line}</h3>\n\n"
                else:
                    html_content += f"<p>{line}</p>\n\n"
            return title, subtitle, html_content.strip(), lines
        except ImportError:
            print(f"antiword Python module not installed; cannot read {docx_path} as .doc")
            return "", "", "", []
        except Exception as e2:
            print(f"Error reading {docx_path} as .doc with antiword: {e2}")
            return "", "", "", []


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


def extract_entities(text, top_n=5):
    """
    Extract top N named entities from text using spaCy.
    Returns comma-separated string of entities.
    """
    if not SPACY_AVAILABLE or not text:
        return ""
    
    try:
        # Process text with spaCy
        doc = nlp(text[:10000])  # Limit to first 10k chars for performance
        
        # Extract entities, filtering for useful types
        # PERSON, ORG (organizations), GPE (countries/cities), EVENT, PRODUCT
        entity_types = {'PERSON', 'ORG', 'GPE', 'EVENT', 'PRODUCT', 'LAW'}
        entities = [
            ent.text.strip() 
            for ent in doc.ents 
            if ent.label_ in entity_types and len(ent.text.strip()) > 2
        ]
        
        # Count frequency and get top N
        entity_counts = Counter(entities)
        top_entities = [entity for entity, count in entity_counts.most_common(top_n)]
        
        return ', '.join(top_entities)
    except Exception as e:
        print(f"    ⚠ Entity extraction failed: {e}")
        return ""


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
    for docx_file in docx_files:
        article_name = docx_file.stem
        print(f"\nProcessing: {article_name}")
        title, subtitle, html_content, paragraphs = extract_text_from_docx(docx_file)
        if not title:
            title = article_name
        matching_images = find_matching_images(article_name, image_files)
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
            featured_image = ""
        print(f"  - Title: {title[:50]}...")
        if subtitle:
            print(f"  - Subtitle: {subtitle[:50]}...")
        print(f"  - Content length: {len(html_content)} chars")
        print(f"  - Matching images: {len(matching_images)}")
        if matching_images:
            print(f"    - Featured: {Path(matching_images[0]).name}")
        meta_desc = ""
        if len(paragraphs) > 2:
            meta_desc = paragraphs[2][:160]
        elif len(paragraphs) > 1:
            meta_desc = paragraphs[1][:160]
        else:
            meta_desc = title[:160]
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
        article = {
            'URL Slug': '',
            'Publish Date': publish_date,
            'Scheduled Date': '',
            'Blog Post Title': title,
            'Meta description': meta_desc,
            'Meta Image': featured_image,
            'Meta Image Alt text': title,
            'Author': author_value or '',
            'Category ': category_value or '',
            'Blog Post Tags': entity_tags,
            'Blog Post Content': html_content
        }
        articles.append(article)
    
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
    # Set the publish_date_mode as an attribute for process_directory
    process_directory.publish_date_mode = args.publish_date
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
