#!/usr/bin/env python3
"""Post a Facebook Page post with an optional local image."""
import sys
import requests
import json
from pathlib import Path

if len(sys.argv) < 5:
    print("Usage: post_facebook.py <page_id> <access_token> <image_path> <message>")
    sys.exit(1)

PAGE_ID = sys.argv[1]
ACCESS_TOKEN = sys.argv[2]
IMAGE_PATH = sys.argv[3]
MESSAGE = sys.argv[4]

media_id = None
if IMAGE_PATH and Path(IMAGE_PATH).exists():
    with open(IMAGE_PATH, "rb") as img:
        upload = requests.post(
            f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos",
            data={"access_token": ACCESS_TOKEN, "published": "false"},
            files={"source": ("image.jpg", img, "image/jpeg")},
            timeout=60,
        )
    media_id = upload.json().get("id")
    if not media_id:
        print(f"UPLOAD_IMAGE_FAILED: {upload.text}")

post_data = {"message": MESSAGE, "access_token": ACCESS_TOKEN}
if media_id:
    post_data["attached_media[0]"] = json.dumps({"media_fbid": media_id})

resp = requests.post(
    f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed",
    data=post_data,
    timeout=60,
)
print(resp.status_code)
print(resp.text)
