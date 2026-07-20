#!/usr/bin/env python3
"""
Cập nhật trang Agent hàng ngày lúc 6h sáng
=============================================
Cách dùng:  python3 daily_agent_update.py
"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path.home() / 'speedreading-research'
AGENT_JSON = BASE / 'agent.json'
ARTICLES_JSON = BASE / 'articles.json'
SCRIPTS_JSON = BASE / 'scripts.json'
VIDEOS_INDEX = BASE / 'ai_videos_index.json'
NOTEBOOKS_INDEX = BASE / 'notebooks_index.json'
ADS_INDEX = BASE / 'ads_items_index.json'

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🤖 Cập nhật Agent — {today}")
    
    # Đọc dữ liệu hiện tại
    agent = json.loads(AGENT_JSON.read_text(encoding='utf-8'))
    articles = json.loads(ARTICLES_JSON.read_text(encoding='utf-8')) if ARTICLES_JSON.exists() else []
    scripts = json.loads(SCRIPTS_JSON.read_text(encoding='utf-8')) if SCRIPTS_JSON.exists() else []
    videos = json.loads(VIDEOS_INDEX.read_text(encoding='utf-8')) if VIDEOS_INDEX.exists() else []
    notebooks = json.loads(NOTEBOOKS_INDEX.read_text(encoding='utf-8')) if NOTEBOOKS_INDEX.exists() else []
    ads = json.loads(ADS_INDEX.read_text(encoding='utf-8')) if ADS_INDEX.exists() else []
    
    # Cập nhật ngày
    agent['updated'] = today
    
    # Cập nhật stats
    if 'stats' not in agent:
        agent['stats'] = {}
    agent['stats']['articles'] = len(articles)
    agent['stats']['scripts'] = len(scripts)
    agent['stats']['ai_videos'] = len(videos)
    agent['stats']['notebooks'] = len(notebooks)
    agent['stats']['ads_variants'] = len(ads)
    
    # Thêm log entry hôm nay (nếu chưa có)
    today_log = f"Cập nhật Agent ngày {today} — 📚{len(articles)} bài • 🎬{len(scripts)} kịch bản • 🤖{len(videos)} videos • 📓{len(notebooks)} notebooks • 📢{len(ads)} ads"
    existing_titles = [l['text'][:30] for l in agent.get('log', [])]
    if today_log[:30] not in existing_titles:
        log_entry = {"tag": "📊", "type": "deploy", "text": today_log}
        agent.setdefault('log', []).append(log_entry)
        # Giữ tối đa 30 log entries
        if len(agent['log']) > 30:
            agent['log'] = agent['log'][-30:]
    
    AGENT_JSON.write_text(json.dumps(agent, ensure_ascii=False, indent=2))
    print(f"✅ agent.json cập nhật: {len(articles)} articles, {len(scripts)} scripts, {len(videos)} videos, {len(notebooks)} notebooks, {len(ads)} ads")
    
    # Không cần deploy — agent.html đọc từ agent.json trực tiếp
    print(f"🔗 https://vanthuonghi.github.io/speedreading-insights/agent.html")

if __name__ == '__main__':
    main()