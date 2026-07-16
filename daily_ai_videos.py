#!/usr/bin/env python3
"""
Pipeline hoàn chỉnh: Fetch AI videos → Generate HTML → Deploy
===============================================================
Cách dùng:  python3 daily_ai_videos.py
"""
import json, subprocess, sys, os
from pathlib import Path
from datetime import datetime

BASE = Path.home() / 'speedreading-research'

def run(cmd, capture=True):
    r = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=capture, text=True, timeout=120)
    if r.returncode != 0 and r.stderr.strip():
        print(f"⚠️ {r.stderr.strip()[:200]}")
    return r.stdout.strip() if capture else r.returncode

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 AI Videos Daily — {date_str}")
    
    # Step 1: Fetch
    print("📡 Đang tìm video AI mới nhất...")
    raw = run("python3 fetch_ai_videos.py")
    try:
        data = json.loads(raw)
    except:
        print("❌ Lỗi parse JSON từ fetch")
        sys.exit(1)
    
    print(f"   ✅ {len(data)} video")
    
    # Step 2: Save raw data
    (BASE / 'ai_videos_raw.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    # Step 3: Generate HTML
    print("📄 Đang tạo HTML...")
    run(f'python3 generate_ai_videos.py --file ai_videos_raw.json --date {date_str}')
    
    # Step 4: Deploy
    print("🚀 Deploy...")
    run("python3 update_website.py")
    
    # Step 5: In ra 3 video nổi bật
    print(f"\n📊 Top 3 video nổi bật hôm nay:")
    for i, v in enumerate(data[:3], 1):
        print(f"   {i}. {v['title']}")
        print(f"      📺 {v['channel']}  {'⏱ ' + v['duration'] if v.get('duration') else ''}")
        print(f"      🔗 {v['url']}")
    
    print(f"\n🔗 https://vanthuonghi.github.io/speedreading-insights/")

if __name__ == '__main__':
    main()