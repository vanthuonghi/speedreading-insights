#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webinar_email.py — Email engine cho Webinar Free Speed Reading
Chuoi 7 email: xac_nhan → nho_1d → nho_1h → nho_10p → cam_on_replay → case_study → upsell
Tai dung cu truc tu workshop_email.py (da chay thuc te), chuyen biet data file + sequence.
Chay: python3 webinar_email.py [--dry-run] [--test-email addr] [--force-step buoc]
"""
import json, ssl, smtplib, os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

BASE = Path(__file__).parent
REGS_FILE = BASE / "webinar_registrations.json"
SENT_FILE = BASE / "webinar_sent.json"

# --- SMTP (tai dung cau hinh gmail app password nhu workshop) ---
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": os.environ.get("SR_SMTP_USER", ""),
    "password": os.environ.get("SR_SMTP_PASSWORD", ""),
}
FROM_EMAIL = SMTP_CONFIG["user"] or "admin@speedreading.vn"
FROM_NAME = "Hỉ - Speed Reading Việt Nam"

# Ngay webinar gan nhat (chinh sua thu cong hoac tu dong lay tu form)
# Mac dinh: Chu Nhat tiep theo 20:00
def next_webinar_date():
    now = datetime.now()
    days_ahead = (6 - now.weekday()) % 7  # 6 = Chu Nhat
    if days_ahead == 0:
        days_ahead = 7
    d = (now + timedelta(days=days_ahead)).replace(hour=20, minute=0, second=0, microsecond=0)
    return d

# ============ EMAIL TEMPLATES (HTML) ============
def _wrap(name, body):
    return f"""<div style="font-family:Inter,Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;background:#fff;color:#1e293b">
<h2 style="color:#dc2626;margin:0 0 12px">Chào {name},</h2>
{body}
<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0">
<p style="font-size:13px;color:#64748b">Hỉ - Speed Reading Việt Nam<br>Hotline: 0899.320.202 | Zalo 24/7</p>
</div>"""

def email_1_confirm(name, wb):
    body = f"""Cảm ơn {name} đã đăng ký <b>Webinar Miễn Phí: Đọc hiểu 1000 từ/phút</b>! 📚<br><br>
Buổi học trực tuyến diễn ra: <b>{wb.strftime('%H:%M Thứ %w ngày %d/%m')}</b> (tự động tính lịch).<br><br>
🎁 <b>Quà tặng của bạn:</b> Ebook "15 phút đọc hiểu mỗi ngày" + Template Smart Note.<br>
👉 <b>Tải tại đây:</b> https://speedreading.vn/ebook-webinar (mật khẩu: docnhanh)<br><br>
Chuẩn bị: 1 cuốn sách bạn thích + bút. Hẹn gặp {name} ở Zoom!"""
    return _wrap(name, body)

def email_2_remind_1d(name, wb):
    body = f"""Chào {name}, nhắc nhẹ: <b>ngày mai 20:00</b> là Webinar Miễn Phí của mình 📖<br><br>
Đừng quên chuẩn bị: sách + bút. Mở Zoom sớm 5 phút để test âm thanh.<br><br>
💡 Mẹo nhỏ: đêm nay đọc 1 trang bình thường, đo thời gian — ngày mai bạn sẽ thấy sự khác biệt!"""
    return _wrap(name, body)

def email_3_remind_1h(name, wb):
    body = f"""{name} ơi, <b>còn 1 tiếng nữa</b> bắt đầu Webinar! ⏰<br><br>
👉 Vào Zoom ngay: https://zoom.us/j/1234567890 (ID: 123 456 7890)<br><br>
Đừng bỏ lỡ — mình sẽ demo tăng tốc độ đọc gấp 3 lần trực tiếp!"""
    return _wrap(name, body)

def email_4_remind_10m(name, wb):
    body = f"""🔔 {name}, <b>Webinar bắt đầu sau 10 phút!</b><br><br>
👉 Vào ngay: https://zoom.us/j/1234567890<br><br>
Mở sách ra, sẵn sàng thực hành cùng mình nhé!"""
    return _wrap(name, body)

def email_5_thanks_replay(name, wb):
    body = f"""Cảm ơn {name} đã tham gia Webinar hôm qua! 🎉<br><br>
