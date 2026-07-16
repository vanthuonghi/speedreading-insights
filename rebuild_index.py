#!/usr/bin/env python3
"""Rebuild ai_videos_index.json từ các file HTML đã có"""
import json, re
from pathlib import Path

BASE = Path.home() / 'speedreading-research'
VIDEOS_DIR = BASE / 'ai-videos-items'
INDEX = BASE / 'ai_videos_index.json'

entries = []
for f in sorted(VIDEOS_DIR.glob('*.html')):
    html = f.read_text(encoding='utf-8')
    title = ''
    m = re.search(r'<h1 class="video-title">(.+?)</h1>', html)
    if m: title = m.group(1)
    
    channel = ''
    m = re.search(r'📺 (.+?)</span>', html)
    if m: channel = m.group(1)
    
    duration = ''
    m = re.search(r'⏱ (.+?)(?:\s|•|</)', html)
    if m: duration = m.group(1).strip()
    
    preview = ''
    m = re.search(r'<div class="video-summary">\s*<p>(.+?)</p>', html, re.DOTALL)
    if m: preview = m.group(1).strip()[:120]
    
    date_match = re.search(r'\d+ tháng (\d+/\d+)', html)
    date_str = f'2026-07-16'
    
    entries.append({
        'title': title,
        'filename': f.name,
        'date': date_str,
        'channel': channel,
        'duration': duration,
        'preview': preview,
    })

INDEX.write_text(json.dumps(entries, ensure_ascii=False, indent=2))
print(f"✅ Rebuilt ai_videos_index.json: {len(entries)} videos")