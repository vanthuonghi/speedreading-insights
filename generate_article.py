#!/usr/bin/env python3
"""
Tạo trang HTML bài nghiên cứu độc lập — phiên bản cải tiến
==========================================================
Mỗi bài nghiên cứu = 1 trang HTML riêng với trình bày đẹp, dễ đọc.

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
    words = s.split('-')
    if len(words) > 10:
        words = words[:10]
    return '-'.join(words)


# ============================================================
#  CONTENT ENHANCER — thêm đậm, highlight, blockquote, list
# ============================================================

def enhance_content(text):
    """
    Chuyển plain text content thành HTML giàu typography.
    - Dòng bắt đầu với '•' hoặc '-' → styled list item
    - Số liệu (%) → <strong class="stat">
    - Tên người nổi tiếng → <strong class="person">
    - Tên sách trong '' hoặc "" → <em>
    - Câu hỏi/cảm thán → insight-box
    """
    if not text:
        return ''

    # First, decode any HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")

    lines = text.split('\n')
    result_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        is_bullet = stripped.startswith('•') or (stripped.startswith('-') and not stripped.startswith('--'))
        is_numbered = bool(re.match(r'^\d+[.)]\s', stripped))
        is_empty = not stripped
        is_heading = stripped.endswith(':') and len(stripped) < 80 and not is_bullet and not is_numbered

        # Close list if we were in one
        if in_list and (is_empty or not (is_bullet or is_numbered)):
            result_lines.append('</ul>')
            in_list = False

        if is_empty:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            continue

        # Process the text — add bold/italic
        processed = add_typography(stripped)

        if is_bullet or is_numbered:
            if not in_list:
                result_lines.append('<ul class="styled-list">')
                in_list = True
            content = re.sub(r'^[•\-]\s*', '', processed)
            content = re.sub(r'^\d+[.)]\s*', '', content)
            result_lines.append(f'  <li>{content}</li>')
        elif is_heading:
            result_lines.append(f'<h3 class="section-heading">{processed}</h3>')
        elif len(stripped) > 200 and re.search(r'[!?]$', stripped):
            result_lines.append(f'<div class="insight-box"><p>{processed}</p></div>')
        else:
            result_lines.append(f'<p>{processed}</p>')

    if in_list:
        result_lines.append('</ul>')

    return '\n'.join(result_lines)


def add_typography(text):
    """
    Thêm bold, highlight vào văn bản dựa trên patterns.
    Không dùng italic book-title vì quotes dễ gây xung đột HTML.
    """
    s = text

    # 1. Bold tên người nổi tiếng
    famous_names = [
        'Jim Kwik', 'Andrew Huberman', 'Carol Dweck', 'James Clear',
        'Scott Young', 'Barbara Oakley', 'Cal Newport', 'Warren Buffett',
        'Elon Musk', 'Bill Gates', 'Mark Cuban', 'Hasard Lee',
        'Richard Feynman', 'Stephen Covey', 'Malcolm Gladwell', 'Simon Sinek',
        'Tony Robbins', 'Tim Ferriss', 'Naval Ravikant', 'Ray Kurzweil',
        'Sam Altman', 'Andrej Karpathy', 'Fei-Fei Li', 'Geoffrey Hinton',
        'Yann LeCun', 'Demis Hassabis', 'Satya Nadella', 'Sundar Pichai',
        'Steve Jobs', 'Jeff Bezos', 'Larry Page', 'Sergey Brin',
        'Mark Zuckerberg', 'Jack Ma',
        'Hermann Ebbinghaus', 'Francesco Cirillo', 'Francis P. Robinson',
        'Mihaly Csikszentmihalyi', 'Anders Ericsson', 'Angela Duckworth',
        'Daniel Kahneman', 'Nassim Taleb', 'Jordan Peterson', 'Matt Ridley',
        'Benedict Carey', 'Peter C. Brown', 'Maryanne Wolf', 'Stanislas Dehaene',
        'Michael Merzenich', 'Piotr Wozniak',
        'Dale Carnegie', 'Robert Kiyosaki', 'Napoleon Hill', 'Brian Tracy',
    ]
    for name in famous_names:
        if name.lower() in s.lower():
            idx = s.lower().index(name.lower())
            orig = s[idx:idx+len(name)]
            s = s[:idx] + f'<strong class="person">{orig}</strong>' + s[idx+len(name):]

    # 2. Bold số liệu + đơn vị (giữ nguyên nội dung gốc, không thêm dấu ngoặc)
    s = re.sub(
        r'(\d+[.,]?\d*)\s*(%|triệu|tỷ|USD|VND|ngàn|nghìn|đô la)',
        lambda m: f'<strong class="stat">{m.group(1)}{m.group(2)}</strong>',
        s, flags=re.IGNORECASE
    )
    s = re.sub(
        r'(\d+[.,]?\d*)\s*(năm|ngày|giờ|phút|giây|tuổi|tháng|người|bản|trang)',
        lambda m: f'<strong class="stat">{m.group(1)} {m.group(2)}</strong>',
        s
    )
    s = re.sub(
        r'(\d+[.,]?\d*)%',
        r'<strong class="stat">\1%</strong>',
        s
    )

    return s


def try_fetch_image(article_title, tags):
    """
    Cố gắng lấy ảnh minh hoạ từ Unsplash dựa trên chủ đề.
    Fallback: placeholder gradient nếu không lấy được.
    """
    # Danh sách keywords theo chủ đề
    topic_keywords = {
        'sách': ['book', 'reading', 'library', 'literature', 'bookshelf'],
        'speed reading': ['books', 'reading', 'speed', 'focus', 'study'],
        'não bộ': ['brain', 'mind', 'neuroscience', 'neuron', 'intelligence'],
        'học tập': ['study', 'learning', 'education', 'knowledge', 'student'],
        'khoa học': ['science', 'laboratory', 'research', 'microscope', 'experiment'],
        'công nghệ': ['technology', 'digital', 'ai', 'computer', 'robot'],
        'ai': ['artificial-intelligence', 'robot', 'neural-network', 'code', 'computer'],
        'phát triển': ['growth', 'success', 'motivation', 'mountain', 'sunrise'],
        'nghiên cứu': ['research', 'analysis', 'data', 'chart', 'document'],
        'bài học': ['wisdom', 'philosophy', 'teacher', 'lesson', 'blackboard'],
        'sức khỏe': ['health', 'wellness', 'fitness', 'mindfulness', 'nature'],
        'diễn giả': ['speaker', 'stage', 'presentation', 'audience', 'public-speaking'],
    }
    
    # Tìm keyword phù hợp nhất
    keywords = ['book', 'reading']  # default
    for tag in tags:
        t = tag.lower().strip()
        for key, vals in topic_keywords.items():
            if key in t:
                keywords = vals
                break
    
    # Try to fetch from Unsplash (free, no API key needed for embed)
    import urllib.request
    import random
    
    keyword = random.choice(keywords)
    # Use Unsplash Source API (no key needed, returns random photo)
    unsplash_url = f"https://images.unsplash.com/photo-{random.randint(1500000000, 1600000000)}?w=800&q=80&fit=crop"
    
    return f'<div class="article-image-wrapper"><img src="{unsplash_url}" alt="{keyword}" class="article-image" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>'


# ============================================================
#  THUMBNAIL / COVER IMAGE
# ============================================================

def try_fetch_cover_image(article_title, tags):
    """
    Cố gắng lấy ảnh bìa từ Unsplash.
    Dùng nhiều keyword để có tỷ lệ match cao.
    """
    tag_text = ' '.join(tags).lower()
    # Map topic → Unsplash keyword
    keyword_map = [
        (['sách', 'đọc'], 'book', 'reading,library,literature'),
        (['não bộ', 'thần kinh'], 'brain', 'brain,neuroscience,mind'),
        (['khoa học', 'nghiên cứu'], 'science', 'science,laboratory,research'),
        (['học tập', 'giáo dục'], 'study', 'study,learning,education'),
        (['công nghệ', 'ai', 'tool'], 'technology', 'technology,code,computer'),
        (['sức khỏe'], 'health', 'health,wellness,nature'),
        (['phát triển', 'tư duy'], 'growth', 'growth,motivation,mountain'),
        (['diễn giả'], 'speaker', 'speaker,stage,presentation'),
        (['cuộc sống'], 'lifestyle', 'lifestyle,morning,coffee'),
    ]
    
    query = 'book,reading'  # default fallback
    for keywords, _, q in keyword_map:
        if any(k in tag_text for k in keywords):
            query = q
            break
    
    # Return a placeholder div that Unsplash will fill (hotlink works without API key)
    # Using picsum.photos as reliable free image source
    import random
    seed = hash(article_title) % 1000
    return f"""
    <div class="article-cover">
        <img src="https://picsum.photos/seed/{seed}/900/400" 
             alt="Article cover" class="cover-img" loading="lazy"
             onerror="this.parentElement.style.background='linear-gradient(135deg, #1a1a3e, #2d1b69)'">
    </div>"""


# ============================================================
#  MAIN HTML GENERATOR
# ============================================================

def generate_article_html(item: dict) -> str:
    """Tạo HTML cho một bài nghiên cứu độc lập — phiên bản cải tiến"""
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
    
    # Tags
    tag_color = ''
    for tag in tags:
        tl = tag.lower().strip()
        for k, c in TAG_COLORS.items():
            if k in tl:
                tag_color = c
                break
    tag_cls = f'tag {tag_color}' if tag_color else 'tag'
    tags_html = ''.join([f'<span class="{tag_cls}">{t}</span>' for t in tags])
    
    # Source
    src_html = ''
    if source:
        if source.startswith('http'):
            src_html = f'🔗 <a href="{source}" target="_blank" rel="noopener" class="source-link">Nguồn tham khảo</a>'
        else:
            src_html = f'📖 {source}'
    
    # Apply box
    apply_html = ''
    if apply:
        apply_html = f'''
        <div class="apply-box">
            <div class="apply-icon">💡</div>
            <div class="apply-body">
                <div class="apply-label">Ứng dụng cho Speed Reading</div>
                <p>{apply}</p>
            </div>
        </div>'''
    
    # Content — enhanced with typography
    content_html = enhance_content(content)
    
    # Cover image
    cover_html = try_fetch_cover_image(title, tags)
    
    # Clean title (strip leading emoji for display)
    title_clean = re.sub(r'^[📚🤖🔥🧠💡⏱️🧪🌱🎤💬⚡🔬🎯💊🍊🎭⏰😴🧘🎵🥑💪🚀🌟☕🚨🗣️🔮🧬📊💎🎯💡🙏]\s*', '', title)
    
    # Table of contents for longer content
    toc_html = ''
    para_count = len([l for l in content.split('\n') if l.strip()])
    if para_count > 8:
        # Generate simple TOC from numbered items and headings
        toc_items = []
        for line in content.split('\n'):
            stripped = line.strip()
            if re.match(r'^\d+[.)]\s', stripped):
                item_text = re.sub(r'^\d+[.)]\s*', '', stripped)[:60]
                toc_items.append(item_text)
            elif stripped.endswith(':') and len(stripped) < 60:
                toc_items.append(stripped)
        
        if toc_items:
            toc_html = '<details class="toc"><summary>📑 Mục lục</summary><ol>'
            for ti in toc_items[:10]:
                clean_ti = re.sub(r'^[•\-]\s*', '', ti)
                toc_html += f'<li>{clean_ti}</li>'
            toc_html += '</ol></details>'

    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        /* ===== TYPOGRAPHY ENHANCEMENTS ===== */
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #0a0a1a;
            color: #e4e4f0;
            line-height: 1.8;
            min-height: 100vh;
        }}
        .bg-grid {{
            position:fixed;top:0;left:0;right:0;bottom:0;
            background-image:linear-gradient(rgba(99,102,241,0.03)1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03)1px,transparent 1px);
            background-size:60px 60px;z-index:-1
        }}
        .container {{ max-width: 820px; margin: 0 auto; padding: 0 24px; }}
        .article-page {{ padding: 40px 0 80px; }}
        
        /* Back link */
        .back-link {{
            display: inline-flex; align-items: center; gap: 6px;
            color: #6b6b8a; text-decoration: none; font-size: .88em;
            margin-bottom: 28px; padding: 6px 14px;
            border-radius: 8px; transition: all .2s;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.04);
        }}
        .back-link:hover {{ color: #818cf8; background: rgba(99,102,241,0.06); border-color: rgba(99,102,241,0.15); }}

        /* ===== COVER IMAGE ===== */
        .article-cover {{
            border-radius: 18px; overflow: hidden; margin-bottom: 32px;
            position: relative; background: linear-gradient(135deg, #1a1a3e, #2d1b69);
            box-shadow: 0 8px 40px rgba(0,0,0,0.3);
        }}
        .cover-img {{
            width: 100%; height: auto; max-height: 400px;
            object-fit: cover; display: block;
            transition: transform .5s ease;
        }}
        .article-cover:hover .cover-img {{
            transform: scale(1.02);
        }}

        /* ===== HEADER ===== */
        .article-header {{
            margin-bottom: 36px; padding-bottom: 28px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}
        .article-meta {{
            display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
            margin-bottom: 14px; font-size: .82em; color: #8b8ba7;
        }}
        .article-meta .cat-badge {{
            display: inline-flex; align-items: center; gap: 4px;
            padding: 4px 14px; border-radius: 8px;
            font-size: .78em; font-weight: 600; border: 1px solid;
        }}
        .article-title {{
            font-size: clamp(1.5em,3.5vw,2.2em); font-weight: 800; line-height: 1.35;
            margin-bottom: 12px;
            background: linear-gradient(135deg,#e0e0f0,#c4b5fd);
            -webkit-background-clip: text;-webkit-text-fill-color: transparent;background-clip: text;
        }}
        .article-tags {{ display: flex; gap: 6px; flex-wrap: wrap; }}

        /* ===== TABLE OF CONTENTS ===== */
        .toc {{
            background: rgba(99,102,241,0.05);
            border: 1px solid rgba(99,102,241,0.12);
            border-radius: 12px; padding: 8px 16px; margin-bottom: 24px;
            cursor: pointer;
        }}
        .toc summary {{
            font-weight: 600; font-size: .88em; color: #818cf8;
            padding: 6px 0; cursor: pointer;
        }}
        .toc ol {{
            margin: 8px 0 4px; padding-left: 24px;
            font-size: .85em; color: #a0a0b8; line-height: 1.8;
        }}
        .toc ol li {{ padding: 2px 0; }}

        /* ===== CONTENT ===== */
        .article-content {{
            font-size: 1.05em; line-height: 1.9; color: #ddddf0;
        }}
        .article-content p {{
            margin-bottom: 18px;
        }}
        .article-content p:last-child {{ margin-bottom: 0; }}
        
        /* Section heading (line ending with colon) */
        .section-heading {{
            font-size: 1.1em; font-weight: 700; color: #c4b5fd;
            margin: 24px 0 12px; padding: 0;
            border: none;
        }}

        /* ===== STYLED LIST ===== */
        .styled-list {{
            list-style: none; padding: 0; margin: 0 0 18px 0;
        }}
        .styled-list li {{
            padding: 8px 0 8px 28px;
            position: relative; line-height: 1.7;
            color: #d0d0e8;
        }}
        .styled-list li::before {{
            content: '✦';
            position: absolute; left: 4px; top: 8px;
            color: #818cf8; font-size: .85em;
        }}
        .styled-list li:nth-child(2n)::before {{ color: #a855f7; }}
        
        /* ===== KEY INSIGHT / HIGHLIGHT ===== */
        .insight-box {{
            background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(168,85,247,0.05));
            border-left: 3px solid #818cf8;
            border-radius: 0 12px 12px 0;
            padding: 16px 20px; margin: 18px 0;
        }}
        .insight-box p {{
            margin: 0; color: #c8c8e8; font-style: italic;
            font-size: .95em;
        }}

        /* ===== INLINE TYPOGRAPHY ===== */
        strong.stat {{
            color: #fbbf24;
            font-weight: 700;
        }}
        strong.person {{
            color: #818cf8;
            font-weight: 700;
        }}
        /* ===== APPLY BOX ===== */
        .apply-box {{
            display: flex; gap: 14px;
            background: linear-gradient(135deg, rgba(52,211,153,0.06), rgba(16,185,129,0.03));
            border: 1px solid rgba(52,211,153,0.12);
            border-radius: 14px; padding: 20px; margin-top: 32px;
        }}
        .apply-icon {{
            font-size: 1.8em; line-height: 1; flex-shrink: 0;
            margin-top: 2px;
        }}
        .apply-body {{ flex: 1; }}
        .apply-label {{
            font-weight: 700; font-size: .92em; color: #34d399;
            margin-bottom: 8px;
        }}
        .apply-body p {{
            font-size: .92em; color: #b0b0c8; line-height: 1.7; margin: 0;
        }}

        /* ===== FOOTER ===== */
        .article-footer {{
            margin-top: 36px; padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.06);
            display: flex; gap: 10px; flex-wrap: wrap;
            align-items: center;
        }}
        .footer-tag {{
            display: inline-block;
            padding: 3px 12px; border-radius: 6px;
            font-size: .78em; color: #6b6b8a;
            background: rgba(139,139,167,0.08);
        }}
        .article-nav {{
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 36px; padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }}
        .article-nav a {{
            color: #818cf8; text-decoration: none; font-weight: 500;
            font-size: .9em; transition: color .2s;
            display: inline-flex; align-items: center; gap: 6px;
        }}
        .article-nav a:hover {{ color: #a78bfa; }}

        /* ===== READING PROGRESS ===== */
        .reading-progress {{
            position: fixed; top: 0; left: 0; right: 0; height: 3px;
            background: rgba(255,255,255,0.03); z-index: 100;
        }}
        .reading-progress .bar {{
            height: 100%; width: 0%;
            background: linear-gradient(90deg, #818cf8, #a855f7);
            transition: width .1s linear;
        }}

        /* ===== FOOTER (page) ===== */
        .page-footer {{
            text-align: center; padding: 30px 20px;
            color: #5a5a7a; font-size: .82em;
            border-top: 1px solid rgba(255,255,255,0.04);
            margin-top: 40px;
        }}
        .page-footer a {{ color: #818cf8; text-decoration: none; }}
        .page-footer a:hover {{ text-decoration: underline; }}

        /* ===== PRINT ===== */
        @media print {{
            .reading-progress, .back-link, .article-nav {{ display: none !important; }}
            .article-cover {{ break-inside: avoid; box-shadow: none; }}
            body {{ background: white; color: black; }}
            .article-title {{ -webkit-text-fill-color: #1a1a2e; }}
        }}

        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {{
            .container {{ padding: 0 16px; }}
            .article-content {{ font-size: 1em; }}
            .article-page {{ padding: 24px 0 60px; }}
            .apply-box {{ flex-direction: column; gap: 10px; }}
            .article-cover {{ border-radius: 12px; }}
        }}
        @media (max-width: 480px) {{
            .article-title {{ font-size: 1.3em; }}
            .article-meta {{ font-size: .75em; gap: 8px; }}
            .insight-box {{ padding: 12px 14px; }}
        }}
    </style>
</head>
<body>
    <div class="reading-progress"><div class="bar" id="progress-bar"></div></div>
    <div class="bg-grid"></div>
    <div class="container article-page">
        <a href="../index.html" class="back-link">← Quay về Dashboard</a>
        
        {cover_html}
        
        <article>
            <div class="article-header">
                <div class="article-meta">
                    <span class="cat-badge" style="background:{badge_color}15;color:{badge_color};border-color:{badge_color}30;">
                        {badge_emoji} {cat_label}
                    </span>
                    <span>{emoji} {weekday}, {day} tháng {month}</span>
                    <span class="footer-tag">{src_html}</span>
                </div>
                <h1 class="article-title">{title_clean}</h1>
                <div class="article-tags">
                    {tags_html}
                </div>
            </div>
            
            {toc_html}
            
            <div class="article-content">
                {content_html}
            </div>
            
            {apply_html}
            
            <div class="article-footer">
                <span class="footer-tag" style="background:rgba(139,139,167,0.08)">{src_html}</span>
                <span class="footer-tag">{emoji} {time_of_day.title()} — {weekday}</span>
            </div>
        </article>
        
        <div class="article-nav">
            <a href="../index.html">← Dashboard</a>
            <a href="#" onclick="window.print()">🖨 In / Lưu PDF</a>
        </div>
    </div>
    
    <footer class="page-footer">
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a> — Hotline: 0899.320.202</p>
    </footer>

    <script>
        // Reading progress bar
        window.addEventListener('scroll', function() {{
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
            document.getElementById('progress-bar').style.width = progress + '%';
        }});
    </script>
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
    source = item.get('source', '')
    content = item.get('content', '')
    
    entry = {
        'title': title,
        'filename': filename,
        'date': date_str,
        'time': time_of_day,
        'cat': cat,
        'tags': tags,
        'source': source,
        'preview': content[:200] if content else '',
    }
    
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
    
    title = item.get('title', 'bai-nghien-cuu')
    slug = slugify(title)
    date_str = item.get('date', datetime.now().strftime('%Y-%m-%d'))
    filename = args.output or f'{date_str}-{slug}.html'
    if not filename.endswith('.html'):
        filename += '.html'
    
    html = generate_article_html(item)
    output_path = ARTICLES_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {output_path}")
    
    update_articles_index(item, filename)
    
    print(f"\n📝 {title}")


if __name__ == '__main__':
    main()