#!/usr/bin/env python3
"""
Tạo trang HTML bài nghiên cứu độc lập
======================================
Mỗi bài nghiên cứu = 1 trang HTML riêng, không gộp chung.

Cách dùng:
  python3 generate_article.py --data '{
    "title": "...",
    "content": "...",
    "source": "...",
    "apply": "...",
    "tags": ["sách", "speed reading"],
    "date": "2026-07-16",
    "time": "sáng"
  }'
"""
import json, os, re, sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / 'speedreading-research'
ARTICLES_DIR = BASE_DIR / 'articles'
ARTICLES_JSON = BASE_DIR / 'articles.json'

TAG_COLORS = {
    'sách':'green', 'diễn giả':'pink', 'xu hướng':'amber',
    'nghiên cứu':'', 'bài học':'pink', 'khoa học':'green',
    'não bộ':'green', 'học tập':'', 'speed reading':'amber',
    'phát triển':'pink', 'productivity':'amber',
    'ai':'purple', 'công nghệ':'purple', 'tool':'purple',
    'app':'purple', 'công cụ':'purple',
}

CATEGORY_BADGES = {
    'reading': ('📚', '#34d399'),
    'ai': ('🤖', '#a855f7'),
}

def get_category(tags):
    tl = ' '.join(tags).lower()
    if any(k in tl for k in ['ai','công nghệ','tool','app','công cụ','technology']):
        return 'ai'
    return 'reading'

def slugify(text):
    """Tạo URL-friendly slug từ tiếng Việt"""
    # Chuyển về ASCII
    s = text.lower().strip()
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[đ]', 'd', s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s)
    s = s.strip('-')
    # Giới hạn độ dài slug
    words = s.split('-')
    if len(words) > 10:
        words = words[:10]
    return '-'.join(words)


