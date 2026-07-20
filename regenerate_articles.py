#!/usr/bin/env python3
"""
Regenerate all existing articles with the new template.
Reads existing HTML → extracts content → re-renders with new generate_article_html()
"""
import json, re, sys
from pathlib import Path

BASE = Path.home() / 'speedreading-research'

# Need to import from generate_article
sys.path.insert(0, str(BASE))
from generate_article import generate_article_html, get_category, CATEGORY_BADGES

ARTICLES_DIR = BASE / 'articles'
ARTICLES_JSON = BASE / 'articles.json'

def extract_from_html(filepath):
    """Parse an existing article HTML to extract item dict fields."""
    html = filepath.read_text(encoding='utf-8')
    
    # Extract title from h1
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = h1_match.group(1).strip() if h1_match else 'Unknown'
    
    # Extract content from article-content div
    # The content is between <div class="article-content"> and </div> before apply-box or article-footer
    content_match = re.search(
        r'<div class="article-content">(.*?)(?:</div>\s*<div class="apply-box"|</div>\s*<div class="article-footer")',
        html, re.DOTALL
    )
    
    if not content_match:
        # Try alternative pattern (old format without apply-box)
        content_match = re.search(
            r'<div class="article-content">(.*?)</div>\s*(?:\n\s*<div class="article-footer|\n\s*<div class="apply-box)',
            html, re.DOTALL
        )
    
    if content_match:
        content_html = content_match.group(1)
        # Extract text from HTML, keeping paragraph structure
        text = content_html
        # Decode HTML entities first
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        # Clean up artifacts from previous bad formatting
        text = re.sub(r'"stat">', '', text)
        # Replace <p> and </p> with newlines
        text = re.sub(r'</?p>', '\n', text)
        text = re.sub(r'</?li>', '\n', text)
        text = re.sub(r'</?ul[^>]*>', '\n', text)
        text = re.sub(r'</?h3[^>]*>', '\n', text)
        text = re.sub(r'</?div[^>]*>', '', text)
        text = re.sub(r'<[^>]+>', '', text)  # strip remaining tags
        # Clean up excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
    else:
        text = ''
    
    # Extract source from meta
    source_match = re.search(r'📖\s*(.*?)(?:</span>|$)', html)
    if not source_match:
        source_match = re.search(r'🔗.*?<a[^>]*>(.*?)</a>', html)
    source = source_match.group(1).strip() if source_match else ''
    
    # Extract apply — handle both old (direct <p> in apply-box) and new format
    apply = ''
    apply_match_new = re.search(
        r'<div class="apply-body">\s*<p>(.*?)</p>',
        html, re.DOTALL
    )
    if apply_match_new:
        apply = apply_match_new.group(1).strip()
    else:
        apply_match_old = re.search(
            r'<div class="apply-box">(?:.*?)<p>(.*?)</p>',
            html, re.DOTALL
        )
        if apply_match_old:
            apply = apply_match_old.group(1).strip()
    
    if apply:
        apply = re.sub(r'<[^>]+>', '', apply)
        apply = apply.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        apply = apply.replace('&quot;', '"').replace('&#39;', "'")
    
    # Extract date and time from filename
    filename = filepath.name
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    date_str = date_match.group(1) if date_match else '2026-07-15'
    
    # Determine time from content (check for 🌅 or 🌆)
    time_of_day = 'sáng'
    if '🌆' in html or 'tối' in html.lower()[:2000]:
        time_of_day = 'tối'
    
    return {
        'title': title,
        'content': text,
        'source': source,
        'apply': apply,
        'tags': [],  # Will be filled from articles.json
        'date': date_str,
        'time': time_of_day,
    }


def main():
    print("🚀 Regenerating all articles with new template...\n")
    
    # Load existing index to get tags
    articles_index = json.loads(ARTICLES_JSON.read_text(encoding='utf-8'))
    index_by_filename = {a['filename']: a for a in articles_index}
    
    html_files = sorted(ARTICLES_DIR.glob('*.html'))
    print(f"📁 Found {len(html_files)} article HTML files")
    print(f"📋 Index has {len(articles_index)} entries\n")
    
    success = 0
    errors = 0
    skipped = 0
    
    for fp in html_files:
        fname = fp.name
        try:
            # Extract data from existing HTML
            item = extract_from_html(fp)
            
            # Merge with index data (tags, etc.)
            if fname in index_by_filename:
                idx = index_by_filename[fname]
                item['tags'] = idx.get('tags', [])
                item['time'] = idx.get('time', item['time'])
                # Keep original source if available
                if not item['source']:
                    item['source'] = idx.get('source', '')
            else:
                item['tags'] = []
            
            # Regenerate HTML
            new_html = generate_article_html(item)
            fp.write_text(new_html, encoding='utf-8')
            title_short = item['title'][:50]
            print(f"  ✅ {title_short}")
            success += 1
            
        except Exception as e:
            print(f"  ❌ {fp.name}: {e}")
            errors += 1
    
    print(f"\n🎉 Done! {success} regenerated, {errors} errors")
    
    # Deploy reminder
    print("\n🔗 Run: python3 update_website.py")


if __name__ == '__main__':
    main()