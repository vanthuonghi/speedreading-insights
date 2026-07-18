#!/usr/bin/env python3
"""Tạo trang quảng cáo riêng cho từng biến thể"""
import json, os
from pathlib import Path
from datetime import datetime

BASE = Path.home() / 'speedreading-research'
ADS_DIR = BASE / 'ads-items'
ADS_INDEX = BASE / 'ads_index.json'

def load_ads():
    with open(ADS_INDEX) as f:
        return json.load(f)

def generate_ad_page(ad):
    """Tạo 1 trang HTML riêng cho quảng cáo"""
    slug = ad['title'].lower()
    slug = slug.replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c in '-')
    slug = slug[:60]
    filename = f"{ad['date']}-{slug}.html"
    
    # Màu sắc theo type
    type_colors = {
        'sp_ad': ('#f59e0b', 'rgba(245,158,11,0.15)', '📢 Bài viết + Ảnh'),
        'sp_video_script': ('#ef4444', 'rgba(239,68,68,0.15)', '🎬 Kịch bản Video'),
        'sp_hook': ('#8b5cf6', 'rgba(139,92,246,0.15)', '💬 Bài viết Cảm xúc')
    }
    color, bg, type_label = type_colors.get(ad['type'], ('#818cf8', 'rgba(99,102,241,0.15)', '📢 Quảng cáo'))
    
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ad['title']} | Speed Reading Insights</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📢</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',sans-serif;background:#0a0a1a;color:#e4e4f0;line-height:1.7}}
        .bg-grid{{position:fixed;top:0;left:0;right:0;bottom:0;
            background-image:linear-gradient(rgba(99,102,241,0.03)1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03)1px,transparent 1px);
            background-size:60px 60px;z-index:-1}}
        .container{{max-width:800px;margin:0 auto;padding:0 20px}}
        .page{{padding:40px 0 80px}}
        .back{{display:inline-flex;align-items:center;gap:8px;color:#8b8ba7;text-decoration:none;font-size:.95em;margin-bottom:24px;transition:color .3s}}
        .back:hover{{color:#818cf8}}
        .header{{padding:30px 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:32px}}
        .header .type-badge{{display:inline-flex;align-items:center;gap:6px;padding:6px 16px;border-radius:10px;font-size:.82em;font-weight:600;margin-bottom:12px}}
        .header h1{{font-size:clamp(1.3em,3vw,1.8em);font-weight:800;line-height:1.3;
            background:linear-gradient(135deg,{color},#c084fc);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
        .header .meta{{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;color:#6b6b8a;font-size:.85em}}
        .header .meta span{{display:inline-flex;align-items:center;gap:4px}}
        .content{{padding:20px 0;white-space:pre-wrap;font-size:1.05em;line-height:1.8;color:#d0d0e8}}
        .content .section-title{{font-size:1.1em;font-weight:700;color:{color};margin:24px 0 12px;display:block}}
        .content .highlight{{background:rgba(255,255,255,0.03);border-left:3px solid {color};padding:12px 16px;margin:12px 0;border-radius:0 8px 8px 0;color:#c8c8e0}}
        .footer{{margin-top:40px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;color:#5a5a7a;font-size:.82em}}
        @media(max-width:768px){{.container{{padding:0 16px}}}}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="container page">
        <a href="../index.html" class="back">← Quay về Dashboard</a>
        <a href="javascript:void(0)" onclick="history.back()" class="back" style="margin-left:16px;">← Quay lại Quảng cáo</a>
        
        <div class="header">
            <div class="type-badge" style="background:{bg};color:{color};">{type_label}</div>
            <h1>{ad['title']}</h1>
            <div class="meta">
                <span>📅 {ad['date']}</span>
                <span>🎯 {ad['target_course']}</span>
                <span>📄 {ad['content_type']}</span>
                <span style="color:{'#34d399' if ad.get('status') == 'active' else '#6b6b8a'};">{'✅ Đang chạy' if ad.get('status') == 'active' else '⏸️ Tạm dừng'}</span>
            </div>
        </div>
        
        <div class="content">
            <span class="section-title">📝 Nội dung quảng cáo</span>
            {ad.get('content', ad['preview'])}
        </div>
        
        <div class="footer">
            <p>© 2026 <a href="https://speedreading.vn" style="color:#818cf8;text-decoration:none;">Speed Reading Việt Nam</a> — Hotline: 0899.320.202</p>
        </div>
    </div>
</body>
</html>"""
    return filename, html

def main():
    ads = load_ads()
    ADS_DIR.mkdir(parents=True, exist_ok=True)
    
    entries = []
    for ad in ads:
        filename, html = generate_ad_page(ad)
        path = ADS_DIR / filename
        path.write_text(html)
        print(f"✅ {filename}")
        entries.append({
            "title": ad['title'],
            "filename": filename,
            "date": ad['date'],
            "type": ad['type'],
            "subtype": ad['subtype'],
            "preview": ad.get('content', ad['preview'])[:200],
            "content_type": ad['content_type'],
            "target_course": ad['target_course'],
            "status": ad['status']
        })
    
    # Ghi index
    index_path = BASE / 'ads_items_index.json'
    index_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2))
    print(f"\n📦 Tổng: {len(entries)} trang quảng cáo")
    print(f"📄 Index: ads_items_index.json")

if __name__ == '__main__':
    main()