def generate_article_html(item: dict) -> str:
    """Tạo HTML cho một bài nghiên cứu độc lập"""
    title = item.get('title', 'Bài nghiên cứu')
    content = item.get('content', '')
    source = item.get('source', '')
    apply = item.get('apply', '')
    tags = item.get('tags', [])
    date_str = item.get('date', datetime.now().strftime('%Y-%m-%d'))
    time_of_day = item.get('time', 'sáng')
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    weekday_map = {'Monday':'Thứ Hai','Tuesday':'Thứ Ba','Wednesday':'Thứ Tư',
                   'Thursday':'Thứ Năm','Friday':'Thứ Sáu','Saturday':'Thứ Bảy','Sunday':'Chủ Nhật'}
    weekday = weekday_map.get(date_obj.strftime('%A'), '')
    emoji = '🌅' if time_of_day == 'sáng' else '🌆'
    
    cat = get_category(tags)
    badge_emoji, badge_color = CATEGORY_BADGES.get(cat, ('📌','#818cf8'))
    cat_label = 'Sách & Đọc' if cat == 'reading' else 'AI & Công nghệ'
    
    # Tags HTML
    tag_color = ''
    for tag in tags:
        tl = tag.lower().strip()
        for k, c in TAG_COLORS.items():
            if k in tl:
                tag_color = c
                break
    tag_cls = f'tag {tag_color}' if tag_color else 'tag'
    tags_html = ''.join([f'<span class="{tag_cls}">{t}</span>' for t in tags])
    
    # Source HTML
    src_html = ''
    if source:
        if source.startswith('http'):
            src_html = f'🔗 <a href="{source}" target="_blank" style="color:#818cf8;">Nguồn tham khảo</a>'
        else:
            src_html = f'📖 {source}'
    
    # Apply HTML
    apply_html = ''
    if apply:
        apply_html = f'''
        <div class="apply-box">
            <div class="label">💡 Ứng dụng cho Speed Reading</div>
            <p>{apply}</p>
        </div>'''
    
    # Content paragraphs
    content_html = ''.join(
        f'<p>{p}</p>' for p in content.split('\n\n') if p.strip()
    )
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .article-header {{
            margin-bottom: 40px; padding-bottom: 30px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}
        .article-meta {{
            display: flex; gap: 16px; align-items: center; flex-wrap: wrap;
            margin-bottom: 16px; font-size: .85em; color: #8b8ba7;
        }}
        .article-meta .cat-badge {{
            display: inline-block; padding: 4px 14px; border-radius: 8px;
            font-size: .8em; font-weight: 600;
            border: 1px solid;
        }}
        .article-title {{
            font-size: clamp(1.4em,3vw,2em); font-weight: 700; line-height: 1.4;
            margin-bottom: 12px;
        }}
        .article-content {{
            font-size: 1.05em; line-height: 1.9; color: #e0e0f0;
        }}
        .article-content p {{ margin-bottom: 18px; }}
        .article-content p:last-child {{ margin-bottom: 0; }}
        .article-footer {{
            margin-top: 40px; padding-top: 24px;
            border-top: 1px solid rgba(255,255,255,0.06);
            display: flex; gap: 12px; flex-wrap: wrap;
        }}
        .article-nav {{
            display: flex; justify-content: space-between;
            margin-top: 40px; padding-top: 24px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }}
        .article-nav a {{
            color: #818cf8; text-decoration: none; font-weight: 500;
            transition: color .2s;
        }}
        .article-nav a:hover {{ color: #a78bfa; }}
        @media (max-width: 768px) {{
            .article-content {{ font-size: 1em; }}
        }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back">← Quay về Dashboard</a>
        
        <article>
            <div class="article-header">
                <div class="article-meta">
                    <span class="cat-badge" style="background:{badge_color}15;color:{badge_color};border-color:{badge_color}30;">
                        {badge_emoji} {cat_label}
                    </span>
                    <span>{emoji} {weekday}, {day} tháng {month}</span>
                    {f'<span>{src_html}</span>' if src_html else ''}
                </div>
                <h1 class="article-title">{title}</h1>
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    {tags_html}
                </div>
            </div>
            
            <div class="article-content">
                {content_html}
            </div>
            
            {apply_html}
            
            <div class="article-footer">
                {f'<span class="tag" style="background:rgba(139,139,167,0.1);color:#8b8ba7;">{src_html}</span>' if src_html else ''}
                <span class="tag" style="background:rgba(139,139,167,0.1);color:#8b8ba7;">{emoji} {time_of_day.title()} — {weekday}</span>
            </div>
        </article>
        
        <div class="article-nav">
            <a href="../index.html">← Dashboard</a>
            <a href="#" onclick="window.print()">🖨 In / Lưu PDF</a>
        </div>
    </div>
    <footer>
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a></p>
        <p>Hotline: 0899.320.202 | Email: admin@speedreading.vn</p>
    </footer>
</body>
</html>'''


def update_articles_index(item: dict, filename: str):
    """Cập nhật articles.json"""
    articles = []
    if ARTICLES_JSON.exists():
        try:
            articles = json.loads(ARTICLES_JSON.read_text())
        except:
            pass
    
    title = item.get('title', '')
    date_str = item.get('date', '')
    time_of_day = item.get('time', 'sáng')
    tags = item.get('tags', [])
    cat = get_category(tags)
    
    entry = {
        'title': title,
        'filename': filename,
        'date': date_str,
        'time': time_of_day,
        'cat': cat,
        'tags': tags,
        'source': item.get('source', ''),
        'preview': item.get('content', '')[:150],
    }
    
    # Check if already exists by title
    for i, a in enumerate(articles):
        if a['title'] == title and a['date'] == date_str:
            articles[i] = entry
            break
    else:
        articles.append(entry)
    
    ARTICLES_JSON.write_text(json.dumps(articles, ensure_ascii=False, indent=2))
    print(f"✅ articles.json: {len(articles)} bài viết")
    return entry


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tạo trang HTML bài nghiên cứu độc lập')
    parser.add_argument('--data', help='JSON object bài nghiên cứu')
    parser.add_argument('--file', help='File JSON chứa dữ liệu')
    parser.add_argument('--output', help='Tên file output (mặc định: auto slug)')
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, encoding='utf-8') as f:
            item = json.load(f)
    elif args.data:
        item = json.loads(args.data)
    else:
        print("❌ Cần --data hoặc --file")
        sys.exit(1)
    
    # Tạo slug từ title
    title = item.get('title', 'bai-nghien-cuu')
    slug = slugify(title)
    date_str = item.get('date', datetime.now().strftime('%Y-%m-%d'))
    filename = args.output or f'{date_str}-{slug}.html'
    if not filename.endswith('.html'):
        filename += '.html'
    
    # Tạo HTML
    html = generate_article_html(item)
    output_path = ARTICLES_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {output_path}")
    
    # Cập nhật index
    update_articles_index(item, filename)
    
    print(f"\n📝 {title}")
    print(f"🔗 articles/{filename}")


if __name__ == '__main__':
    main()