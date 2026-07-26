#!/usr/bin/env python3
"""Build searchable content bank index from ebooks and website."""
import json
from pathlib import Path
from collections import defaultdict

# Sources
EBOOK_DIR = Path("/home/vider/speedreading-research/Speed Reading")
STATIC_DIR = EBOOK_DIR / "speedreading-vn-main/static"
INDEX_OUT = EBOOK_DIR / "content_bank_index.json"

# Load existing knowledge base if available
KB_PATH = STATIC_DIR / "static_knowledge_base.json"
knowledge_base = []
if KB_PATH.exists():
    with open(KB_PATH, encoding="utf-8") as f:
        knowledge_base = json.load(f)

# Ebook text extracts (from previous pdftotext outputs)
EBOOK_EXCERPTS = {
    "ebook-sieu-toc-doc-sach.pdf": {
        "title": "Siêu Tốc Đọc Sách - Bí Kíp Làm Chủ Tri Thức",
        "author": "Văn Hỉ",
        "pages": 18,
        "key_frameworks": [
            "Framework 3 bước đọc: Tổng quan → Chi tiết → Ghi chép",
            "Con trỏ thần kỳ",
            "Tầm nhìn siêu nhân",
            "Hạn chế đọc thầm: ngân nga/đếm 1-4",
            "Sổ Thông Minh: Kể lại + Mind map + Tóm tắt siêu ngắn",
        ],
        "quotes": [
            "Sách là kho báu tri thức không đáy",
            "Bộ não giống như siêu máy tính đang được nâng cấp liên tục",
            "Đọc sách cũng giống như xem phim, nhưng bạn là đạo diễn trong trí tưởng tượng",
        ],
        "angles": [
            "framework read",
            "con tro than ky",
            "tam nhin sieu nhan",
            "han che doc tham",
            "so thong minh",
            "mind map",
            "thoi quen doc",
        ],
    },
    "ebook-14-ky-thuat-speed-reading.pdf": {
        "title": "14 Kỹ Thuật Speed Reading",
        "key_frameworks": [
            "Con trPointer + Cover up method",
            "Mở rộng tầm nhìn 3-5 từ/lần",
            "Giảm đọc quay lại (Regression)",
            "Timer Drill: đo WPM, tăng 10-20%/lần",
            "Đọc chủ động: Đặt câu hỏi → Ghi chú → Tóm tắt → Kết nối",
            "Skimming → Scanning → Active Reading",
            "Smart Notes: Fleeting → Literature → Permanent notes",
            "Mind Map + Active Recall + Spaced Repetition",
            "Phân biệt 5 mục đích đọc: Tổng quan/Tìm kiếm/Học sâu/Giải trí/Đánh giá",
        ],
        "angles": [
            "timer drill",
            "active reading",
            "smart notes",
            "mind map",
            "active recall",
            "spaced repetition",
            "skimming",
            "scanning",
            "purposive reading",
        ],
    },
    "ebook-lo-trinh-hoc-tap-1-nam.pdf": {
        "title": "Lộ Trình Học Tập 1 Năm",
        "key_frameworks": [
            "Tháng 6-8: Ôn tập nhẹ, khám phá sở thích, kỹ năng sống",
            "Tháng 9-12: Xây nền móng, đặt mục tiêu, kỹ năng tự học",
            "Tháng 1: Đánh giá, nghỉ ngơi, củng cố",
            "Tháng 2-5: Tăng tốc, chuyên sâu, chuẩn bị thi cuối năm",
            "Pattern mỗi tháng: Học tập → Kỹ năng mềm → Sức khỏe → Gia đình",
        ],
        "angles": [
            "summer plan",
            "semester 1",
            "winter break",
            "semester 2",
            "yearly cycle",
        ],
    },
    "ebook-chinh-phuc-moi-mon-hoc-1.pdf": {
        "title": "Chinh Phục Mọi Môn Học",
        "key_frameworks": [
            "11 môn học: Lịch sử, Toán, Ngữ văn, Vật lý, Hóa học, Sinh học, Địa lý, GDCD, Công nghệ, Tin học, Hoạt động trải nghiệm",
            "Pattern chung: Giá trị/ý nghĩa → Lộ trình cấp 2→3 → Cách học khoa học → Áp dụng Speed Reading",
            "Toán: Sổ lỗi sai + sổ phương pháp",
            "Lịch sử: Kể chuyện + Timeline + Bản đồ tư duy",
            "Sinh học: Vẽ sơ đồ chu trình + bảng so sánh",
            "GDCD: Thảo luận + đóng vai + ngân hàng luận điểm",
        ],
        "angles": [
            "toan",
            "ngu van",
            "tieng anh",
            "vat ly",
            "hoa hoc",
            "sinh hoc",
            "dia ly",
            "gducd",
            "cong nghe",
            "tin hoc",
            "trai nghiem",
        ],
    },
    "ebook-thuoc-bai-tai-lop.pdf": {
        "title": "Thuộc Bài Tại Lớp",
        "key_frameworks": [
            "Chuẩn bị trước: Đọc lướt 5-10 phút, chuẩn bị đồ dùng, ngủ đủ, ăn sáng",
            "Trong giờ: Nghe chủ động (đặt câu hỏi, dự đoán, liên hệ), ghi chú từ khóa",
            "Cornell Notes: Cột chính 2/3, cột gợi Ý 1/3, tóm tắt cuối trang",
            "Mind Map tại lớp: Chủ đề trung tâm → nhánh màu → từ khóa → hình ảnh",
            "Mnemonics: Từ viết tắt + Story method",
            "Sau giờ học: Ôn 10-15 phút, giảng lại cho bạn bè, làm bài tập ngay",
            "Spaced Repetition: Ôn sau 1 ngày → 3 ngày → 1 tuần → 1 tháng",
        ],
        "angles": [
            "cornell notes",
            "mind map",
            "mnemonics",
            "story method",
            "spaced repetition",
            "active listening",
        ],
    },
    "ebook-von-sinh-ton.pdf": {
        "title": "Vốn Sinh Tồn",
        "key_frameworks": [
            "Quy tắc 4 Không + 5 Phải",
            "Vùng an toàn cơ thể",
            "An toàn mạng - không chia sẻ thông tin cá nhân",
            "Bảo vệ khỏi người lạ",
            "Diễn tập tình huống khẩn cấp",
            "Giữ bình tĩnh khi gặp nguy hiểm",
            "Số điện thoại khẩn cấp 113/114/115",
            "Ô nhiễm môi trường",
            "Bạo lực học đường",
            "Kỹ năng sống cơ bản: Tự phục vụ, quản lý cảm xúc, giao tiếp",
        ],
        "angles": [
            "safety rules",
            "internet safety",
            "stranger danger",
            "emergency",
            "environment",
            "bullying",
            "life skills",
        ],
    },
}