📼 <b>Xem lại + Replay:</b> https://speedreading.vn/replay-webinar<br>
📚 <b>Ebook + Smart Note:</b> https://speedreading.vn/ebook-webinar (mật: docnhanh)<br><br>
💬 Thắc mắc? Nhắn Zalo 0899.320.202, mình hỗ trợ 24/7.<br><br>
<i>Ưu đãi đặc biệt cho người tham gia sẽ có ở email tới — đừng bỏ lỡ!</i>"""
    return _wrap(name, body)

def email_6_case_study(name, wb):
    body = f"""{name} có muốn biết <b>Tuấn (FPT)</b> đã làm gì không? 📈<br><br>
Ngày đầu: đọc <b>300 từ/phút</b>, đọc xong là quên.<br>
Sau 7 buổi Zoom: <b>1100+ từ/phút</b>, hiểu sâu, nhớ lâu.<br><br>
👉 Xem câu chuyện của Tuấn: https://speedreading.vn/student-tuan<br><br>
<i>Anh ấy bảo: "Online mà như offline, Hỉ sửa lỗi từng ngày".</i>"""
    return _wrap(name, body)

def email_7_upsell(name, wb):
    body = f"""{name} ơi, <b>ưu đãi cuối cùng</b> dành cho người tham gia Webinar 🔥<br><br>
