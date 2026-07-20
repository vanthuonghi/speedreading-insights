#!/usr/bin/env python3
"""
Hệ thống gửi email tự động cho Workshop Speed Reading
========================================================
Gửi 5 email trong chuỗi: Xác nhận → Nhắc 1h → Nhắc 10' → Cảm ơn → Upsell

Cách dùng:
  python3 workshop_email.py                          # Kiểm tra & gửi email đến hạn
  python3 workshop_email.py --test email@example.com  # Gửi email test
  python3 workshop_email.py --send-all                # Gửi tất cả email đang chờ

Cron schedule:
  30 6 * * 1  cd /root/speedreading-research && python3 workshop_email.py       # 06:30 Thứ 2 — gửi email xác nhận
  0 18 * * 1  cd /root/speedreading-research && python3 workshop_email.py       # 18:00 Thứ 2 — nhắc 1h trước
  0 19 * * 1  cd /root/speedreading-research && python3 workshop_email.py       # 19:50 Thứ 2 — nhắc 10' trước
  30 21 * * 1 cd /root/speedreading-research && python3 workshop_email.py       # 21:30 Thứ 2 — cảm ơn + replay
  0 8 * * 2   cd /root/speedreading-research && python3 workshop_email.py       # 08:00 Thứ 3 — upsell membership
"""
import json, os, smtplib, ssl, sys, re, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path.home() / 'speedreading-research'
REGS_FILE = BASE / 'workshop_registrations.json'
SENT_FILE = BASE / 'workshop_emails_sent.json'

# ─── SMTP CONFIG ───
# VH: Nếu bạn dùng Gmail SMTP, cần tạo App Password
# Lấy từ https://myaccount.google.com/apppasswords
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "",      # Nhập email của bạn (VH)
    "password": "",  # Nhập App Password
}
FROM_NAME = "Văn Hỉ - Speed Reading Việt Nam"
FROM_EMAIL = ""  # Email gửi đi

# ─── WORKSHOP INFO ───
WORKSHOP = {
    "title": "Workshop Speed Reading — Đọc nhanh gấp 3 lần",
    "time": "20:00 - 21:00",
    "day": "Thứ 2",
    "zoom_link": "https://zoom.us/j/...",  # Link Zoom cố định
    "zoom_id": "...",
    "zoom_pass": "...",
    "hotline": "0899.320.202",
    "fb_page": "Speed Reading HCM",
    "membership_url": "https://vanthuonghi.github.io/speedreading-insights/membership.html",
    "replay_url": "https://vanthuonghi.github.io/speedreading-insights/workshop.html#replay",
}

# ─── EMAIL TEMPLATES ───

def email_1_confirm(reg):
    """Email 1: Xác nhận đăng ký — gửi ngay sau khi đăng ký"""
    return f"""
    <!DOCTYPE html>
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;padding:32px;">
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:2em;">📚</span>
        <h1 style="font-size:1.3em;color:#1a1a2e;">Xác nhận đăng ký Workshop</h1>
    </div>

    <p>Chào <strong>{reg['name']}</strong>,</p>
    <p>Cảm ơn bạn đã đăng ký workshop Speed Reading!</p>

    <div style="background:#fef3e7;border-left:4px solid #f59e0b;padding:16px;margin:20px 0;border-radius:0 8px 8px 0;">
        <p style="margin:0;"><strong>📅 Thông tin workshop:</strong></p>
        <p style="margin:4px 0;">⏰ 20:00 - 21:00 — <strong>{WORKSHOP['day']} tuần này</strong></p>
        <p style="margin:4px 0;">💻 Online qua Zoom</p>
        <p style="margin:4px 0;">🔗 Link Zoom: <a href="{WORKSHOP['zoom_link']}" style="color:#f59e0b;">{WORKSHOP['zoom_link']}</a></p>
    </div>

    <p><strong>📋 Chuẩn bị:</strong></p>
    <ul>
        <li>Một cuốn sách bất kỳ (chưa đọc hoặc đọc dở)</li>
        <li>Bút + giấy note</li>
        <li>Máy tính / điện thoại có Zoom</li>
    </ul>

    <p>✅ Mình sẽ gửi email nhắc nhở 1 tiếng trước giờ workshop.</p>
    <p>Nếu có thắc mắc, inbox Facebook <strong>{WORKSHOP['fb_page']}</strong> hoặc gọi <strong>{WORKSHOP['hotline']}</strong>.</p>

    <p style="margin-top:24px;">Hẹn gặp bạn tối Thứ 2! 🚀</p>
    <p><strong>Văn Hỉ</strong><br>Speed Reading Việt Nam</p>
    </div></body></html>
    """

