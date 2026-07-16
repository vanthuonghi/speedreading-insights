#!/usr/bin/env python3
"""Chuyển scripts cũ và AI videos cũ sang individual pages"""
import json, subprocess, sys
from pathlib import Path

BASE = Path.home() / 'speedreading-research'
PYTHON = sys.executable

# ===== 1. Convert old scripts (2026-07-15) =====
scripts = [
    {
        "title": "🎬 Mẹo đọc: Chỉ tay dẫn đường",
        "script": "Các bạn có bao giờ đọc sách mà mắt cứ nhảy lung tung, đọc xong chẳng nhớ gì không?\n\nMình cũng từng vậy đó. Rồi mình khám phá ra kỹ thuật siêu đơn giản: dùng ngón tay dẫn đường.\n\nChỉ cần đặt ngón tay dưới dòng chữ và di chuyển đều, mắt sẽ tự động tập trung theo. Vừa nhanh hơn 30%, vừa nhớ lâu hơn.\n\nThử xem, chỉ mất 2 phút tập làm quen thôi. Bạn nào muốn đọc sách hiệu quả hơn, thử ngay nhé!",
        "hashtag": "#SpeedReading #ĐọcNhanh #KỹThuậtĐọc #MẹoHọcTập",
        "tip": "Quay góc nghiêng 45 độ, ánh sáng tự nhiên. Dùng tay minh họa kỹ thuật chỉ tay trên cuốn sách thật.",
        "date": "2026-07-15",
        "stt": 1
    },
    {
        "title": "🎬 Tâm sự: Đọc sách để làm gì?",
        "script": "Nhiều bạn hỏi mình: Đọc sách để làm gì giữa cuộc sống bận rộn này?\n\nMình chỉ muốn nói: Sách không chỉ là kiến thức, mà là cách bạn dừng lại giữa dòng đời xô bồ. Mỗi cuốn sách là một cuộc trò chuyện với tác giả, một tấm gương soi vào tâm hồn mình.\n\nHồi xưa mình cũng lười đọc, nhưng từ khi bắt đầu, mình thấy mỗi ngày đều nhẹ nhàng hơn. Hãy dành 10 phút mỗi tối, bạn sẽ thấy khác.\n\nCùng nhau đọc sách nhé!",
        "hashtag": "#ĐọcSách #CảmHứng #PhátTriểnBảnThân #TâmSự",
        "tip": "Quay mặt thẳng, ánh sáng mềm, giọng chậm rãi và ấm áp. Có thể thêm nhạc nền nhẹ.",
        "date": "2026-07-15",
        "stt": 2
    },
    {
        "title": "🎬 Giới thiệu Speed Reading",
        "script": "Bạn có muốn đọc một cuốn sách dày 300 trang chỉ trong 2 giờ?\n\nMình từng nghĩ đó là chuyện viển vông, cho đến khi học Speed Reading. Giờ mình đọc nhanh gấp 3 lần, nhớ được ý chính, và không còn sợ sách dày nữa.\n\nMình mở khóa học Zoom 980k, chỉ 2 buổi online, hướng dẫn chi tiết từ A-Z. Còn nếu bạn muốn thử trước, có webinar miễn phí vào cuối tuần.\n\nĐăng ký ngay trong bio để nhận link nhé, mình chờ bạn!",
        "hashtag": "#SpeedReading #KhóaHọc #ĐọcNhanh #KỹNăngMềm",
        "tip": "Quay gần, giọng hào hứng, có thể thêm hiệu ứng chữ xuất hiện trên màn hình khi kể về kết quả.",
        "date": "2026-07-15",
        "stt": 3
    }
]

print("🔄 Đang chuyển scripts cũ sang individual pages...")
for s in scripts:
    tmp = Path('/tmp/_script_item.json')
    tmp.write_text(json.dumps(s, ensure_ascii=False), encoding='utf-8')
    r = subprocess.run(
        [PYTHON, str(BASE/'generate_script_item.py'), '--file', str(tmp)],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode == 0:
        print(f"   ✅ {s['title'][:50]}")
    else:
        print(f"   ❌ {s['title'][:50]}: {r.stderr[:100]}")

# ===== 2. Convert old AI videos (2026-07-16) to individual pages =====
print("\n🔄 Đang chuyển AI videos cũ sang individual pages...")

# Read the old ai_videos.json
old_videos = json.loads((BASE / 'ai_videos.json').read_text(encoding='utf-8'))
for v in old_videos:
    v['fetch_date'] = '2026-07-16'
    v['summary_vi'] = v.get('summary', '')[:200]  # Keep original summary for now
    # Add video_id if missing (extract from URL)
    if not v.get('video_id') and v.get('url'):
        vid = v['url'].split('v=')[-1] if 'v=' in v['url'] else ''
        v['video_id'] = vid.split('&')[0] if '&' in vid else vid
    
    tmp = Path('/tmp/_ai_video_item.json')
    tmp.write_text(json.dumps(v, ensure_ascii=False), encoding='utf-8')
    r = subprocess.run(
        [PYTHON, str(BASE/'generate_ai_video_item.py'), '--file', str(tmp)],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode == 0:
        print(f"   ✅ {v['title'][:50]}")
    else:
        print(f"   ❌ {v['title'][:50]}: {r.stderr[:100]}")

# ===== 3. Clean up old batch files =====
print("\n🧹 Dọn dẹp...")
(old_batch := BASE / 'ai_videos.json').unlink(missing_ok=True)
(old_batch := BASE / 'ai_videos_raw.json').unlink(missing_ok=True)
(old_batch := BASE / 'ai_videos_index.json').unlink(missing_ok=True)
(old_batch := BASE / 'scripts.json').unlink(missing_ok=True)

print("\n🎉 Hoàn tất! Đã chuyển tất cả sang individual pages.")