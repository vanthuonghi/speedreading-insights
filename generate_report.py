#!/usr/bin/env python3
"""
Tạo trang HTML báo cáo nghiên cứu cho Speed Reading Insights
=============================================================
Cách dùng:
  python3 generate_report.py "sáng" "2026-07-16" --data '[
    {"title": "...", "content": "...", "source": "...", "apply": "..."},
    ...
  ]'
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Đường dẫn
BASE_DIR = Path.home() / 'speedreading-research'
REPORTS_DIR = BASE_DIR / 'reports'
INDEX_PATH = BASE_DIR / 'index.html'
REPORTS_JSON = BASE_DIR / 'reports.json'

# Màu sắc cho các tag
TAG_COLORS = {
    'sách': 'green',
    'diễn giả': 'pink',
    'xu hướng': 'amber',
    'nghiên cứu': '',
    'bài học': 'pink',
    'ứng dụng': '',
    'công nghệ': 'amber',
    'khoa học': 'green',
    'não bộ': 'green',
    'học tập': '',
    'speed reading': 'amber',
    'phát triển': 'pink',
    'productivity': 'amber',
    'book': 'green',
    'speaker': 'pink',
    'trend': 'amber',
    'research': 'green',
}


def slugify(text):
    """Tạo filename từ text"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50]


def detect_tag_color(tags):
    """Phát hiện màu tag dựa trên nội dung"""
    for tag in tags:
        tag_lower = tag.lower().strip()
        for key, color in TAG_COLORS.items():
            if key in tag_lower:
                return color
    return ''


def generate_report_html(date_str: str, time_of_day: str, items: list) -> str:
    """
    Tạo trang HTML báo cáo
    
    Args:
        date_str: "2026-07-16"
        time_of_day: "sáng" hoặc "tối"
        items: List dict với các keys: title, content, source, apply, tags
    
    Returns:
        str: Nội dung HTML
    """
    # Parse date
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    weekday_map = {
        'Monday': 'Thứ Hai', 'Tuesday': 'Thứ Ba', 'Wednesday': 'Thứ Tư',
        'Thursday': 'Thứ Năm', 'Friday': 'Thứ Sáu', 'Saturday': 'Thứ Bảy',
        'Sunday': 'Chủ Nhật'
    }
    weekday = weekday_map.get(date_obj.strftime('%A'), '')
    
    time_label = '🌅 Sáng' if time_of_day == 'sáng' else '🌆 Tối'
    emoji = '🌅' if time_of_day == 'sáng' else '🌆'
    
    # Generate research cards
    cards_html = ''
    for i, item in enumerate(items, 1):
        title = item.get('title', 'Chưa có tiêu đề')
        content = item.get('content', '')
        source = item.get('source', '')
        apply = item.get('apply', '')
        tags = item.get('tags', [])
        
        tag_color = detect_tag_color(tags)
        tag_class = f'tag {tag_color}' if tag_color else 'tag'
        
        tags_html = ''.join([f'<span class="{tag_class}">{t}</span>' for t in tags])
        
        apply_html = ''
        if apply:
            apply_html = f'''
            <div class="apply-box">
                <div class="label">💡 Ứng dụng cho Speed Reading</div>
                <p>{apply}</p>
            </div>
            '''
        
        source_html = ''
        if source:
            if source.startswith('http'):
                source_html = f'🔗 <a href="{source}" target="_blank" style="color:#818cf8;">Nguồn</a>'
            else:
                source_html = f'📖 {source}'
        
        cards_html += f'''
        <div class="research-card">
            <div class="number">{i}</div>
            <h2>{title}</h2>
            <div class="content">
                <p>{content}</p>
            </div>
            <div class="meta">
                {tags_html}
                {f'<span class="tag" style="background:rgba(139,139,167,0.1);color:#8b8ba7;">{source_html}</span>' if source_html else ''}
            </div>
            {apply_html}
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo {time_of_day} - {date_str} | Speed Reading Insights</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>

    <div class="container report-page">
        <a href="../index.html" class="back">← Quay về trang chủ</a>
        
        <div class="report-header">
            <div class="report-date">{emoji} {time_label} — {weekday}</div>
            <h1>Báo cáo nghiên cứu {time_of_day}</h1>
            <p>Ngày {day} tháng {month} • {len(items)} thông tin</p>
        </div>

        {cards_html}
    </div>

    <footer>
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a> — Nghiên cứu & Phát triển</p>
        <p>Hotline: 0899.320.202 | Email: admin@speedreading.vn</p>
    </footer>
</body>
</html>'''


def update_index(items: list, date_str: str, time_of_day: str, filename: str):
    """Cập nhật index.html và reports.json"""
    
    # Cập nhật reports.json
    reports = []
    if REPORTS_JSON.exists():
        try:
            reports = json.loads(REPORTS_JSON.read_text())
        except:
            reports = []
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    report_entry = {
        'day': date_obj.strftime('%d'),
        'month': date_obj.strftime('%m/%Y'),
        'date': date_str,
        'time': time_of_day,
        'title': f'Báo cáo {"Sáng" if time_of_day == "sáng" else "Tối"} {date_str}',
        'filename': filename,
        'items': [{'title': i.get('title', '')} for i in items]
    }
    
    # Thay thế nếu đã tồn tại
    for i, r in enumerate(reports):
        if r['date'] == date_str and r['time'] == time_of_day:
            reports[i] = report_entry
            break
    else:
        reports.append(report_entry)
    
    REPORTS_JSON.write_text(json.dumps(reports, ensure_ascii=False, indent=2))
    print(f"✅ Đã cập nhật reports.json ({len(reports)} báo cáo)")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tạo trang HTML báo cáo nghiên cứu')
    parser.add_argument('time_of_day', choices=['sáng', 'tối'], help='Buổi')
    parser.add_argument('date', help='Ngày (VD: 2026-07-16)')
    parser.add_argument('--data', required=True, help='JSON array của các mục nghiên cứu')
    parser.add_argument('--output', help='Tên file output (mặc định: tự động)')
    
    args = parser.parse_args()
    
    items = json.loads(args.data)
    
    # Tạo tên file
    filename = args.output or f'{args.date}-{args.time_of_day}.html'
    if not filename.endswith('.html'):
        filename += '.html'
    
    # Tạo HTML
    html = generate_report_html(args.date, args.time_of_day, items)
    
    # Lưu file
    output_path = REPORTS_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {output_path}")
    
    # Cập nhật index
    update_index(items, args.date, args.time_of_day, filename)
    
    print(f"\n📊 Báo cáo {args.time_of_day} ngày {args.date}")
    print(f"📝 {len(items)} thông tin")
    print(f"🔗 file://{output_path}")


if __name__ == '__main__':
    main()