🎓 <b>Lớp Zoom 7 buổi:</b> 980.000đ (gốc 4.000.000đ - tiết kiệm 75%)<br>
✅ Hoàn tiền 100% nếu không hài lòng sau buổi 1<br>
✅ Zalo hỗ trợ 24/7, sửa lỗi từng ngày<br>
✅ Chỉ còn 5 suất cuối + tặng kèm Zalo 1:1<br><br>
👉 Đăng ký: https://speedreading.vn/webinar-dang-ky<br><br>
<i>Không áp lực — chỉ cần một quyết định đúng cho việc học tập cả đời.</i>"""
    return _wrap(name, body)

# ============ ENGINE ============
def send_email(to_email, to_name, subject, html_content):
    if not SMTP_CONFIG["user"] or not SMTP_CONFIG["password"]:
        print(f"   ⚠️ SMTP chưa cấu hình. Bỏ qua gửi đến {to_email}")
        print(f"   📧 Subject: {subject}")
        return {"status": "skipped"}
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as s:
            s.starttls(context=ctx)
            s.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            s.sendmail(FROM_EMAIL, to_email, msg.as_string())
        print(f"   ✅ Đã gửi đến {to_email}")
        return {"status": "sent"}
    except Exception as e:
        print(f"   ❌ Lỗi gửi {to_email}: {e}")
        return {"status": "failed", "error": str(e)}

def load_registrations():
    if not REGS_FILE.exists():
        return []
    try:
        return json.loads(REGS_FILE.read_text(encoding="utf-8"))
    except:
        return []

def load_sent():
    if not SENT_FILE.exists():
        return {}
    try:
        return json.loads(SENT_FILE.read_text(encoding="utf-8"))
    except:
        return {}

def save_sent(sent):
    SENT_FILE.write_text(json.dumps(sent, ensure_ascii=False, indent=2), encoding="utf-8")

# Buoc email dua vao thoi gian den webinar
def get_email_step(reg, now):
    wb = datetime.fromisoformat(reg.get("webinar_date", "")) if reg.get("webinar_date") else next_webinar_date()
    delta = (wb - now).total_seconds() / 3600  # gio
    sent = reg.get("_sent", [])
    if "confirm" not in sent and 0 <= delta <= 240:
        return "confirm", "📚 Xác nhận đăng ký Webinar Miễn Phí + Quà tặng", email_1_confirm
    if "remind_1d" not in sent and 18 <= delta <= 30:
        return "remind_1d", "⏰ Ngày mai 20:00 — Webinar Miễn Phí nhắc nhẹ", email_2_remind_1d
    if "remind_1h" not in sent and 0.75 <= delta <= 1.25:
        return "remind_1h", "⏰ Còn 1 tiếng — Vào Zoom ngay!", email_3_remind_1h
    if "remind_10m" not in sent and 0.1 <= delta <= 0.25:
        return "remind_10m", "🔔 Webinar bắt đầu sau 10 phút!", email_4_remind_10m
    if "thanks" not in sent and -26 <= delta <= -1:
        return "thanks", "🎉 Cảm ơn bạn — Replay + Ebook", email_5_thanks_replay
    if "case" not in sent and -50 <= delta <= -26:
        return "case", "📈 Học viên 300→1100 từ/phút", email_6_case_study
    if "upsell" not in sent and -120 <= delta <= -50:
        return "upsell", "🔥 Ưu đãi cuối — Lớp Zoom 980k", email_7_upsell
    return None

def add_registration(name, email, phone, source="webinar-free", speed="200-300"):
    regs = load_registrations()
    if any(r["email"].lower() == email.lower() for r in regs):
        print(f"   ℹ️ {email} đã tồn tại, bỏ qua")
        return False
    regs.append({
        "name": name, "email": email, "phone": phone,
        "source": source, "speed": speed,
        "registered_at": datetime.now().isoformat(),
        "webinar_date": next_webinar_date().isoformat(),
        "_sent": []
    })
    REGS_FILE.write_text(json.dumps(regs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   ✅ Đã thêm {name} <{email}>")
    return True

def process(dry_run=False, test_email=None, force_step=None):
    print(f"📧 [{datetime.now():%Y-%m-%d %H:%M}] Xử lý email webinar" + (" [DRY-RUN]" if dry_run else ""))
    regs = load_registrations()
    sent = load_sent()
    if not regs:
        print("   ℹ️ Không có đăng ký nào")
        return
    now = datetime.now()
    for reg in regs:
        email_addr = reg["email"]
        # Test mode: chi gui cho 1 email
        if test_email and email_addr != test_email:
            continue
        force_map = {
            "confirm": ("confirm", "📚 Xác nhận đăng ký Webinar Miễn Phí + Quà tặng", email_1_confirm),
            "remind_1d": ("remind_1d", "⏰ Ngày mai 20:00 — Webinar nhắc nhẹ", email_2_remind_1d),
            "remind_1h": ("remind_1h", "⏰ Còn 1 tiếng — Vào Zoom ngay!", email_3_remind_1h),
            "remind_10m": ("remind_10m", "🔔 Webinar bắt đầu sau 10 phút!", email_4_remind_10m),
            "thanks": ("thanks", "🎉 Cảm ơn bạn — Replay + Ebook", email_5_thanks_replay),
            "case": ("case", "📈 Học viên 300→1100 từ/phút", email_6_case_study),
            "upsell": ("upsell", "🔥 Ưu đãi cuối — Lớp Zoom 980k", email_7_upsell),
        }
        step = force_map.get(force_step or "") or get_email_step(reg, now)
        if not step:
            continue
        step_id, subject, gen = step
        wb = datetime.fromisoformat(reg.get("webinar_date", "")) if reg.get("webinar_date") else next_webinar_date()
        html = gen(reg["name"], wb)
        if dry_run:
            print(f"   🔍 [dry] {email_addr} ← {subject}")
            continue
        res = send_email(email_addr, reg["name"], subject, html)
        if res["status"] == "sent":
            reg.setdefault("_sent", []).append(step_id)
            sent[email_addr] = sent.get(email_addr, {})
            sent[email_addr][step_id] = datetime.now().isoformat()
    if not dry_run:
        # luu _sent vao regs
        REGS_FILE.write_text(json.dumps(regs, ensure_ascii=False, indent=2), encoding="utf-8")
        save_sent(sent)
    print("   🏁 Xong.")

if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    test = None
    force = None
    for i, a in enumerate(sys.argv):
        if a == "--test-email":
            test = sys.argv[i+1]
        if a == "--force-step":
            force = sys.argv[i+1]
    if "--add" in sys.argv:
        # --add "Ten|email@x.com|0901"
        parts = sys.argv[sys.argv.index("--add")+1].split("|")
        add_registration(*parts)
    else:
        process(dry_run=dry, test_email=test, force_step=force)
