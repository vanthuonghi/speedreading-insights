#!/usr/bin/env python3
"""
Deploy Speed Reading Insights lên GitHub Pages
===============================================
Cách dùng:
  python3 deploy.py            # Push toàn bộ website lên GitHub
  python3 deploy.py --setup    # Lần đầu: tạo repo + cấu hình GitHub Pages
"""

import os
import sys
import json
import subprocess
from pathlib import Path

BASE_DIR = Path.home() / 'speedreading-research'
REPO_NAME = 'speedreading-insights'


def run_cmd(cmd, cwd=None):
    """Chạy lệnh và in ra output"""
    result = subprocess.run(cmd, shell=True, cwd=cwd or BASE_DIR, 
                           capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ {result.stderr}")
    return result.stdout.strip()


def setup_repo():
    """Lần đầu: tạo repo GitHub"""
    print("🚀 Thiết lập GitHub Pages...\n")
    
    # Kiểm tra GitHub CLI
    gh_check = run_cmd('gh auth status 2>&1')
    if 'not logged' in gh_check.lower():
        print("❌ Bạn cần đăng nhập GitHub trước!")
        print("\n📌 Chạy lệnh sau và làm theo hướng dẫn:")
        print("  gh auth login")
        print("\nSau đó chạy lại: python3 deploy.py --setup")
        return False
    
    # Tạo repo trên GitHub
    print(f"📦 Tạo repository: {REPO_NAME}...")
    result = run_cmd(f'gh repo create {REPO_NAME} --public --description "Speed Reading Insights - Nghiên cứu & Học tập mỗi ngày" --homepage "https://$(gh api user --jq .login).github.io/{REPO_NAME}"')
    print(f"✅ {result}")
    
    # Init Git
    run_cmd('git init')
    run_cmd(f'git remote add origin https://github.com/$(gh api user --jq .login)/{REPO_NAME}.git')
    
    # Bật GitHub Pages
    run_cmd(f'gh api repos/$(gh api user --jq .login)/{REPO_NAME}/pages -X POST -f source.branch=main -f source.path=/ 2>/dev/null || echo "Pages đã bật"')
    
    print("✅ Thiết lập hoàn tất!")
    return True


def deploy():
    """Push website lên GitHub Pages"""
    print("🚀 Deploy Speed Reading Insights...\n")
    
    # Kiểm tra Git
    if not (BASE_DIR / '.git').exists():
        print("❌ Chưa có Git repo. Chạy: python3 deploy.py --setup")
        return
    
    # Kiểm tra file
    if not (BASE_DIR / 'index.html').exists():
        print("❌ Thiếu index.html")
        return
    
    print("📦 Chuẩn bị deploy...")
    
    # Copy assets
    run_cmd('mkdir -p assets')
    
    # Git add & commit
    run_cmd('git add -A')
    run_cmd('git commit -m "Cập nhật báo cáo $(date +%Y-%m-%d)"')
    
    # Push
    print("📤 Push lên GitHub...")
    result = run_cmd('git push origin main 2>&1')
    print(result)
    
    # Lấy URL
    username = run_cmd('gh api user --jq .login 2>/dev/null')
    if username:
        url = f"https://{username}.github.io/{REPO_NAME}/"
        print(f"\n✅ Deploy thành công!")
        print(f"🔗 {url}")
        return url
    
    print("✅ Deploy hoàn tất!")
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Deploy Speed Reading Insights')
    parser.add_argument('--setup', action='store_true', help='Lần đầu: tạo repo')
    args = parser.parse_args()
    
    if args.setup:
        setup_repo()
    else:
        deploy()


if __name__ == '__main__':
    main()