def email_2_remind_1h(reg):
    """Email 2: Nhắc nhở 1 tiếng trước workshop"""
    return f"""
    <!DOCTYPE html>
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;padding:32px;">
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:2em;">⏰</span>
        <h1 style="font-size:1.3em;color:#1a1a2e;">Còn 1 tiếng nữa — Workshop bắt đầu!</h1>
    </div>

    <p>Chào <strong>{reg['name']}</strong>,</p>
    <p>Chỉ còn <strong>1 tiếng nữa</strong> là workshop bắt đầu! 🚀</p>

    <div style="background:#e8f5e9;border-left:4px solid #34d399;padding:16px;margin:20px 0;border-radius:0 8px 8px 0;">
        <p style="margin:0;"><strong>🔗 Link Zoom:</strong></p>
        <p style="margin:4px 0;"><a href="{WORKSHOP['zoom_link']}" style="color:#34d399;font-weight:600;">{WORKSHOP['zoom_link']}</a></p>
        <p style="margin:4px 0;">🆔 ID: {WORKSHOP['zoom_id']} | 🔑 Pass: {WORKSHOP['zoom_pass']}</p>
    </div>

    <p><strong>Trong 60 phút, bạn sẽ học:</strong></p>
    <ul>
        <li>👆 Kỹ thuật chỉ tay dẫn đường — tăng tốc ngay lập tức</li>
        <li>🔇 Cách loại bỏ đọc thầm</li>
        <li>📊 Đo tốc độ đọc thực tế</li>
        <li>🧠 Ghi nhớ chủ động — nhớ gấp 3 lần</li>
    </ul>

    <p>Mang theo một cuốn sách và tinh thần sẵn sàng thay đổi nhé! 📖</p>
    <p>Hẹn gặp bạn lúc 20:00!</p>

    <p><strong>Văn Hỉ</strong><br>Speed Reading Việt Nam</p>
    </div></body></html>
    """

def email_3_remind_10m(reg):
    """Email 3: Nhắc 10 phút trước — khẩn cấp"""
    return f"""
    <!DOCTYPE html>
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;padding:32px;">
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:2em;">🔔</span>
        <h1 style="font-size:1.3em;color:#1a1a2e;">Workshop bắt đầu sau 10 phút!</h1>
    </div>

    <p>Chào <strong>{reg['name']}</strong>,</p>
    <p>Workshop sắp bắt đầu — <strong>click ngay link bên dưới</strong> để vào Zoom! ⏰</p>

    <div style="text-align:center;margin:24px 0;">
        <a href="{WORKSHOP['zoom_link']}" 
           style="display:inline-block;padding:14px 32px;background:#f59e0b;color:#1a1a2e;
                  text-decoration:none;border-radius:10px;font-weight:700;font-size:1.05em;">
           🚀 Vào Zoom ngay
        </a>
    </div>

    <div style="background:#fff3e0;border-left:4px solid #f59e0b;padding:12px 16px;border-radius:0 8px 8px 0;">
        <p style="margin:0;font-size:.9em;">
            🔗 Link dự phòng: <a href="{WORKSHOP['zoom_link']}">{WORKSHOP['zoom_link']}</a><br>
            🆔 {WORKSHOP['zoom_id']} | 🔑 {WORKSHOP['zoom_pass']}
        </p>
    </div>

    <p style="margin-top:16px;">Nếu có trục trặc kỹ thuật, inbox ngay Facebook <strong>{WORKSHOP['fb_page']}</strong> hoặc gọi <strong>{WORKSHOP['hotline']}</strong>.</p>

    <p>Vào Zoom đi — mình đang chờ bạn! 🎯</p>
    <p><strong>Văn Hỉ</strong></p>
    </div></body></html>
    """

