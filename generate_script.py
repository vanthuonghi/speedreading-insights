#!/usr/bin/env python3
"""
Tạo trang HTML kịch bản video cho Speed Reading Insights
=========================================================
Cách dùng:
  python3 generate_script.py "2026-07-16" --data '[
    {"title": "...", "script": "...", "hashtag": "...", "tip": "..."},
    ...
  ]'
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / 'speedreading-research'
SCRIPTS_DIR = BASE_DIR / 'scripts'
SCRIPTS_JSON = BASE_DIR / 'scripts.json'

def generate_script_html(date_str: str, items: list) -> str:
    """Tạo trang HTML kịch bản video"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    weekday_map = {'Monday':'Thứ Hai','Tuesday':'Thứ Ba','Wednesday':'Thứ Tư',
                   'Thursday':'Thứ Năm','Friday':'Thứ Sáu','Saturday':'Thứ Bảy','Sunday':'Chủ Nhật'}
    weekday = weekday_map.get(date_obj.strftime('%A'), '')
    
    cards_html = ''
    for i, item in enumerate(items, 1):
        title = item.get('title', '')
        script = item.get('script', '')
        hashtag = item.get('hashtag', '')
        tip = item.get('tip', '')
        
        tip_html = f'<div class="tip-box">💡 <strong>Mẹo quay:</strong> {tip}</div>' if tip else ''
        
        cards_html += f'''
        <div class="script-card">
            <div class="script-number">{i}</div>
            <h2>{title}</h2>
            <div class="script-text">{script}</div>
            <div class="script-meta">
                <span class="tag amber">🎯 Hashtag</span>
                <span style="color:#fbbf24;font-size:0.9em;">{hashtag}</span>
            </div>
            {tip_html}
            <div class="copy-btn" onclick="navigator.clipboard.writeText(this.parentElement.querySelector('.script-text').innerText.replace(/<br>/g,'\\n').replace(/<[^>]*>/g,''))">📋 Copy lời thoại</div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kịch bản Video {date_str} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .script-card {{
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px; padding: 28px; margin-bottom: 24px;
            transition: all .3s ease; position: relative;
        }}
        .script-card::before {{
            content: ''; position: absolute; top: 0; left: 0;
            width: 4px; height: 100%;
            background: linear-gradient(to bottom, #fbbf24, #f472b6);
            border-radius: 0 2px 2px 0;
        }}
        .script-card:hover {{
            border-color: rgba(251,191,36,0.25);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }}
        .script-number {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 36px; height: 36px;
            background: rgba(251,191,36,0.15); color: #fbbf24;
            border-radius: 10px; font-weight: 700; font-size: 0.9em; margin-bottom: 12px;
        }}
        .script-card h2 {{ font-size: 1.15em; font-weight: 600; color: #fbbf24; margin-bottom: 14px; }}
        .script-text {{
            background: rgba(0,0,0,0.2); border-radius: 12px; padding: 20px;
            font-size: 1em; line-height: 1.9; color: #e4e4f0;
            border-left: 3px solid rgba(251,191,36,0.3);
            font-style: italic;
        }}
        .script-text::before {{ content: '"'; font-size: 1.5em; color: #fbbf24; opacity: 0.5; margin-right: 4px; }}
        .script-text::after {{ content: '"'; font-size: 1.5em; color: #fbbf24; opacity: 0.5; margin-left: 4px; }}
        .script-meta {{ display: flex; gap: 12px; align-items: center; margin-top: 16px; flex-wrap: wrap; }}
        .tip-box {{
            margin-top: 14px; padding: 14px 18px;
            background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.12);
            border-radius: 12px; color: #fbbf24; font-size: 0.9em; line-height: 1.6;
        }}
        .copy-btn {{
            display: inline-block; margin-top: 14px; padding: 8px 20px;
            background: rgba(251,191,36,0.12); color: #fbbf24;
            border-radius: 8px; font-size: 0.85em; font-weight: 500; cursor: pointer;
            transition: all .3s ease; border: 1px solid rgba(251,191,36,0.2);
        }}
        .copy-btn:hover {{ background: rgba(251,191,36,0.2); }}
        .tag.amber {{ background: rgba(251,191,36,0.1); color: #fbbf24; }}
        @media (max-width:768px) {{ .script-card {{ padding: 20px; }} .script-text {{ padding: 16px; }} }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back">← Quay về Dashboard</a>
        <div class="report-header">
            <div class="report-date" style="color:#fbbf24;">🎬 KỊCH BẢN VIDEO — {weekday}</div>
            <h1 style="background:linear-gradient(135deg,#fbbf24,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Kịch bản ngày {day} tháng {month}</h1>
            <p>{len(items)} kịch bản • Mỗi kịch bản 20-40 giây</p>
        </div>
        {cards_html}
    </div>
    <footer>
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a></p>
        <p>Hotline: 0899.320.202 | Email: admin@speedreading.vn</p>
    </footer>
</body>
</html>'''


def update_scripts_json(items: list, date_str: str, filename: str):
    """Cập nhật scripts.json"""
    scripts = []
    if SCRIPTS_JSON.exists():
        try:
            scripts = json.loads(SCRIPTS_JSON.read_text())
        except:
            scripts = []
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    entry = {
        'day': date_obj.strftime('%d'),
        'month': date_obj.strftime('%m/%Y'),
        'date': date_str,
        'title': f'🎬 Kịch bản Video {date_str}',
        'filename': filename,
        'items': [{'title': i.get('title', '')} for i in items]
    }
    
    for i, s in enumerate(scripts):
        if s['date'] == date_str:
            scripts[i] = entry
            break
    else:
        scripts.append(entry)
    
    SCRIPTS_JSON.write_text(json.dumps(scripts, ensure_ascii=False, indent=2))
    print(f"✅ Đã cập nhật scripts.json ({len(scripts)} bộ kịch bản)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tạo trang HTML kịch bản video')
    parser.add_argument('date', help='Ngày (VD: 2026-07-16)')
    parser.add_argument('--data', required=True, help='JSON array các kịch bản')
    parser.add_argument('--output', help='Tên file output')
    args = parser.parse_args()
    
    items = json.loads(args.data)
    filename = args.output or f'{args.date}-scripts.html'
    if not filename.endswith('.html'):
        filename += '.html'
    
    html = generate_script_html(args.date, items)
    
    output_path = SCRIPTS_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {output_path}")
    
    update_scripts_json(items, args.date, filename)
    
    print(f"\n🎬 {len(items)} kịch bản video ngày {args.date}")
    print(f"🔗 file://{output_path}")


if __name__ == '__main__':
    main()