# Research topic banks
RESEARCH_TOPICS = {
    "Tin Tức & Xu Hướng": {
        "Thi THPT Quốc gia": "Thay đổi format, điểm chuẩn, đề thi",
        "Chương trình giáo dục mới": "Phổ thát mới, sách giáo khoa mới",
        "AI trong giáo dục": "ChatGPT trong lớp học, AI grading",
        "App học tập": "Quizlet, Duolingo, Khan Academy VN",
        "Microlearning": "Học 5 phút/ngày, spaced learning",
        "Bạo lực học đường": "Clip mới, chính sách nhà trường",
        "Cận thị học sinh": "Số liệu, phòng ngừa",
        "Béo phì học đường": "Dinh dưỡng, thể thao",
    },
    "Thực Trạng Xã Hội": {
        "Áp lực học tập": "Con học 12 tiếng/ngày, phụ huynh chi học thêm",
        "Ngộ nhận phổ biến": [
            "Đọc nhanh = đọc không hiểu",
            "Con giỏi phải học thêm",
            "Điểm cao = học đúng phương pháp",
            "Sách điện tử không tốt bằng sách giấy",
            "Trẻ con càng học nhiều càng giỏi",
        ],
        "Tin tức thực tế": [
            "Học sinh tự tử vì áp lực học",
            "Cha mẹ tố cáo giáo viên",
            "Bạo lực học đường clip mới",
            "Trẻ em lừa đảo online",
            "Thiên tai ảnh hưởng học tập",
        ],
    },
}

