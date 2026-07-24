#!/usr/bin/env python3
"""Generate a Facebook post from OpenRouter free model and print the content."""
import sys
import requests
import json
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: generate_openrouter_post.py <model> <topic>")
    sys.exit(1)

MODEL = sys.argv[1]
TOPIC = sys.argv[2]
API_KEY = Path("/home/vider/facebook-auto/config.sh").read_text().split('OPENROUTER_API_KEY="')[1].split('"')[0]
URL = "https://openrouter.ai/api/v1/chat/completions"

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "Ban la copywriter Facebook cua Speed Reading Vietnam. Viet van noi, khong markdown, khong loi chinh ta. Ket thuc bang CTA dang ky khoa Speed Reading."},
        {"role": "user", "content": f"Viet bai Facebook loi cuoi ve: {TOPIC}. Ky ten Huy. Co CTA ro rang."}
    ],
    "temperature": 0.7,
    "max_tokens": 512,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://speedreading-insights.vercel.app",
    "X-Title": "Speed Reading VN Content Gen",
}

resp = requests.post(URL, headers=headers, json=payload, timeout=90)
if resp.status_code != 200:
    print(f"ERROR: {resp.status_code} {resp.text}")
    sys.exit(2)

content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
print(content)
