#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webinar_webhook_receiver.py — Nhan form dang ky tu webinar-free.html
Nhan POST (form-data hoac JSON) -> ghi webinar_registrations.json
-> trigger email xac nhan (webinar_email.add_registration + send email 1)

Chay: python3 webinar_webhook_receiver.py [port]
Mac dinh port 5000. Deploy sau nginx/caddy hoac chay nen.
"""
import json, os, sys, urllib.parse, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE = Path(__file__).parent
REGS_FILE = BASE / "webinar_registrations.json"

# Import engine (cung thu muc)
sys.path.insert(0, str(BASE))
import webinar_email as engine

def parse_body(handler):
    length = int(handler.headers.get("Content-Length", 0) or 0)
    raw = handler.rfile.read(length) if length else b""
    ctype = handler.headers.get("Content-Type", "")
    data = {}
    if "application/json" in ctype:
        try:
            data = json.loads(raw.decode("utf-8"))
        except:
            data = {}
    else:
        # form-urlencoded hoac multipart (co ban)
        parsed = urllib.parse.parse_qs(raw.decode("utf-8", "ignore"))
        for k, v in parsed.items():
            data[k] = v[0] if v else ""
    return data

def handle_registration(data):
    name = (data.get("name") or data.get("fullname") or "anh chi").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or data.get("sdt") or "").strip()
    source = (data.get("source") or "webinar-free")
    if not email or "@" not in email:
        return {"status": "error", "msg": "thieu email"}, 400
    # Ghi + trigger email 1
    added = engine.add_registration(name, email, phone, source=source)
    if added:
        # Gui email xac nhan ngay (step confirm)
        wb = engine.next_webinar_date()
        res = engine.send_email(email, name, "📚 Xac nhan dang ky Webinar Mien Phi + Qua tang",
                                     engine.email_1_confirm(name, wb))
        return {"status": "ok", "email_sent": res.get("status", "skip")}, 200
    return {"status": "exists"}, 200

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self._cors()
        self.end_headers()
        self.wfile.write("Webinar webhook receiver OK".encode("utf-8"))

    def do_POST(self):
        data = {}
        try:
            data = parse_body(self)
            result, code = handle_registration(data)
        except Exception as e:
            result, code = {"status": "error", "msg": str(e)}, 500
        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.end_headers()
        self.wfile.write(body)
        print(f"[{datetime.datetime.now():%H:%M:%S}] POST {data.get('email','?')} -> {result['status']}")

    def log_message(self, format, *args):
        pass  # tat log mac dinh

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    os.chdir(BASE)
    srv = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🚀 Webinar webhook receiver dang chay tai http://0.0.0.0:{port}/")
    print(f"   Form webinar-free.html POST ve day. Data: {REGS_FILE}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dung.")
