#!/usr/bin/env python3
"""
Tạo trang HTML video AI độc lập
================================
Mỗi video AI = 1 trang HTML riêng, mô tả bằng tiếng Việt.

Cách dùng:
  python3 generate_ai_video_item.py --file /tmp/video.json
  python3 generate_ai_video_item.py --data '{...}'
"""
import json, re, sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / 'speedreading-research'
AI_VIDEOS_DIR = BASE_DIR / 'ai-videos-items'  # individual video pages
AI_VIDEOS_INDEX_JSON = BASE_DIR / 'ai_videos_index.json'

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
    if len(words) > 10: words = words[:10]
    return '-'.join(words)


def generate_html(item: dict) -> str:
    title = item.get('title', 'Video AI')
    url = item.get('url', '')
    video_id = item.get('video_id', '')
    channel = item.get('channel', '')
    duration = item.get('duration', '')
    views = item.get('views', 0)
    date_published = item.get('date', '')
    summary_vi = item.get('summary_vi', item.get('summary', ''))
    date_str = item.get('fetch_date', datetime.now().strftime('%Y-%m-%d'))
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    weekday_map = {'Monday':'Thứ Hai','Tuesday':'Thứ Ba','Wednesday':'Thứ Tư',
                   'Thursday':'Thứ Năm','Friday':'Thứ Sáu','Saturday':'Thứ Bảy','Sunday':'Chủ Nhật'}
    weekday = weekday_map.get(date_obj.strftime('%A'), '')
    
    # Views
    view_str = ''
    if views:
        if views >= 1000000: view_str = f"{views/1000000:.1f}M lượt xem"
        elif views >= 1000: view_str = f"{views/1000:.0f}K lượt xem"
        else: view_str = f"{views} lượt xem"
    
    meta_parts = [f'📺 {channel}'] if channel else []
    if duration: meta_parts.append(f'⏱ {duration}')
    if view_str: meta_parts.append(f'👁 {view_str}')
    if date_published: meta_parts.append(f'📅 {date_published}')
    meta_str = ' • '.join(meta_parts)
    
    embed_url = f'https://www.youtube-nocookie.com/embed/{video_id}' if video_id else ''
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .video-header {{ margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
        .video-meta {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; font-size: .85em; color: #8b8ba7; }}
        .video-title {{ font-size: clamp(1.3em,3vw,1.8em); font-weight: 700; line-height: 1.4; margin-bottom: 8px; }}
        .video-meta-row {{ color: #a0a0b8; font-size: .9em; display: flex; gap: 16px; flex-wrap: wrap; }}
        .video-embed {{ position: relative; width: 100%; border-radius: 16px; overflow: hidden; margin-bottom: 24px; }}
        .video-embed iframe {{ width: 100%; aspect-ratio: 16/9; border: none; }}
        .video-summary {{
            font-size: 1.05em; line-height: 1.9; color: #e0e0f0;
            background: rgba(168,85,247,0.04); border-radius: 16px; padding: 24px;
            border: 1px solid rgba(168,85,247,0.08);
        }}
        .video-summary p {{ margin-bottom: 14px; }}
        .video-summary p:last-child {{ margin-bottom: 0; }}
        .video-actions {{ margin-top: 20px; }}
        .watch-btn {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 12px 28px; background: rgba(168,85,247,0.12);
            color: #a855f7; border-radius: 10px; font-size: .95em; font-weight: 600;
            text-decoration: none; transition: all .2s;
            border: 1px solid rgba(168,85,247,0.2);
        }}
        .watch-btn:hover {{ background: rgba(168,85,247,0.2); text-decoration: none; }}
        .article-nav {{ display: flex; justify-content: space-between; margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.06); }}
        .article-nav a {{ color: #a855f7; text-decoration: none; font-weight: 500; }}
        .article-nav a:hover {{ color: #c084fc; }}
        @media (max-width:768px) {{ .video-summary {{ padding: 18px; font-size: 1em; }} }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back" style="color:#a855f7;">← Quay về Dashboard</a>
        
        <div class="video-header">
            <div class="video-meta">
                <span style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;background:rgba(168,85,247,0.12);color:#a855f7;font-size:.8em;font-weight:600;">
                    🤖 AI Video
                </span>
                <span>{weekday}, {day} tháng {month}</span>
            </div>
            <h1 class="video-title">{title}</h1>
            <div class="video-meta-row">{meta_str}</div>
        </div>
        
        {f'<div class="video-embed"><iframe src="{embed_url}" allowfullscreen loading="lazy"></iframe></div>' if embed_url else ''}
        
        <div class="video-summary">
            <p>{summary_vi}</p>
        </div>
        
        <div class="video-actions">
            <a href="{url}" target="_blank" class="watch-btn">▶ Xem trên YouTube</a>
        </div>
        
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
    if AI_VIDEOS_INDEX_JSON.exists():
        try: items = json.loads(AI_VIDEOS_INDEX_JSON.read_text())
        except: pass
    
    entry = {
        'title': item.get('title', ''),
        'filename': filename,
        'date': item.get('fetch_date', ''),
        'channel': item.get('channel', ''),
        'duration': item.get('duration', ''),
        'preview': item.get('summary_vi', item.get('summary', ''))[:120],
    }
    
    for i, a in enumerate(items):
        if a['title'] == entry['title']:
            items[i] = entry; break
    else:
        items.append(entry)
    
    AI_VIDEOS_INDEX_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"✅ ai_videos_index.json: {len(items)} video")


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
    
    title = item.get('title', 'ai-video')
    slug = slugify(title)
    date_str = item.get('fetch_date', datetime.now().strftime('%Y-%m-%d'))
    filename = args.output or f'{date_str}-{slug}.html'
    if not filename.endswith('.html'): filename += '.html'
    
    html = generate_html(item)
    out = AI_VIDEOS_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {out}")
    
    update_index(item, filename)
    print(f"\n🤖 {title}")


if __name__ == '__main__':
    main()