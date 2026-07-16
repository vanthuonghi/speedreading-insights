#!/usr/bin/env python3
"""
Tạo trang HTML video AI từ dữ liệu JSON
========================================
Cách dùng:
  python3 generate_ai_videos.py --data '[...]'
  python3 generate_ai_videos.py --file ai_videos.json
"""
import json, os, sys, subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / 'speedreading-research'
AI_VIDEOS_DIR = BASE_DIR / 'ai-videos'
AI_VIDEOS_JSON = BASE_DIR / 'ai_videos.json'
AI_VIDEOS_INDEX_JSON = BASE_DIR / 'ai_videos_index.json'


def generate_ai_video_html(items: list, date_str: str = None) -> str:
    """Tạo trang HTML danh sách video AI"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    weekday_map = {'Monday':'Thứ Hai','Tuesday':'Thứ Ba','Wednesday':'Thứ Tư',
                   'Thursday':'Thứ Năm','Friday':'Thứ Sáu','Saturday':'Thứ Bảy','Sunday':'Chủ Nhật'}
    weekday = weekday_map.get(date_obj.strftime('%A'), '')
    
    cards_html = ''
    for i, item in enumerate(items, 1):
        title = item.get('title', '')
        url = item.get('url', '')
        channel = item.get('channel', '')
        duration = item.get('duration', '')
        views = item.get('views', 0)
        date = item.get('date', '')
        summary = item.get('summary', '')
        category = item.get('category', 'AI & Công nghệ')
        
        # Format views
        view_str = ''
        if views:
            if views >= 1000000:
                view_str = f"{views/1000000:.1f}M lượt xem"
            elif views >= 1000:
                view_str = f"{views/1000:.0f}K lượt xem"
            else:
                view_str = f"{views} lượt xem"
        
        meta_parts = []
        if channel:
            meta_parts.append(f'📺 {channel}')
        if duration:
            meta_parts.append(f'⏱ {duration}')
        if view_str:
            meta_parts.append(f'👁 {view_str}')
        if date:
            meta_parts.append(f'📅 {date}')
        meta_str = ' • '.join(meta_parts)
        
        embed = f'https://www.youtube-nocookie.com/embed/{item.get("video_id", "")}' if item.get('video_id') else ''
        
        cards_html += f'''
        <div class="ai-video-card">
            <div class="video-number">{i}</div>
            <div class="video-main">
                <h2><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>
                <div class="video-meta">{meta_str}</div>
                <div class="video-summary">{summary}</div>
                <div class="video-actions">
                    <a href="{url}" target="_blank" class="watch-btn">▶ Xem trên YouTube</a>
                </div>
            </div>
        </div>'''
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Videos {date_str} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .ai-video-card {{
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px; padding: 24px 28px; margin-bottom: 20px;
            display: flex; gap: 18px; align-items: flex-start;
            transition: all .3s ease; position: relative;
        }}
        .ai-video-card::before {{
            content: ''; position: absolute; top: 0; left: 0;
            width: 4px; height: 100%;
            background: linear-gradient(to bottom, #a855f7, #3b82f6);
            border-radius: 0 2px 2px 0;
        }}
        .ai-video-card:hover {{
            border-color: rgba(168,85,247,0.25);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }}
        .video-number {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 40px; height: 40px; min-width: 40px;
            background: rgba(168,85,247,0.15); color: #a855f7;
            border-radius: 12px; font-weight: 700; font-size: 1em;
        }}
        .video-main {{ flex: 1; min-width: 0; }}
        .video-main h2 {{ font-size: 1.05em; font-weight: 600; margin-bottom: 6px; }}
        .video-main h2 a {{ color: #e4e4f0; text-decoration: none; transition: color .2s; }}
        .video-main h2 a:hover {{ color: #a855f7; }}
        .video-meta {{
            font-size: .82em; color: #8b8ba7; margin-bottom: 10px;
            display: flex; flex-wrap: wrap; gap: 4px;
        }}
        .video-summary {{
            color: #c8c8e0; font-size: .92em; line-height: 1.7;
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
        }}
        .video-actions {{ margin-top: 12px; }}
        .watch-btn {{
            display: inline-flex; align-items: center; gap: 6px;
            padding: 8px 20px; background: rgba(168,85,247,0.12);
            color: #a855f7; border-radius: 8px; font-size: .85em; font-weight: 500;
            text-decoration: none; transition: all .2s;
            border: 1px solid rgba(168,85,247,0.2);
        }}
        .watch-btn:hover {{ background: rgba(168,85,247,0.2); text-decoration: none; }}
        
        @media (max-width: 768px) {{
            .ai-video-card {{ padding: 18px 20px; flex-direction: column; }}
            .video-number {{ width: 32px; height: 32px; min-width: 32px; font-size: .85em; }}
        }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back">← Quay về Dashboard</a>
        <div class="report-header">
            <div class="report-date" style="color:#a855f7;">🤖 AI VIDEOS — {weekday}</div>
            <h1 style="background:linear-gradient(135deg,#a855f7,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">AI Tools & Công nghệ mới</h1>
            <p>Ngày {day} tháng {month} • {len(items)} video • Cập nhật từ YouTube</p>
        </div>
        {cards_html}
    </div>
    <footer>
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a></p>
        <p>Hotline: 0899.320.202 | Email: admin@speedreading.vn</p>
    </footer>
</body>
</html>'''


def update_index_json(items: list, date_str: str, filename: str):
    """Cập nhật ai_videos_index.json cho dashboard"""
    index_data = []
    if AI_VIDEOS_INDEX_JSON.exists():
        try:
            index_data = json.loads(AI_VIDEOS_INDEX_JSON.read_text())
        except:
            pass
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    entry = {
        'day': date_obj.strftime('%d'),
        'month': date_obj.strftime('%m/%Y'),
        'date': date_str,
        'title': f'🤖 AI Videos {date_str}',
        'filename': filename,
        'count': len(items),
        'items': [{'title': i.get('title', '')[:80], 'channel': i.get('channel', '')} for i in items]
    }
    
    for i, s in enumerate(index_data):
        if s['date'] == date_str:
            index_data[i] = entry
            break
    else:
        index_data.append(entry)
    
    AI_VIDEOS_INDEX_JSON.write_text(json.dumps(index_data, ensure_ascii=False, indent=2))
    print(f"✅ Đã cập nhật ai_videos_index.json ({len(index_data)} bộ)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tạo trang HTML AI Videos')
    parser.add_argument('--data', help='JSON array video')
    parser.add_argument('--file', help='File JSON chứa dữ liệu')
    parser.add_argument('--date', help='Ngày (VD: 2026-07-16)')
    parser.add_argument('--output', help='Tên file output')
    args = parser.parse_args()
    
    # Lấy dữ liệu
    if args.file:
        with open(args.file) as f:
            items = json.load(f)
    elif args.data:
        items = json.loads(args.data)
    else:
        print("❌ Cần --data hoặc --file")
        sys.exit(1)
    
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    filename = args.output or f'{date_str}-ai-videos.html'
    if not filename.endswith('.html'):
        filename += '.html'
    
    # Lưu raw data
    AI_VIDEOS_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"✅ Đã lưu ai_videos.json ({len(items)} video)")
    
    # Tạo HTML
    html = generate_ai_video_html(items, date_str)
    output_path = AI_VIDEOS_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {output_path}")
    
    # Cập nhật index
    update_index_json(items, date_str, filename)
    
    print(f"\n🤖 {len(items)} video AI ngày {date_str}")


if __name__ == '__main__':
    main()