def email_4_thanks_replay(reg):
    """Email 4: Cảm ơn + link xem lại + tài liệu"""
    return f"""
    <!DOCTYPE html>
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;padding:32px;">
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:2em;">🎉</span>
        <h1 style="font-size:1.3em;color:#1a1a2e;">Cảm ơn bạn đã tham gia workshop!</h1>
    </div>

    <p>Chào <strong>{reg['name']}</strong>,</p>
    <p>Cảm ơn bạn đã dành 60 phút tối nay để học Speed Reading! Hy vọng bạn đã có những kỹ thuật hữu ích. 🚀</p>

    <div style="background:#fef3e7;border-left:4px solid #f59e0b;padding:16px;margin:20px 0;border-radius:0 8px 8px 0;">
        <p style="margin:0;"><strong>📹 Xem lại workshop:</strong></p>
        <p style="margin:4px 0;"><a href="{WORKSHOP['replay_url']}" style="color:#f59e0b;">{WORKSHOP['replay_url']}</a></p>
        <p style="margin:4px 0;font-size:.85em;color:#666;">(Link có hiệu lực 7 ngày)</p>
    </div>

    <p><strong>📚 Tài liệu tặng kèm:</strong></p>
    <ul>
        <li>Ebook "5 Kỹ Thuật Speed Reading Cơ Bản"</li>
        <li>Bảng đo tốc độ đọc (PDF)</li>
        <li>Template ghi chú thông minh</li>
    </ul>

    <p style="margin-top:16px;">👉 <strong>Bạn muốn đọc 1000+ từ/phút?</strong></p>
    <p>Mình có khoá Speed Reading Online 7 buổi Zoom — cam kết hoàn phí nếu không hài lòng.</p>
    <p>Người tham gia workshop được <strong>giảm thêm 200.000đ</strong> — chỉ còn <strong>780.000đ</strong> cho gói Cơ Bản.</p>

    <div style="text-align:center;margin:20px 0;">
        <a href="{WORKSHOP['membership_url']}" 
           style="display:inline-block;padding:12px 28px;background:#f59e0b;color:#1a1a2e;
                  text-decoration:none;border-radius:10px;font-weight:700;">
           🔥 Xem chi tiết khoá học
        </a>
    </div>

    <p>Có thắc mắc gì, inbox mình nhé! 💬</p>
    <p><strong>Văn Hỉ</strong><br>Speed Reading Việt Nam</p>
    </div></body></html>
    """

