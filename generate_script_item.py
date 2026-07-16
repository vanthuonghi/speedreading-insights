#!/usr/bin/env python3
"""
Tạo trang HTML kịch bản video độc lập
======================================
Mỗi kịch bản = 1 trang HTML riêng.

Cách dùng:
  python3 generate_script_item.py --file /tmp/script.json
  python3 generate_script_item.py --data '{"title":"...","script":"...","hashtag":"...","tip":"...","date":"2026-07-16"}'
"""
import json, os, re, sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / 'speedreading-research'
SCRIPTS_DIR = BASE_DIR / 'scripts-items'  # individual script pages
SCRIPTS_JSON = BASE_DIR / 'scripts.json'

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


def generate_html(item: dict) -> str:
    title = item.get('title', 'Kịch bản')
    script = item.get('script', '')
    hashtag = item.get('hashtag', '')
    tip = item.get('tip', '')
    date_str = item.get('date', datetime.now().strftime('%Y-%m-%d'))
    stt = item.get('stt', 1)
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    weekday_map = {'Monday':'Thứ Hai','Tuesday':'Thứ Ba','Wednesday':'Thứ Tư',
                   'Thursday':'Thứ Năm','Friday':'Thứ Sáu','Saturday':'Thứ Bảy','Sunday':'Chủ Nhật'}
    weekday = weekday_map.get(date_obj.strftime('%A'), '')
    
    tip_html = f'<div class="tip-box">💡 <strong>Mẹo quay:</strong> {tip}</div>' if tip else ''
    
    # Script lines -> paragraphs
    script_paragraphs = ''.join(f'<p>{p.strip()}</p>' for p in script.split('\n') if p.strip())
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .script-header {{ margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
        .script-meta {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; font-size: .85em; color: #8b8ba7; }}
        .script-number-badge {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 40px; height: 40px; background: rgba(251,191,36,0.15); color: #fbbf24;
            border-radius: 12px; font-weight: 700; font-size: 1.1em;
        }}
        .script-title {{ font-size: clamp(1.3em,3vw,1.8em); font-weight: 700; margin-bottom: 4px; }}
        .script-content {{
            background: rgba(0,0,0,0.2); border-radius: 16px; padding: 28px;
            font-size: 1.1em; line-height: 2; color: #e4e4f0;
            border-left: 4px solid rgba(251,191,36,0.3);
            margin-bottom: 20px;
        }}
        .script-content p {{ margin-bottom: 12px; padding-left: 20px; border-left: 2px solid rgba(251,191,36,0.1); }}
        .script-content p:last-child {{ margin-bottom: 0; }}
        .script-content::before {{ content: '"'; font-size: 2em; color: #fbbf24; opacity: 0.3; display: block; margin-bottom: 8px; }}
        .script-content::after {{ content: '"'; font-size: 2em; color: #fbbf24; opacity: 0.3; display: block; margin-top: 8px; text-align: right; }}
        .hashtag-display {{ color: #fbbf24; font-size: .95em; }}
        .tip-box {{
            margin-top: 16px; padding: 16px 20px;
            background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.12);
            border-radius: 12px; color: #fbbf24; font-size: .9em; line-height: 1.6;
        }}
        .copy-btn {{
            display: inline-block; margin-top: 16px; padding: 10px 24px;
            background: rgba(251,191,36,0.12); color: #fbbf24;
            border-radius: 8px; font-size: .9em; font-weight: 500; cursor: pointer;
            transition: all .3s ease; border: 1px solid rgba(251,191,36,0.2);
        }}
        .copy-btn:hover {{ background: rgba(251,191,36,0.2); }}
        .article-nav {{ display: flex; justify-content: space-between; margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.06); }}
        .article-nav a {{ color: #fbbf24; text-decoration: none; font-weight: 500; }}
        .article-nav a:hover {{ color: #fcd34d; }}
        @media (max-width:768px) {{ .script-content {{ padding: 20px; font-size: 1em; }} }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back" style="color:#fbbf24;">← Quay về Dashboard</a>
        
        <div class="script-header">
            <div class="script-meta">
                <span class="script-number-badge">{stt}</span>
                <span>🎬 Kịch bản — {weekday}, {day} tháng {month}</span>
            </div>
            <h1 class="script-title">{title}</h1>
        </div>
        
        <div class="script-content">
            {script_paragraphs}
        </div>
        
        <div class="hashtag-display">🎯 {hashtag}</div>
        {tip_html}
        
        <div class="copy-btn" onclick="navigator.clipboard.writeText(document.querySelector('.script-content').innerText.replace(/[\\n]{3,}/g,'\\n\\n'))">📋 Copy lời thoại</div>
        
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


def update_index(item: dict, filename: str):
    items = []
    if SCRIPTS_JSON.exists():
        try: items = json.loads(SCRIPTS_JSON.read_text())
        except: pass
    
    entry = {
        'title': item.get('title', ''),
        'filename': filename,
        'date': item.get('date', ''),
        'stt': item.get('stt', 1),
        'hashtag': item.get('hashtag', ''),
        'preview': item.get('script', '')[:120],
    }
    
    for i, a in enumerate(items):
        if a['title'] == entry['title'] and a['date'] == entry['date']:
            items[i] = entry; break
    else:
        items.append(entry)
    
    SCRIPTS_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"✅ scripts.json: {len(items)} kịch bản")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='JSON object')
    parser.add_argument('--file', help='File JSON')
    parser.add_argument('--output', help='Tên file output')
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, encoding='utf-8') as f: item = json.load(f)
    elif args.data:
        item = json.loads(args.data)
    else:
        print("❌ Cần --data hoặc --file"); sys.exit(1)
    
    title = item.get('title', 'kich-ban')
    slug = slugify(title)
    date_str = item.get('date', datetime.now().strftime('%Y-%m-%d'))
    stt = item.get('stt', 1)
    filename = args.output or f'{date_str}-{slug}.html'
    if not filename.endswith('.html'): filename += '.html'
    
    html = generate_html(item)
    out = SCRIPTS_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {out}")
    
    update_index(item, filename)
    print(f"\n🎬 {title}")


if __name__ == '__main__':
    main()