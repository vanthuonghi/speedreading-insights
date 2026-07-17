#!/usr/bin/env python3
"""
Daily NotebookLM Pipeline: 3 articles → 3 notebooks → deploy
==============================================================
Cách dùng:  python3 daily_notebook_pipeline.py
"""
import subprocess, sys
from pathlib import Path

BASE = Path.home() / 'speedreading-research'

def run(cmd):
    r = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=True, text=True, timeout=300)
    if r.stdout.strip(): print(r.stdout.strip())
    if r.stderr.strip(): print(f"⚠️ {r.stderr.strip()[:200]}")
    return r.returncode

def main():
    date_str = __import__('datetime').datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 NotebookLM Daily — {date_str}")
    
    # Step 1: Generate 3 notebooks from random articles
    print("📚 Bước 1: Tạo 3 Notebook từ bài nghiên cứu...")
    ret = run(f"python3 notebooklm_pipeline.py --random 3")
    if ret != 0:
        print("⚠️ Có lỗi khi tạo notebook")
    
    # Step 2: Deploy
    print("\n🚀 Bước 2: Deploy...")
    run("python3 update_website.py")
    
    print(f"\n🔗 https://vanthuonghi.github.io/speedreading-insights/")

if __name__ == '__main__':
    main()