def email_5_upsell(reg):
    """Email 5: Upsell membership — gửi sáng hôm sau"""
    return f"""
    <!DOCTYPE html>
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;padding:32px;">
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:2em;">🔥</span>
        <h1 style="font-size:1.3em;color:#1a1a2e;">Bạn đã sẵn sàng đọc 1000+ từ/phút?</h1>
    </div>

    <p>Chào <strong>{reg['name']}</strong>,</p>
    <p>Tối qua bạn đã thấy: Speed Reading <strong>không phải ảo thuật</strong>. Chỉ là kỹ thuật đúng.</p>

    <p>Trong workshop, bạn học được những kỹ thuật đầu tiên. Nhưng để đạt <strong>1000+ từ/phút</strong>, bạn cần một lộ trình bài bản.</p>

    <div style="background:#fff3e0;border-left:4px solid #f59e0b;padding:16px;margin:20px 0;border-radius:0 8px 8px 0;">
        <p style="margin:0;"><strong>🎯 Khoá Speed Reading Online — 7 buổi Zoom</strong></p>
        <p style="margin:4px 0;">📚 Từ 300 → 1000+ từ/phút</p>
        <p style="margin:4px 0;">✅ Kèm cặp 1:1 qua Zalo</p>
        <p style="margin:4px 0;">🛡 Cam kết hoàn phí sau buổi 1</p>
    </div>

    <p><strong>🎁 Ưu đãi đặc biệt cho người tham gia workshop:</strong></p>
    <ul>
        <li>Gói Cơ Bản: <strong>780.000đ</strong> (giảm 200.000đ — còn 980.000đ)</li>
        <li>Gói Cao Cấp: <strong>1.780.000đ</strong> (giảm 200.000đ — còn 1.980.000đ)</li>
        <li>➕ Tặng thêm buổi Zoom 1:1 trị giá 500.000đ</li>
    </ul>

    <div style="text-align:center;margin:20px 0;">
        <a href="{WORKSHOP['membership_url']}?utm_source=workshop&utm_medium=email&utm_campaign=upsell" 
           style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#f59e0b,#d97706);color:#1a1a2e;
                  text-decoration:none;border-radius:10px;font-weight:700;font-size:1.05em;">
           🚀 Đăng ký ngay — tiết kiệm 200k
        </a>
    </div>

    <p style="font-size:.85em;color:#666;">* Ưu đãi có hiệu lực trong 7 ngày sau workshop.</p>
    <p>Inbox mình nếu bạn cần tư vấn thêm! 💬</p>

    <p><strong>Văn Hỉ</strong><br>Speed Reading Việt Nam</p>
    <p style="font-size:.8em;color:#999;">
        📩 Bạn nhận được email này vì đã đăng ký workshop Speed Reading.<br>
        Nếu không muốn nhận thêm email, <a href="#" style="color:#999;">bấm vào đây để huỷ</a>.
    </p>
    </div></body></html>
    """

# ─── EMAIL ENGINE ───

def send_email(to_email, to_name, subject, html_content):
    """Gửi 1 email qua SMTP"""
    if not SMTP_CONFIG["user"] or not SMTP_CONFIG["password"]:
        print(f"   ⚠️ SMTP chưa cấu hình. Bỏ qua gửi đến {to_email}")
        print(f"   📧 Subject: {subject}")
        print(f"   📝 Nội dung: {html_content[:100]}...")
        return {"status": "skipped", "reason": "SMTP not configured"}

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls(context=context)
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        print(f"   ✅ Đã gửi đến {to_email}")
        return {"status": "sent"}
    except Exception as e:
        print(f"   ❌ Lỗi gửi đến {to_email}: {e}")
        return {"status": "failed", "error": str(e)}


def load_registrations():
    """Đọc danh sách đăng ký từ file JSON"""
    if not REGS_FILE.exists():
        return []
    try:
        return json.loads(REGS_FILE.read_text())
    except:
        return []


def load_sent():
    """Đọc lịch sử email đã gửi"""
    if not SENT_FILE.exists():
        return {}
    try:
        return json.loads(SENT_FILE.read_text())
    except:
        return {}


def save_sent(sent):
    """Lưu lịch sử email đã gửi"""
    SENT_FILE.write_text(json.dumps(sent, ensure_ascii=False, indent=2))


