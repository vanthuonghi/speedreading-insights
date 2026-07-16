#!/usr/bin/env python3
"""
Tạo trang HTML báo cáo nghiên cứu - hỗ trợ đa chủ đề
====================================================
Cách dùng:
  python3 generate_report.py "sáng" "2026-07-16" --data '[
    {"title":"...", "content":"...", "source":"...", "apply":"...", "tags":["sách","speed reading"]},
    ...
  ]'
"""

import json, os, sys, re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / 'speedreading-research'
REPORTS_DIR = BASE_DIR / 'reports'
REPORTS_JSON = BASE_DIR / 'reports.json'

TAG_COLORS = {
    'sách':'green', 'diễn giả':'pink', 'xu hướng':'amber',
    'nghiên cứu':'', 'bài học':'pink', 'khoa học':'green',
    'não bộ':'green', 'học tập':'', 'speed reading':'amber',
    'phát triển':'pink', 'productivity':'amber',
    'ai':'purple', 'công nghệ':'purple', 'tool':'purple',
    'app':'purple', 'công cụ':'purple',
}

CATEGORY_BADGES = {
    'sách': ('📚', '#34d399'),
    'speed reading': ('📚', '#34d399'),
    'ai': ('🤖', '#a855f7'),
    'công nghệ': ('🤖', '#a855f7'),
    'tool': ('🤖', '#a855f7'),
}

def detect_tag_color(tags):
    for tag in tags:
        tl = tag.lower().strip()
        for k, c in TAG_COLORS.items():
            if k in tl:
                return c
    return ''

def get_category(tags):
    """Xác định category: 'reading' hoặc 'ai'"""
    tl = ' '.join(tags).lower()
    if any(k in tl for k in ['ai','công nghệ','tool','app','công cụ','technology']):
        return 'ai'
    return 'reading'

def make_report_html(date_str: str, time_of_day: str, items: list) -> str:
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day = date_obj.strftime('%d')
    month = date_obj.strftime('%m/%Y')
    wd = ['Thứ Hai','Thứ Ba','Thứ Tư','Thứ Năm','Thứ Sáu','Thứ Bảy','Chủ Nhật'][date_obj.weekday()]
    emoji = '🌅' if time_of_day == 'sáng' else '🌆'
    time_label = 'Sáng' if time_of_day == 'sáng' else 'Tối'

    # Đếm số lượng mỗi category
    reading_count = sum(1 for i in items if get_category(i.get('tags',[])) == 'reading')
    ai_count = sum(1 for i in items if get_category(i.get('tags',[])) == 'ai')

    cards_html = ''
    for idx, item in enumerate(items, 1):
        title = item.get('title','')
        content = item.get('content','')
        source = item.get('source','')
        apply = item.get('apply','')
        tags = item.get('tags',[])
        cat = get_category(tags)
        badge_emoji, badge_color = CATEGORY_BADGES.get(cat, ('📌','#818cf8'))
        tag_color = detect_tag_color(tags)
        tag_cls = f'tag {tag_color}' if tag_color else 'tag'
        tags_html = ''.join([f'<span class="{tag_cls}">{t}</span>' for t in tags])

        # Badge category
        cat_badge = f'<span class="cat-badge" style="background:{badge_color}15;color:{badge_color};border-color:{badge_color}30;">{badge_emoji} {"Sách & Đọc" if cat=="reading" else "AI & Công nghệ"}</span>'

        apply_html = ''
        if apply:
            apply_html = f'''
            <div class="apply-box">
                <div class="label">💡 Ứng dụng cho Speed Reading</div>
                <p>{apply}</p>
            </div>'''

        src_html = ''
        if source:
            if source.startswith('http'):
                src_html = f'🔗 <a href="{source}" target="_blank" style="color:#818cf8;">Nguồn</a>'
            else:
                src_html = f'📖 {source}'

        cards_html += f'''
        <div class="research-card cat-{cat}">
            <div class="number">{idx}</div>
            {cat_badge}
            <h2>{title}</h2>
            <div class="content">{"".join(f'<p>{p}</p>' for p in content.split(chr(10)+chr(10)) if p.strip())}</div>
            <div class="meta">
                {tags_html}
                {f'<span class="tag" style="background:rgba(139,139,167,0.1);color:#8b8ba7;">{src_html}</span>' if src_html else ''}
            </div>
            {apply_html}
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo {time_label} {date_str} | Speed Reading Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .cat-badge { display:inline-block; padding:4px 14px; border-radius:8px; font-size:.8em; font-weight:600; margin-bottom:10px; border:1px solid; margin-left:8px; }
        .research-card.cat-ai::before { background:linear-gradient(to bottom,#a855f7,#6366f1) !important; }
        .tag.purple { background:rgba(168,85,247,0.1) !important; color:#a855f7 !important; }
        .research-card .content p {{ margin-bottom: 12px; line-height: 1.8; }}
        .research-card .content p:last-child {{ margin-bottom: 0; }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="g1"></div><div class="g2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back">← Quay về Dashboard</a>
        <div class="report-header">
            <div class="report-date">{emoji} {time_label} — {wd}</div>
            <h1>Báo cáo nghiên cứu {time_label.lower()}</h1>
            <p>Ngày {day} tháng {month} • 📚 {reading_count} Sách & Đọc • 🤖 {ai_count} AI & Công nghệ</p>
        </div>
        {cards_html}
    </div>
    <footer>
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a></p>
        <p>Hotline: 0899.320.202 | Email: admin@speedreading.vn</p>
    </footer>
</body>
</html>'''


