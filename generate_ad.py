#!/usr/bin/env python3
"""
Tạo nội dung quảng cáo đa dạng cho khoá học Speed Reading Online
===============================================================
Mỗi ngày 3 nội dung: 3 bài viết + 3 hình ảnh + 3 kịch bản video
Mỗi bài có góc tiếp cận khác nhau để test hiệu quả.

Cách dùng:
  python3 generate_ad.py                   # Tạo 3 nội dung
  python3 generate_ad.py --count 5         # Tạo 5 nội dung
  python3 generate_ad.py --dry-run         # Chỉ xem trước, không lưu
"""
import json, requests, re, sys, os, random
from pathlib import Path
from datetime import datetime

BASE = Path.home() / 'speedreading-research'
ADS_DIR = BASE / 'ads'
ADS_JSON = BASE / 'ads_index.json'

# === THÔNG TIN KHOÁ HỌC (từ sp-online.speedreading.vn) ===
COURSE = {
    "name": "Speed Reading Online - 7 Buổi Zoom",
    "url": "https://speedreading.vn/sp-online",
    "price": "980.000đ",
    "original_price": "4.000.000đ",
    "format": "7 buổi Zoom thực chiến (60-90 phút/buổi tối)",
    "bonus": "Kèm cặp Zalo 1:1 + Hoàn phí nếu không hài lòng buổi 1 + Bộ tài liệu & Ebook độc quyền",
    "result": "Từ 300 → 1000 từ/phút chỉ sau 7 buổi",
    "target": "Học sinh, sinh viên, người đi làm bận rộn, phụ huynh",
    "teacher": "Văn Hỉ",
    "guarantee": "Hoàn tiền nếu không hài lòng sau buổi 1",
    "limited": "Chỉ còn 5 suất cuối nhận kèm cặp 1:1 qua Zalo",
    "sessions": [
        "Buổi 1: Kích hoạt đôi mắt thiên tài — Kỹ thuật 3-2-1, chỉ tay dẫn đường",
        "Buổi 2: Bí thuật đọc cụm từ — Loại bỏ đọc thầm, cơ chế Tai-Mắt-Não",
        "Buổi 3: Thấu thị toàn bộ cuốn sách — Skimming 15 phút, bản đồ cấu trúc",
        "Buổi 4: Ghi chép thông minh — Smart Note, Mind Map, hệ thống 3 ô",
        "Buổi 5: Tư duy chọn sách đúng — Tiết kiệm 90% ngân sách mua sách",
        "Buổi 6: Công thức truyền tin 4 bước — Chia sẻ tri thức tự tin",
        "Buổi 7: Tổng kết & Ôn tập — Ghi nhớ chủ động, thuộc vĩnh viễn",
    ],
    "testimonials": "8 video học viên thực tế + 10 ảnh kết quả từ nhóm Zalo",
}