def get_email_step(now):
    """
    Xác định bước email cần gửi dựa vào thời gian hiện tại
    Trả về: (step_id, subject_generator, email_generator)
    """
    weekday = now.weekday()  # 0=Monday
    hour = now.hour
    minute = now.minute

    # Thứ 2
    if weekday == 0:
        # 06:30 → Gửi email xác nhận (cho người đăng ký trong vòng 7 ngày qua chưa nhận)
        if hour == 6 and 25 <= minute <= 35:
            return ("confirm", "📚 Xác nhận đăng ký Workshop Speed Reading", email_1_confirm)
        # 18:00 → Nhắc 1h trước
        if hour == 18 and 0 <= minute <= 5:
            return ("remind_1h", "⏰ Còn 1 tiếng — Workshop Speed Reading sắp bắt đầu!", email_2_remind_1h)
        # 19:50 → Nhắc 10 phút
        if hour == 19 and 48 <= minute <= 55:
            return ("remind_10m", "🔔 Workshop bắt đầu sau 10 phút — Vào Zoom ngay!", email_3_remind_10m)
        # 21:30 → Cảm ơn + replay
        if hour == 21 and 25 <= minute <= 35:
            return ("thanks_replay", "🎉 Cảm ơn bạn — Link xem lại workshop + tài liệu", email_4_thanks_replay)

    # Thứ 3 — 08:00 → Upsell
    if weekday == 1 and hour == 8 and 0 <= minute <= 5:
        return ("upsell", "🔥 Ưu đãi đặc biệt — 200.000đ cho người tham gia workshop", email_5_upsell)

    return None


