#!/usr/bin/env python3
"""
Tìm 10 video YouTube mới nhất về AI Tools, AI Agent, Công nghệ mới
===============================================================
Cần: yt-dlp (pip install yt-dlp)
Output: JSON array ra stdout
"""
import json, subprocess, sys
from datetime import datetime, timezone

# Các từ khoá tìm kiếm — luân phiên để đa dạng
SEARCH_QUERIES = [
    "new AI tools 2026",
    "AI agent latest",
    "best AI productivity tools",
    "AI news this week",
    "new AI technology 2026",
    "AI workflow automation",
    "AI content creation tools",
    "AI programming tools",
    "machine learning news",
    "AI research breakthroughs",
]

# Kênh YouTube uy tín về AI (ưu tiên)
PREFERRED_CHANNELS = [
    "AI Explained",
    "Fireship",
    "Two Minute Papers",
    "Matt Wolfe",
    "The AI Advantage",
    "AI Foundations",
    "Prompt Engineering",
    "WorldofAI",
    "Nicholas Renotte",
    "Sam Witteveen",
    "Yannic Kilcher",
    "Andrej Karpathy",
]

def search_youtube(query, max_results=10):
    """Tìm video YouTube bằng yt-dlp"""
    try:
        cmd = [
            "yt-dlp",
            f"ytsearch{max_results}:{query}",
            "--dump-json",
            "--no-warnings",
            "--flat-playlist",
            "--extractor-args", "youtube:player_client=web",
            "--match-filter", "duration < 1800",  # Dưới 30 phút
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                videos.append({
                    "title": data.get("title", ""),
                    "url": f"https://youtube.com/watch?v={data.get('id', '')}",
                    "video_id": data.get("id", ""),
                    "channel": data.get("channel", data.get("uploader", "")),
                    "duration": data.get("duration", 0),
                    "view_count": data.get("view_count", 0),
                    "upload_date": data.get("upload_date", ""),
                    "description": data.get("description", "")[:300],
                    "query": query,
                })
            except:
                continue
        return videos
    except Exception as e:
        print(f"⚠️ Lỗi tìm kiếm '{query}': {e}", file=sys.stderr)
        return []

def deduplicate(videos):
    """Loại bỏ video trùng lặp"""
    seen = set()
    unique = []
    for v in videos:
        if v["video_id"] and v["video_id"] not in seen:
            seen.add(v["video_id"])
            unique.append(v)
    return unique

def format_duration(seconds):
    """Định dạng thời lượng video"""
    if not seconds:
        return ""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m}m"
    return f"{m}m{s}s"

def format_date(date_str):
    """Định dạng ngày từ YYYYMMDD"""
    if not date_str or len(date_str) != 8:
        return ""
    try:
        d = datetime.strptime(date_str, "%Y%m%d")
        return d.strftime("%d/%m/%Y")
    except:
        return date_str

def main():
    print("🔍 Đang tìm video AI mới nhất...", file=sys.stderr)
    
    all_videos = []
    # Tìm với 3 query đầu tiên
    for query in SEARCH_QUERIES[:3]:
        print(f"   📡 Từ khoá: {query}", file=sys.stderr)
        videos = search_youtube(query, max_results=5)
        all_videos.extend(videos)
    
    # Deduplicate và lấy 10 video
    unique = deduplicate(all_videos)
    top10 = unique[:10]
    
    print(f"   ✅ Tìm thấy {len(top10)} video (sau khi loại trùng)", file=sys.stderr)
    
    # Format output
    output = []
    for v in top10:
        output.append({
            "title": v["title"],
            "url": v["url"],
            "channel": v["channel"],
            "duration": format_duration(v.get("duration")),
            "views": v.get("view_count", 0),
            "date": format_date(v.get("upload_date", "")),
            "summary": v.get("description", "")[:200],
            "category": "AI & Công nghệ",
        })
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()