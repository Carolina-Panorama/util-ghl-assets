"""
Article CSV Generator for Bulk Import
Processes Word documents and matches images to generate a CSV for article import.
"""

import os
import csv
import shutil
import zipfile
import argparse
from pathlib import Path
from docx import Document
from datetime import datetime
from collections import Counter

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
    Extract text content from a Word document.
    Returns: title, subtitle (if exists), html_content, plain_paragraphs
    """
    try:
        doc = Document(docx_path)
        
        # Extract all paragraphs
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append({
                    'text': para.text.strip(),
                    'style': para.style.name if para.style else 'Normal'
                })
        
        if not paragraphs:
            return "", "", "", []
        
        # First paragraph is the title
        title = paragraphs[0]['text']
        
        # Check if second paragraph might be a subtitle (shorter, different style, etc.)
        subtitle = ""
        body_start_idx = 1
        
        if len(paragraphs) > 1:
            second_para = paragraphs[1]['text']
            # If second paragraph is relatively short, treat as subtitle
            if len(second_para) < 150 and len(paragraphs) > 2:
                subtitle = second_para
                body_start_idx = 2
        
        # Build HTML content with subtitle and body
        html_content = ""
        
        # Add subtitle if it exists
        if subtitle:
            html_content += f"<h2>{subtitle}</h2>\n\n"
        
        # Add body paragraphs
        for para in paragraphs[body_start_idx:]:
            # Check if it looks like a heading (short, might be all caps, etc.)
            text = para['text']
            if len(text) < 80 and (text.isupper() or 'Heading' in para['style']):
                html_content += f"<h3>{text}</h3>\n\n"
            else:
                html_content += f"<p>{text}</p>\n\n"
        
        plain_paragraphs = [p['text'] for p in paragraphs]
        
        return title, subtitle, html_content.strip(), plain_paragraphs
    except Exception as e:
        print(f"Error reading {docx_path}: {e}")
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


def process_directory(input_dir, output_csv):
    """Process all Word documents and images in a directory."""
    input_path = Path(input_dir)
    
    # Find all Word documents
    docx_files = list(input_path.glob("*.docx")) + list(input_path.glob("*.doc"))
    
    # Find all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f"*{ext}"))
        image_files.extend(input_path.glob(f"*{ext.upper()}"))
    
    image_files = [str(f) for f in image_files]
    
    print(f"Found {len(docx_files)} Word documents")
    print(f"Found {len(image_files)} images")
    
    # Prepare CSV data
    articles = []
    
    for docx_file in docx_files:
        article_name = docx_file.stem
        print(f"\nProcessing: {article_name}")
        
        # Extract content
        title, subtitle, html_content, paragraphs = extract_text_from_docx(docx_file)
        
        # If no title found, use filename
        if not title:
            title = article_name
        
        # Find matching images
        matching_images = find_matching_images(article_name, image_files)
        
        # Use first matching image as featured image
        featured_image = Path(matching_images[0]).name if matching_images else ""
        
        print(f"  - Title: {title[:50]}...")
        if subtitle:
            print(f"  - Subtitle: {subtitle[:50]}...")
        print(f"  - Content length: {len(html_content)} chars")
        print(f"  - Matching images: {len(matching_images)}")
        if matching_images:
            print(f"    - Featured: {Path(matching_images[0]).name}")
        
        # Create meta description from first body paragraph or subtitle
        meta_desc = ""
        if len(paragraphs) > 2:
            meta_desc = paragraphs[2][:160]  # First body paragraph
        elif len(paragraphs) > 1:
            meta_desc = paragraphs[1][:160]  # Subtitle or first para
        else:
            meta_desc = title[:160]
        
        # Extract entities for tags
        full_text = ' '.join(paragraphs)
        entity_tags = extract_entities(full_text)
        if entity_tags:
            print(f"  - Extracted tags: {entity_tags}")
        
        # Create article entry matching the CSV format
        article = {
            'URL Slug': '',  # Empty - will be auto-generated
            'Publish Date': '',  # Empty for manual review
            'Scheduled Date': '',  # Empty to keep as draft
            'Blog Post Title': title,
            'Meta description': meta_desc,
            'Meta Image': featured_image,
            'Meta Image Alt text': title,
            'Author': '',  # Empty - can be set manually
            'Category ': '',  # Empty - note the space in column name
            'Blog Post Tags': entity_tags,  # Auto-extracted entities
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


def process_zip(zip_path, output_csv):
    """Extract and process a zip file."""
    extract_dir = Path(zip_path).parent / "temp_extract"
    extract_dir.mkdir(exist_ok=True)
    
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    process_directory(extract_dir, output_csv)
    
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
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return
    
    if input_path.suffix == '.zip':
        process_zip(args.input, args.output)
    elif input_path.is_dir():
        process_directory(args.input, args.output)
    else:
        print("Error: Input must be a directory or zip file")


if __name__ == "__main__":
    main()