def build_index():
    """Build comprehensive content bank index."""
    index = {
        "meta": {
            "created_at": "2026-07-22",
            "total_sources": len(EBOOK_EXCERPTS) + len(knowledge_base),
            "categories": ["Ebook", "Website", "Research Topics"],
        },
        "ebooks": EBOOK_EXCERPTS,
        "website": {
            "total_pages": len(knowledge_base),
            "pages_by_type": defaultdict(int),
            "key_pages": [],
        },
        "research_topics": RESEARCH_TOPICS,
        "content_bank": {
            "ebook_angles": [],
            "research_angles": [],
            "quotes": [],
            "case_studies": [],
            "statistics": [],
        },
    }

    # Index website pages
    for page in knowledge_base:
        ptype = page.get("page_type", "Khác")
        index["website"]["pages_by_type"][ptype] += 1
        if ptype in ["Trang chủ", "Đào tạo", "Khóa học Zoom", "Review/Cảm nhận"]:
            index["website"]["key_pages"].append({
                "filename": page["filename"],
                "title": page.get("title", ""),
                "type": ptype,
            })

    # Extract angles and quotes from ebooks
    for filename, ebook in EBOOK_EXCERPTS.items():
        for angle in ebook.get("angles", []):
            index["content_bank"]["ebook_angles"].append({
                "source": filename,
                "angle": angle,
                "category": "framework",
            })
        for quote in ebook.get("quotes", []):
            index["content_bank"]["quotes"].append({
                "source": filename,
                "quote": quote,
                "category": "inspiration",
            })

    # Research angles
    for category, topics in RESEARCH_TOPICS.items():
        for topic, detail in topics.items():
            if isinstance(detail, list):
                for sub in detail:
                    index["content_bank"]["research_angles"].append({
                        "category": category,
                        "topic": topic,
                        "sub_topic": sub,
                    })
            else:
                index["content_bank"]["research_angles"].append({
                    "category": category,
                    "topic": topic,
                    "detail": detail,
                })

    # Statistics bank
    index["content_bank"]["statistics"] = [
        {"text": "127 học viên đã thay đổi", "category": "social_proof"},
        {"text": "850 từ/phút tốc độ trung bình", "category": "result"},
        {"text": "80% nhớ sau 30 ngày", "category": "result"},
        {"text": "300% cải thiện tốc độ đọc", "category": "result"},
        {"text": "Giảm 5-7 tiếng/tuần học tập", "category": "result"},
        {"text": "Cam kết hoàn phí, chỉ 5/127 yêu cầu", "category": "guarantee"},
        {"text": "76% học sinh THPT học thêm", "category": "market_data"},
        {"text": "62% học sinh ngủ dưới 7 tiếng/ngày", "category": "market_data"},
        {"text": "Pho huynh chi 3-10 trieu/thang hoc them", "category": "market_data"},
    ]

    return index

def print_summary(index):
    """Print index summary."""
    print("=" * 70)
    print("📚 CONTENT BANK INDEX")
    print("=" * 70)
    print(f"\n📊 Sources:")
    print(f"  • Ebooks: {len(index['ebooks'])} cuốn")
    print(f"  • Website pages: {index['website']['total_pages']} trang")
    print(f"  • Research topics: {len(index['research_topics'])} categories")
    
    print(f"\n📝 Content Bank:")
    print(f"  • Ebook angles: {len(index['content_bank']['ebook_angles'])}")
    print(f"  • Research angles: {len(index['content_bank']['research_angles'])}")
    print(f"  • Quotes: {len(index['content_bank']['quotes'])}")
    print(f"  • Statistics: {len(index['content_bank']['statistics'])}")
    
    print(f"\n📈 Website breakdown:")
    for ptype, count in sorted(index['website']['pages_by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {ptype}: {count}")
    
    print("\n✅ Index ready for content generation!")

if __name__ == "__main__":
    index = build_index()
    
    with open(INDEX_OUT, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved: {INDEX_OUT}")
    print_summary(index)
