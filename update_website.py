#!/usr/bin/env python3
"""
Helper: Cập nhật nhanh website Speed Reading Insights
Cách dùng:  python3 update_website.py
"""
import subprocess, sys
from pathlib import Path

BASE = Path.home() / 'speedreading-research'

def run(cmd, cwd=BASE):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0 and r.stderr.strip():
        print(f"⚠️ {r.stderr.strip()[:200]}")
    return r.stdout.strip()

def main():
    print("🚀 Cập nhật website Speed Reading Insights...")
    
    # Kiểm tra có thay đổi không
    status = run("git status --short")
    if not status:
        print("   📭 Không có thay đổi nào. Website đã up-to-date.")
    
    run("git add -A")
    run(f'git commit -m "Cập nhật {run("date +%Y-%m-%d")}"')
    
    print("   📤 Push lên GitHub...")
    result = run("git push origin main")
    print(f"   ✅ {result}")
    print()
    print("🔗 https://vanthuonghi.github.io/speedreading-insights/")

if __name__ == '__main__':
    main()