# === 40 GÓC TIẾP CẬN QUẢNG CÁO ĐA DẠNG ===
AD_ANGLES = [
    # Pain points (nỗi đau)
    {"id": "pain_01", "hook": "Đọc chậm thiệt thòi", "angle": "Bạn mất hàng giờ đọc sách nhưng không nhớ gì? Đây là giải pháp."},
    {"id": "pain_02", "hook": "Quên sạch sau khi đọc", "angle": "Đóng sách là quên? Lỗi không phải do bạn, mà do cách đọc."},
    {"id": "pain_03", "hook": "Áp lực tài liệu", "angle": "Tài liệu chất cao như núi? Biến áp lực thành lợi thế."},
    {"id": "pain_04", "hook": "Đọc thầm từ nhỏ", "angle": "Vẫn đọc thầm như hồi cấp 1? Bạn đang giới hạn chính mình."},
    {"id": "pain_05", "hook": "Không có thời gian", "angle": "Bận rộn không có nghĩa là không thể đọc sách mỗi ngày."},
    
    # Benefit (lợi ích)
    {"id": "benefit_01", "hook": "X3 tốc độ", "angle": "Tăng tốc đọc gấp 3 lần chỉ sau 7 buổi — có bằng chứng khoa học."},
    {"id": "benefit_02", "hook": "Nhớ lâu hơn", "angle": "Đọc nhanh mà vẫn nhớ — bí mật nằm ở kỹ thuật ghi nhớ chủ động."},
    {"id": "benefit_03", "hook": "Hiểu sâu hơn", "angle": "Tốc độ không làm giảm hiểu — ngược lại, còn hiểu sâu hơn."},
    {"id": "benefit_04", "hook": "Tiết kiệm thời gian", "angle": "15 phút/ngày là đủ để đọc xong một cuốn sách trong tuần."},
    {"id": "benefit_05", "hook": "Học bất kỳ đâu", "angle": "Học online qua Zoom, ở nhà vẫn bứt phá tốc độ đọc."},
    
    # Social proof (bằng chứng xã hội)
    {"id": "proof_01", "hook": "Học viên thành công", "angle": "Nguyễn Thuỳ Ngân tăng từ 300 lên 1000 từ/phút sau 7 buổi."},
    {"id": "proof_02", "hook": "Cam kết hoàn tiền", "angle": "Không hiệu quả? Hoàn phí — không có rủi ro nào cả."},
    {"id": "proof_03", "hook": "Số lượng có hạn", "angle": "Chỉ còn 5 suất cuối nhận kèm cặp 1:1 qua Zalo."},
    {"id": "proof_04", "hook": "Học viên đa dạng", "angle": "Từ học sinh, sinh viên đến người đi làm, ai cũng áp dụng được."},
    {"id": "proof_05", "hook": "Kết quả đo lường được", "angle": "Đo tốc độ trước và sau — con số không biết nói dối."},
    
    # Curiosity (tò mò)
    {"id": "curious_01", "hook": "Bí mật tỷ phú", "angle": "Warren Buffett đọc 500 trang/ngày. Bí mật của ông là gì?"},
    {"id": "curious_02", "hook": "Khoa học não bộ", "angle": "Mắt bạn có thể đọc nhanh gấp 5 lần — đây là cách kích hoạt."},
    {"id": "curious_03", "hook": "Kỹ thuật thiên tài", "angle": "Elon Musk, Bill Gates, Mark Zuckerberg — họ đọc sách thế nào?"},
    {"id": "curious_04", "hook": "Sự thật bất ngờ", "angle": "Đọc chậm không giúp bạn nhớ lâu hơn. Sự thật ngược lại."},
    {"id": "curious_05", "hook": "AI không thể thay thế", "angle": "AI có thể đọc giúp bạn, nhưng không thể hiểu giúp bạn."},
    
    # Objection handling (xoá rào cản)
    {"id": "object_01", "hook": "Không có thời gian", "angle": "Chỉ 7 buổi tối, mỗi buổi 60-90 phút — ai cũng sắp xếp được."},
    {"id": "object_02", "hook": "Sợ học online kém hiệu quả", "angle": "Zoom tương tác trực tiếp, sửa lỗi từng người — hiệu quả hơn học offline."},
    {"id": "object_03", "hook": "Giá quá rẻ, sợ không chất lượng", "angle": "Giá ưu đãi chỉ 980k — nhưng cam kết hoàn tiền nếu không hài lòng."},
    {"id": "object_04", "hook": "Đã thử nhiều cách không hiệu quả", "angle": "Phương pháp này đã được kiểm chứng với hàng ngàn học viên."},
    {"id": "object_05", "hook": "Ngại học cùng lớp đông", "angle": "Sĩ số giới hạn, kèm cặp 1:1 qua Zalo sau mỗi buổi học."},
    
    # Urgency (khẩn cấp)
    {"id": "urgent_01", "hook": "Giảm giá có hạn", "angle": "Từ 2 triệu chỉ còn 980k — ưu đãi đặc biệt cho 5 người đăng ký đầu tiên."},
    {"id": "urgent_02", "hook": "Sắp hết suất", "angle": "Chỉ còn 5 suất cuối cùng nhận quà tặng kèm cặp 1:1."},
    {"id": "urgent_03", "hook": "Cơ hội cuối", "angle": "Đợt ưu đãi này sắp kết thúc — đăng ký ngay trước khi hết."},
    {"id": "urgent_04", "hook": "Đầu năm học mới", "angle": "Đầu năm là thời điểm vàng để đầu tư vào kỹ năng học tập."},
    {"id": "urgent_05", "hook": "Không chần chừ", "angle": "Càng chần chừ, bạn càng mất thêm cơ hội đọc những cuốn sách hay."},
    
    # Lifestyle (phong cách sống)
    {"id": "life_01", "hook": "Người thành công đọc sách", "angle": "90% người thành công dành 30 phút mỗi ngày để đọc sách."},
    {"id": "life_02", "hook": "Đọc sách là đầu tư", "angle": "Một cuốn sách 100k có thể thay đổi cuộc đời bạn — khoản đầu tư rẻ nhất."},
    {"id": "life_03", "hook": "Văn hoá đọc cho gia đình", "angle": "Làm gương cho con — xây dựng văn hoá đọc ngay tại nhà."},
    {"id": "life_04", "hook": "Cạnh tranh trong thời đại số", "angle": "Người đọc nhanh có lợi thế gấp 3 lần trong thời đại bùng nổ thông tin."},
    {"id": "life_05", "hook": "Học tập suốt đời", "angle": "Kỹ năng đọc nhanh là nền tảng cho mọi kỹ năng học tập khác."},
    
    # Specific technique (kỹ thuật cụ thể)
    {"id": "tech_01", "hook": "Chỉ tay dẫn đường", "angle": "Kỹ thuật đơn giản nhất — dùng ngón tay dẫn mắt, tăng tốc ngay lập tức."},
    {"id": "tech_02", "hook": "Loại bỏ đọc thầm", "angle": "Đọc thầm giới hạn bạn ở 250 từ/phút. Loại bỏ nó, bạn đọc được 1000+."},
    {"id": "tech_03", "hook": "Kỹ thuật 3-2-1", "angle": "3 phút, 2 phút, 1 phút — tăng tốc qua từng vòng lặp."},
    {"id": "tech_04", "hook": "Chunking thần tốc", "angle": "Thay vì đọc từng chữ, hãy đọc cụm từ — như xe đạp lên ô tô."},
    {"id": "tech_05", "hook": "Skimming bản đồ", "angle": "3 phút quét bản đồ trước khi đọc — tiết kiệm 50% thời gian."},
]

