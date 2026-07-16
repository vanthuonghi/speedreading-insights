#!/usr/bin/env python3
"""Chuyển đổi các bài nghiên cứu cũ thành individual articles"""
import json, subprocess, sys
from pathlib import Path

BASE = Path.home() / 'speedreading-research'
ARTICLES = json.loads(Path('/tmp/_articles_batch.json').read_text(encoding='utf-8'))

for article in ARTICLES:
    tmp = Path('/tmp/_single_article.json')
    tmp.write_text(json.dumps(article, ensure_ascii=False), encoding='utf-8')
    
    r = subprocess.run(
        [sys.executable, str(BASE/'generate_article.py'), '--file', '/tmp/_single_article.json'],
        capture_output=True, text=True, timeout=30
    )
    title = article['title'][:50]
    if r.returncode == 0:
        print(f"✅ {title}")
    else:
        print(f"❌ {title}: {r.stderr[:150]}")

print(f"\n🎉 Hoàn tất! {len(ARTICLES)} articles.")