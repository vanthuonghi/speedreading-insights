#!/usr/bin/env python3
"""Extract content from all HTML files in speedreading-vn-main/static into a searchable knowledge base."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser

STATIC_DIR = Path("/home/vider/speedreading-research/Speed Reading/speedreading-vn-main/static")
OUTPUT_PATH = Path("/home/vider/speedreading-research/Speed Reading/speedreading-vn-main/static_knowledge_base.json")

class SimpleHTMLContentExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.in_style = False
        self.text_parts = []
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.in_script = True if tag == "script" else self.in_script
            self.in_style = True if tag == "style" else self.in_style
            
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_script = False
            self.in_style = False
            
    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            text = data.strip()
            if text:
                self.text_parts.append(text)
    
    def get_content(self):
        return "\n".join(self.text_parts)

def extract_title(content):
    """Extract title from HTML content."""
    match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_meta_description(content):
    """Extract meta description from HTML content."""
    match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def extract_headings(content):
    """Extract all headings from HTML content."""
    headings = []
    for match in re.finditer(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE | re.DOTALL):
        tag_content = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        if tag_content:
            headings.append(tag_content)
    return headings

def clean_text(text):
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove script-like patterns
    text = re.sub(r'const\s+\w+\s*=\s*', '', text)
    text = re.sub(r'import\s+.*', '', text)
    text = re.sub(r'export\s+', '', text)
    # Keep only Vietnamese, English, numbers, and common punctuation
    text = re.sub(r'[^\w\s\.,!?;:()\-+/%đĐăĂâÂêÔôơƠưƯàÀảẢãÃáÁạẠầẦẩẨẫẪấẤậẬằẰẳẲẵẴắẮặẶđĐẽẼéÉèÈẻẺẼéÉẹẸềỀểỂễỄếẾệỆìÌỉỈĩĨíÍịỊòÒỏỎõÕóÓọỌồỒổỔỗỖốỐộỘờỜởỞỡỠớỚợỢùÙủỦũŨúÚụỤừỪửỬữỮứỨựỰỳỲỷỶỹỸýÝỵỴ\s]', '', text, flags=re.UNICODE)
    text = text.strip()
    if len(text) < 5:  # Skip very short fragments
        return ""
    return text

def classify_page(filename):
    """Classify page type based on filename."""
    name = filename.lower()
    if any(x in name for x in ["home", "index", "trang-chu"]):
        return "Trang chủ"
    elif any(x in name for x in ["daotao", "training", "hoc"]):
        return "Đào tạo"
    elif any(x in name for x in ["payment", "thanhtoan"]):
        return "Thanh toán"
    elif any(x in name for x in ["sp-online", "zoom", "coach"]):
        return "Khóa học Zoom"
    elif any(x in name for x in ["sp-video", "video"]):
        return "Khóa video"
    elif any(x in name for x in ["free", "webinar"]):
        return "Webinar miễn phí"
    elif any(x in name for x in ["book", "sach", "ebook"]):
        return "Sách/Ebook"
    elif any(x in name for x in ["tool", "cong-cu"]):
        return "Công cụ"
    elif any(x in name for x in ["post", "review", "camnhan", "testimonial"]):
        return "Review/Cảm nhận"
    elif any(x in name for x in ["study", "hoctap"]):
        return "Học tập"
    elif any(x in name for x in ["intro", "gioi-thieu"]):
        return "Giới thiệu"
    elif any(x in name for x in ["seo"]):
        return "SEO"
    elif any(x in name for x in ["paymentcoach", "paymentvideo"]):
        return "Thanh toán khóa học"
    elif any(x in name for x in ["ws", "workshop"]):
        return "Workshop"
    else:
        return "Khác"

def extract_key_content(text, max_length=500):
    """Extract key content from page text."""
    # Remove boilerplate
    lines = text.split('\n')
    good_lines = []
    
    skip_patterns = [
        r'^import\s', r'^export\s', r'^const\s+\w+\s*=', r'^let\s+\w+\s*=',
        r'^function\s', r'^class\s', r'^\/\/\s', r'^\s*\/\*', r'^\s*\*',
        r'^<script', r'^<\/script>', r'^<style', r'^<\/style>',
        r'^https?:\/\/', r'^img\.', r'^static\.',
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip lines matching boilerplate patterns
        skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line):
                skip = True
                break
        if skip:
            continue
        # Keep meaningful content
        if len(line) > 10 and len(line) < 500:
            good_lines.append(line)
    
    # Join and truncate
    content = ' '.join(good_lines)
    content = re.sub(r'\s+', ' ', content).strip()
    if len(content) > max_length:
        content = content[:max_length] + "..."
    return content

def main():
    html_files = sorted(STATIC_DIR.glob("*.html"))
    print(f"📄 Found {len(html_files)} HTML files")
    
    knowledge_base = []
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            
            # Extract basic info
            title = extract_title(content)
            description = extract_meta_description(content)
            headings = extract_headings(content)
            
            # Extract text content
            parser = SimpleHTMLContentExtractor()
            parser.feed(content)
            raw_text = parser.get_content()
            key_content = extract_key_content(raw_text)
            
            # Classify page
            page_type = classify_page(html_file.name)
            
            entry = {
                "filename": html_file.name,
                "filepath": str(html_file.relative_to(STATIC_DIR)),
                "page_type": page_type,
                "title": title,
                "description": description,
                "headings": headings[:10],  # Top 10 headings
                "key_content": key_content[:800],  # First 800 chars of key content
                "file_size_kb": round(html_file.stat().st_size / 1024, 1),
            }
            
            knowledge_base.append(entry)
            print(f"  ✓ {html_file.name[:50]:<50} [{page_type}]")
            
        except Exception as e:
            print(f"  ✗ {html_file.name}: {e}")
    
    # Save as JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved: {OUTPUT_PATH}")
    print(f"📊 Total pages: {len(knowledge_base)}")
    
    # Summary by type
    type_counts = {}
    for entry in knowledge_base:
        t = entry["page_type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print("\n📊 Pages by type:")
    for t, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {t}: {count}")
    
    return knowledge_base

if __name__ == "__main__":
    kb = main()
    
    # Quick search example
    print("\n🔍 Quick search examples:")
    search_terms = ["payment", "zoom", "video", "testimonial", "tool"]
    for term in search_terms:
        matches = [e for e in kb if term.lower() in e["filename"].lower() or term.lower() in e["key_content"].lower()]
        print(f"  '{term}': {len(matches)} matches")