# === HÌNH THỨC BÀI VIẾT ===
POST_FORMATS = [
    "list",       # Danh sách lợi ích
    "story",      # Câu chuyện cá nhân
    "question",   # Đặt câu hỏi khơi gợi
    "myth_bust",  # Phá vỡ quan niệm sai
    "stat",       # Số liệu gây sốc
    "testimonial",# Chia sẻ học viên
    "comparison", # So sánh trước-sau
    "howto",      # Hướng dẫn từng bước
]


def get_api_key():
    env_path = Path.home() / '.hermes' / '.env'
    if env_path.exists():
        for line in env_path.read_text().split('\n'):
            if line.startswith('OPENROUTER_API_KEY='):
                return line.split('=', 1)[1].strip()
    return ''

API_KEY = get_api_key()


def call_llm(prompt, system="Bạn là copywriter quảng cáo chuyên nghiệp, viết tiếng Việt."):
    if not API_KEY:
        return None
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek/deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 2000,
            },
            timeout=90,
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"   ⚠️ LLM: {e}")
    return None


def generate_ad(angle, post_format, day_number):
    """Tạo 1 nội dung quảng cáo hoàn chỉnh"""
    angle_name = angle['hook']
    angle_desc = angle['angle']
    
    # Build session details
    seminar_details = '\n'.join([f"- {s}" for s in COURSE['sessions']])
    
    prompt = f"""Bạn là copywriter quảng cáo Facebook chuyên nghiệp, viết tiếng Việt. Viết 1 bài quảng cáo cho khoá học Speed Reading Online 7 Buổi Zoom.

THÔNG TIN KHOÁ HỌC CHI TIẾT:
- Tên: {COURSE['name']}
- Giảng viên: {COURSE['teacher']}
- Giá: {COURSE['price']} (giá gốc {COURSE['original_price']} — tiết kiệm 75%)
- Hình thức: {COURSE['format']}
- Kết quả: {COURSE['result']}
- Cam kết: {COURSE['bonus']}
- Đảm bảo: {COURSE['guarantee']}
- Số lượng: {COURSE['limited']}
- Link đăng ký: {COURSE['url']}

LỘ TRÌNH 7 BUỔI:
{seminar_details}

BẰNG CHỨNG THỰC TẾ:
- {COURSE['testimonials']}
- 8 video YouTube học viên chia sẻ kết quả thật
- 10+ ảnh chụp phản hồi từ nhóm Zalo

GÓC TIẾP CẬN: {angle_name} — {angle_desc}
HÌNH THỨC BÀI VIẾT: {post_format}

YÊU CẦU BÀI VIẾT:
- Mở đầu hấp dẫn, câu đầu tiên phải gây tò mò
- Nội dung có giá trị, không bán hàng quá lộ liễu
- Đề cập đến lợi ích: X3 tốc độ, nhớ lâu, cam kết hoàn tiền
- CTA: "Inbox mình để được tư vấn" hoặc "Đăng ký ngay tại link trong bio"
- TUYỆT ĐỐI KHÔNG đưa link vào bài viết (link chỉ để trong phần quảng cáo)
- XUỐNG HÀNH thường xuyên, dễ đọc trên điện thoại
- Dùng emoji phù hợp, gần gũi
- Độ dài: 5-8 dòng

YÊU CẦU HÌNH ẢNH:
- Mô tả ảnh quảng cáo bằng tiếng Anh, ngắn gọn, phù hợp với nội dung
- Phong cách: chuyên nghiệp, hiện đại, màu sắc ấm áp

YÊU CẦU KỊCH BẢN VIDEO:
- Lời thoại 20-30 giây, tự nhiên, gần gũi
- Có CTA cuối video
- Không link

ĐẦU RA LÀ JSON:
{{
    "title": "Tiêu đề quảng cáo ngắn gọn",
    "content": "Nội dung bài viết đầy đủ...",
    "image_prompt": "Prompt tiếng Anh cho ảnh quảng cáo",
    "video_script": "Lời thoại video 20-30s",
    "hashtags": ["#ad1", "#ad2", "#ad3"]
}}
"""
    
    result = call_llm(prompt)
    if result:
        # Clean JSON
        result = re.sub(r'^```(?:json)?\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        try:
            data = json.loads(result)
            data['angle'] = angle_name
            data['format'] = post_format
            data['day'] = day_number
            return data
        except:
            m = re.search(r'\{.*\}', result, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group())
                    data['angle'] = angle_name
                    data['format'] = post_format
                    data['day'] = day_number
                    return data
                except:
                    pass
    return None


def generate_ads_for_day(count=3, dry_run=False):
    """Tạo N nội dung quảng cáo cho 1 ngày"""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📢 TẠO {count} NỘI DUNG QUẢNG CÁO — {today}")
    print(f"{'='*60}")
    
    # Random chọn góc tiếp cận + hình thức
    selected_angles = random.sample(AD_ANGLES, min(count * 2, len(AD_ANGLES)))
    selected_formats = random.choices(POST_FORMATS, k=count)
    
    ads = []
    for i in range(count):
        angle = selected_angles[i]
        fmt = selected_formats[i]
        print(f"\n📝 Bài {i+1}: [{angle['hook']}] + [{fmt}]")
        
        if dry_run:
            print(f"   Góc: {angle['angle']}")
            continue
        
        ad = generate_ad(angle, fmt, i+1)
        if ad:
            ads.append(ad)
            print(f"   ✅ {ad.get('title', 'OK')[:60]}")
        else:
            print(f"   ❌ Lỗi tạo nội dung")
    
    if dry_run:
        return ads
    
    # Lưu ads
    ads_dir = ADS_DIR / today
    ads_dir.mkdir(parents=True, exist_ok=True)
    
    for i, ad in enumerate(ads):
        filename = f"ad-{today}-{i+1}.json"
        (ads_dir / filename).write_text(json.dumps(ad, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"   💾 Đã lưu: {filename}")
    
    # Update index
    index = []
    if ADS_JSON.exists():
        try: index = json.loads(ADS_JSON.read_text())
        except: pass
    
    for i, ad in enumerate(ads):
        entry = {
            'title': ad.get('title', '')[:60],
            'filename': f"ads/{today}/ad-{today}-{i+1}.json",
            'date': today,
            'angle': ad.get('angle', ''),
            'format': ad.get('format', ''),
        }
        index.append(entry)
    
    ADS_JSON.write_text(json.dumps(index, ensure_ascii=False, indent=2))
    
    # In ra preview
    print(f"\n{'='*60}")
    print(f"📊 PREVIEW {len(ads)} NỘI DUNG QUẢNG CÁO")
    print(f"{'='*60}")
    for i, ad in enumerate(ads):
        print(f"\n--- Bài {i+1}: {ad.get('title', '')} ---")
        print(f"🎯 Góc: {ad.get('angle', '')}")
        print(f"📄 Nội dung:\n{ad.get('content', '')[:200]}...")
        print(f"🎨 Image prompt: {ad.get('image_prompt', '')[:80]}...")
        print(f"🎬 Video script: {ad.get('video_script', '')[:100]}...")
    
    return ads


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tạo nội dung quảng cáo')
    parser.add_argument('--count', '-n', type=int, default=3, help='Số nội dung (mặc định: 3)')
    parser.add_argument('--dry-run', action='store_true', help='Chỉ xem trước, không lưu')
    args = parser.parse_args()
    
    generate_ads_for_day(count=args.count, dry_run=args.dry_run)


if __name__ == '__main__':
    main()