def update_index(items, date_str, time_of_day, filename):
    reports = []
    if REPORTS_JSON.exists():
        try: reports = json.loads(REPORTS_JSON.read_text())
        except: pass

    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    reading_count = sum(1 for i in items if get_category(i.get('tags',[])) == 'reading')
    ai_count = sum(1 for i in items if get_category(i.get('tags',[])) == 'ai')

    entry = {
        'day': date_obj.strftime('%d'),
        'month': date_obj.strftime('%m/%Y'),
        'date': date_str,
        'time': time_of_day,
        'title': f'Báo cáo {time_of_day.title()} {date_str}',
        'filename': filename,
        'reading': reading_count,
        'ai': ai_count,
        'items': [{'title':i.get('title',''),'cat':get_category(i.get('tags',[]))} for i in items]
    }

    for i, r in enumerate(reports):
        if r['date'] == date_str and r['time'] == time_of_day:
            reports[i] = entry; break
    else:
        reports.append(entry)

    REPORTS_JSON.write_text(json.dumps(reports, ensure_ascii=False, indent=2))
    print(f"✅ reports.json: {len(reports)} báo cáo (📚{reading_count} 🤖{ai_count})")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('time_of_day', choices=['sáng','tối'])
    parser.add_argument('date', help='Ngày (VD: 2026-07-16)')
    parser.add_argument('--data', required=True, help='JSON array')
    parser.add_argument('--output')
    args = parser.parse_args()

    items = json.loads(args.data)
    filename = args.output or f'{args.date}-{args.time_of_day}.html'
    if not filename.endswith('.html'): filename += '.html'

    html = make_report_html(args.date, args.time_of_day, items)
    out = REPORTS_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)  # FIX: use exist_ok
    out.write_text(html, encoding='utf-8')
    print(f"✅ Đã tạo: {out}")

    update_index(items, args.date, args.time_of_day, filename)
    reading = sum(1 for i in items if get_category(i.get('tags',[])) == 'reading')
    ai = sum(1 for i in items if get_category(i.get('tags',[])) == 'ai')
    print(f"\n📊 📚{reading} Sách • 🤖{ai} AI & Công nghệ")


if __name__ == '__main__':
    main()