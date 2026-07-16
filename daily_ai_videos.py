#!/usr/bin/env python3
"""
Pipeline AI Videos: Fetch → Dịch tiếng Việt → Gen individual pages → Deploy
=====================================================================
Cách dùng:  python3 daily_ai_videos.py
"""
import json, subprocess, sys, os
from pathlib import Path
from datetime import datetime

BASE = Path.home() / 'speedreading-research'

def run_cmd(cmd, capture=True):
    r = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=capture, text=True, timeout=120)
    if r.returncode != 0 and r.stderr.strip():
        print(f"⚠️ {r.stderr.strip()[:200]}")
    return r.stdout.strip() if capture else r.returncode

def translate_to_vietnamese(text, title):
    """Dùng OpenRouter để dịch summary sang tiếng Việt"""
    try:
        # Đọc config
        env_path = Path.home() / '.hermes' / '.env'
        api_key = ''
        if env_path.exists():
            for line in env_path.read_text().split('\n'):
                if line.startswith('OPENROUTER_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
        
        if not api_key:
            return text[:300]  # fallback
        
        prompt = f"""Bạn là chuyên gia dịch thuật. Dịch đoạn mô tả video YouTube sau sang tiếng Việt tự nhiên, dễ hiểu.

Tiêu đề video: {title}
Mô tả gốc (tiếng Anh): {text}

Yêu cầu:
- Dịch sang tiếng Việt tự nhiên, giọng văn gần gũi
- Giữ nguyên tên công cụ, tên sản phẩm, số liệu
- Tóm tắt ngắn gọn nội dung chính (2-3 câu)
- KHÔNG thêm bình luận cá nhân
- KHÔNG thêm link"""

        import requests
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "Bạn là dịch giả chuyên nghiệp, dịch từ tiếng Anh sang tiếng Việt. Chỉ trả về bản dịch, không thêm gì khác."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            translated = resp.json()['choices'][0]['message']['content'].strip()
            # Loại bỏ quote nếu có
            translated = translated.strip('"\'')
            return translated
    except Exception as e:
        print(f"   ⚠️ Lỗi dịch: {e}")
    
    return text[:300]  # fallback


def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 AI Videos Daily — {date_str}")
    
    # Step 1: Fetch
    print("📡 Đang tìm video AI mới nhất...")
    raw = run_cmd("python3 fetch_ai_videos.py")
    try:
        data = json.loads(raw)
    except:
        print("❌ Lỗi parse JSON từ fetch")
        sys.exit(1)
    
    print(f"   ✅ {len(data)} video")
    
    # Step 2: Translate summaries to Vietnamese + gen individual pages
    print("🌐 Đang dịch summaries sang tiếng Việt...")
    for i, video in enumerate(data):
        video['fetch_date'] = date_str
        # Dịch summary
        eng_summary = video.get('summary', '')
        if eng_summary:
            vi_summary = translate_to_vietnamese(eng_summary, video.get('title', ''))
            video['summary_vi'] = vi_summary
            print(f"   {i+1}. ✅ {video.get('title', '')[:50]}...")
        else:
            video['summary_vi'] = 'Không có mô tả.'
            print(f"   {i+1}. ⚠️ {video.get('title', '')[:50]}... (không có summary)")
        
        # Ghi từng video ra file tạm
        tmp = Path('/tmp/_ai_video_item.json')
        tmp.write_text(json.dumps(video, ensure_ascii=False), encoding='utf-8')
        
        # Gen individual page
        r = subprocess.run(
            [sys.executable, str(BASE/'generate_ai_video_item.py'), '--file', '/tmp/_ai_video_item.json'],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            print(f"      ⚠️ Lỗi gen: {r.stderr[:100]}")
    
    # Step 3: Deploy
    print("\n🚀 Deploy...")
    run_cmd("python3 update_website.py")
    
    # Step 4: Top 3
    print(f"\n📊 Top 3 video nổi bật hôm nay:")
    for i, v in enumerate(data[:3], 1):
        print(f"   {i}. {v['title']}")
        print(f"      📺 {v['channel']}  {'⏱ ' + v['duration'] if v.get('duration') else ''}")
        print(f"      🔗 {v['url']}")
    
    print(f"\n🔗 https://vanthuonghi.github.io/speedreading-insights/")

if __name__ == '__main__':
    main()