def process_workshop_emails(now=None, force_step=None, test_email=None):
    """Xử lý gửi email workshop"""
    if now is None:
        now = datetime.now()

    print(f"📧 Workshop Email Engine — {now.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # Xác định bước
    if force_step:
        step_info = force_step
    else:
        step_info = get_email_step(now)

    if not step_info:
        print("   📭 Không có email nào cần gửi vào thời điểm này.")
        return

    step_id, subject_template, email_fn = step_info
    print(f"   📋 Bước: {step_id}")

    # Load data
    registrations = load_registrations()
    sent = load_sent()

    if test_email:
        # Chế độ test
        test_reg = {"name": "Test User", "email": test_email, "phone": "0900000000"}
        html = email_fn(test_reg)
        send_email(test_email, test_reg['name'], subject_template, html)
        print(f"\n   🧪 Đã gửi email test đến {test_email}")
        return

    # Lọc người cần gửi
    this_monday = now - timedelta(days=now.weekday())
    this_monday = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    to_send = []
    for reg in registrations:
        # Chỉ gửi cho người đăng ký trong tuần này (hoặc chưa gửi bước này)
        reg_time = datetime.fromisoformat(reg.get('registered_at', now.isoformat()))
        if reg_time < this_monday - timedelta(days=7):
            continue  # Quá cũ, bỏ qua

        # Kiểm tra đã gửi chưa
        email_key = f"{reg['email']}_{step_id}"
        if email_key in sent:
            continue

        to_send.append(reg)

    if not to_send:
        print(f"   ✅ Tất cả đã được gửi. Không có email mới.")
        return

    print(f"   📨 Số lượng cần gửi: {len(to_send)}")

    for reg in to_send:
        html = email_fn(reg)
        result = send_email(reg['email'], reg['name'], subject_template, html)

        # Ghi nhận đã gửi
        email_key = f"{reg['email']}_{step_id}"
        sent[email_key] = {
            "step": step_id,
            "email": reg['email'],
            "sent_at": now.isoformat(),
            "status": result.get("status"),
        }
        save_sent(sent)
        time.sleep(1)  # Tránh spam

    print(f"\n   ✅ Hoàn tất! Đã gửi {len(to_send)} email.")


def add_registration_manually(name, email, phone, source="Facebook", speed="200-300"):
    """Thêm đăng ký thủ công — dùng khi có người đăng ký qua form"""
    regs = load_registrations()
    reg = {
        "name": name,
        "email": email,
        "phone": phone,
        "source": source,
        "speed": speed,
        "registered_at": datetime.now().isoformat(),
        "workshop_date": (datetime.now() + timedelta(days=(7 - datetime.now().weekday()) % 7 or 7)).isoformat(),
    }
    # Kiểm tra trùng
    for r in regs:
        if r['email'] == email:
            print(f"   ⚠️ Email {email} đã đăng ký trước đó.")
            return False

    regs.append(reg)
    REGS_FILE.write_text(json.dumps(regs, ensure_ascii=False, indent=2))
    # Gửi email xác nhận ngay
    html = email_1_confirm(reg)
    send_email(email, name, "📚 Xác nhận đăng ký Workshop Speed Reading", html)
    print(f"   ✅ Đã thêm {name} ({email}) và gửi email xác nhận.")
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Workshop Email System')
    parser.add_argument('--test', type=str, help='Gửi email test đến địa chỉ')
    parser.add_argument('--force', type=str, choices=['confirm','remind_1h','remind_10m','thanks_replay','upsell'],
                       help='Force gửi 1 bước cụ thể')
    parser.add_argument('--add', nargs=3, metavar=('NAME','EMAIL','PHONE'),
                       help='Thêm đăng ký thủ công')
    parser.add_argument('--list', action='store_true', help='Xem danh sách đăng ký')
    args = parser.parse_args()

    if args.test:
        now = datetime.now()
        # Gửi tất cả 5 email test
        test_reg = {"name": "Test User", "email": args.test, "phone": "0900000000"}
        steps = [
            ("confirm", email_1_confirm, "📚 Xác nhận đăng ký Workshop Speed Reading"),
            ("remind_1h", email_2_remind_1h, "⏰ Còn 1 tiếng — Workshop Speed Reading sắp bắt đầu!"),
            ("remind_10m", email_3_remind_10m, "🔔 Workshop bắt đầu sau 10 phút — Vào Zoom ngay!"),
            ("thanks_replay", email_4_thanks_replay, "🎉 Cảm ơn bạn — Link xem lại workshop + tài liệu"),
            ("upsell", email_5_upsell, "🔥 Ưu đãi đặc biệt — 200.000đ cho người tham gia workshop"),
        ]
        for sid, fn, subj in steps:
            html = fn(test_reg)
            send_email(args.test, "Test User", subj, html)
            time.sleep(2)
        print(f"\n🧪 Đã gửi {len(steps)} email test đến {args.test}")
    elif args.add:
        add_registration_manually(*args.add)
    elif args.list:
        regs = load_registrations()
        print(f"📋 Danh sách đăng ký ({len(regs)} người):")
        for i, r in enumerate(regs, 1):
            print(f"   {i}. {r['name']} — {r['email']} — {r.get('registered_at','')[:10]}")
    elif args.force:
        process_workshop_emails(force_step=(args.force, "", lambda r: ""))  # Placeholder
        # Force mode sẽ được xử lý riêng
        regs = load_registrations()
        sent = load_sent()
        step_map = {
            'confirm': ('confirm', email_1_confirm, "📚 Xác nhận đăng ký Workshop Speed Reading"),
            'remind_1h': ('remind_1h', email_2_remind_1h, "⏰ Còn 1 tiếng — Workshop sắp bắt đầu!"),
            'remind_10m': ('remind_10m', email_3_remind_10m, "🔔 Workshop bắt đầu sau 10 phút!"),
            'thanks_replay': ('thanks_replay', email_4_thanks_replay, "🎉 Cảm ơn bạn — Link xem lại workshop"),
            'upsell': ('upsell', email_5_upsell, "🔥 Ưu đãi đặc biệt — 200.000đ cho người tham gia"),
        }
        sid, fn, subj = step_map[args.force]
        count = 0
        for reg in regs:
            key = f"{reg['email']}_{sid}"
            if key not in sent:
                html = fn(reg)
                send_email(reg['email'], reg['name'], subj, html)
                sent[key] = {"step": sid, "email": reg['email'], "sent_at": datetime.now().isoformat(), "status": "sent"}
                count += 1
                time.sleep(1)
        save_sent(sent)
        print(f"\n✅ Force gửi {count} email bước '{args.force}'")
    else:
        process_workshop_emails()
