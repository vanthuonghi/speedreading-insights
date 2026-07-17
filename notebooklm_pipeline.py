#!/usr/bin/env python3
"""
NotebookLM Pipeline: Research → Presentation → Script → Visual
=============================================================
Mô phỏng NotebookLM: lấy bài nghiên cứu, tạo bản trình bày có cấu trúc,
chuyển thành lời thoại video, và tạo hình tổng hợp thông tin.

Cách dùng:
  python3 notebooklm_pipeline.py --article "articles/2026-07-16-...html"
  python3 notebooklm_pipeline.py --random 3   # Xử lý 3 bài ngẫu nhiên
"""
import json, re, sys, os, requests
from pathlib import Path
from datetime import datetime

BASE = Path.home() / 'speedreading-research'
NOTEBOOKS_DIR = BASE / 'notebooks'
NOTEBOOKS_JSON = BASE / 'notebooks_index.json'
ARTICLES_DIR = BASE / 'articles'

# Đọc OpenRouter API key
def get_api_key():
    env_path = Path.home() / '.hermes' / '.env'
    if env_path.exists():
        for line in env_path.read_text().split('\n'):
            if line.startswith('OPENROUTER_API_KEY='):
                return line.split('=', 1)[1].strip()
    return ''

API_KEY = get_api_key()

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[đ]', 'd', s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s)
    s = s.strip('-')
    words = s.split('-')
    if len(words) > 12: words = words[:12]
    return '-'.join(words)


def extract_article_content(html_path):
    """Trích xuất nội dung từ file HTML bài nghiên cứu"""
    html = Path(html_path).read_text(encoding='utf-8')
    title = ''
    m = re.search(r'<h1[^>]*class="article-title"[^>]*>(.+?)</h1>', html)
    if m: title = m.group(1)
    
    content = ''
    m = re.search(r'<div class="article-content">(.+?)</div>\s*<div class="apply-box">', html, re.DOTALL)
    if m:
        content = m.group(1)
        content = re.sub(r'<p>', '', content)
        content = re.sub(r'</p>', '\n\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = content.strip()
    
    apply = ''
    m = re.search(r'<div class="label">💡 Ứng dụng cho Speed Reading</div>\s*<p>(.+?)</p>', html, re.DOTALL)
    if m: apply = m.group(1)
    
    source = ''
    m = re.search(r'<span>📖 (.+?)</span>', html)
    if m: source = m.group(1)
    
    return {'title': title, 'content': content, 'apply': apply, 'source': source}


def call_llm(prompt, system="Bạn là NotebookLM AI — chuyên gia phân tích và tổng hợp thông tin học thuật."):
    """Gọi OpenRouter LLM để xử lý"""
    if not API_KEY:
        return None
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek/deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 3000,
            },
            timeout=90,
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"   ⚠️ LLM error: {e}")
    return None


def generate_notebook(article):
    """Tạo NotebookLM-style presentation từ bài nghiên cứu"""
    prompt = f"""Bạn là NotebookLM. Hãy phân tích bài nghiên cứu sau và tạo một "Notebook" có cấu trúc gồm các phần:

TIÊU ĐỀ: {article['title']}
NGUỒN: {article['source']}
NỘI DUNG:
{article['content']}
ỨNG DỤNG: {article['apply']}

Hãy tạo Notebook với cấu trúc JSON sau (chỉ trả về JSON, không markdown):
{{
    "summary": "Tóm tắt ngắn gọn bài nghiên cứu (2-3 câu)",
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "key_quotes": ["Quote/phát biểu quan trọng 1", "Quote 2"],
    "data_points": ["Số liệu đáng chú ý 1", "Số liệu 2"],
    "themes": ["Chủ đề chính 1", "Chủ đề 2"],
    "visual_concept": "Mô tả ý tưởng cho hình tổng hợp thông tin (infographic/visual)",
    "presentation_outline": [
        "Phần 1: Mở đầu - ...",
        "Phần 2: Nội dung chính - ...",
        "Phần 3: Ứng dụng thực tế - ...",
        "Phần 4: Kết luận - ..."
    ],
    "video_script": "Lời thoại video 45-60 giây, tự nhiên, gần gũi, có emoji. Mở đầu hấp dẫn → nội dung chính → CTA. Không link.",
    "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3"]
}}
"""
    result = call_llm(prompt)
    if result:
        try:
            # Clean markdown
            result = re.sub(r'^```(?:json)?\s*', '', result)
            result = re.sub(r'\s*```$', '', result)
            return json.loads(result)
        except:
            # Try to extract JSON from the text
            m = re.search(r'\{.*\}', result, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except:
                    pass
            return {"error": "Failed to parse", "raw": result[:200]}
    return None


def generate_infographic_svg(notebook, article_title):
    """Tạo SVG infographic từ notebook data"""
    insights = notebook.get('key_insights', [])
    data_points = notebook.get('data_points', [])
    themes = notebook.get('themes', [])
    summary = notebook.get('summary', '')
    
    # Build SVG
    insights_html = ''.join(f'<text x="40" y="{130 + i*35}" fill="#e0e0f0" font-size="14" font-family="Inter">{insight[:60]}</text>'
                           for i, insight in enumerate(insights[:3]))
    data_html = ''.join(f'<text x="40" y="{130 + i*35}" fill="#fbbf24" font-size="14" font-family="Inter">{dp[:60]}</text>'
                       for i, dp in enumerate(data_points[:3]))
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <rect width="800" height="600" rx="16" fill="#0f0f23"/>
  <rect x="0" y="0" width="800" height="4" fill="url(#g)"/>
  <defs>
    <linearGradient id="g" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#a855f7"/>
    </linearGradient>
  </defs>
  <text x="40" y="45" fill="#e4e4f0" font-size="20" font-weight="700" font-family="Inter">📓 NotebookLM</text>
  <text x="40" y="75" fill="#8b8ba7" font-size="12" font-family="Inter">Speed Reading Insights • {datetime.now().strftime("%d/%m/%Y")}</text>
  <text x="40" y="105" fill="#e4e4f0" font-size="16" font-weight="600" font-family="Inter">{article_title[:70]}</text>
  
  <rect x="40" y="130" width="340" height="200" rx="12" fill="rgba(52,211,153,0.04)" stroke="rgba(52,211,153,0.12)" stroke-width="1"/>
  <text x="55" y="155" fill="#34d399" font-size="13" font-weight="600" font-family="Inter">💡 Key Insights</text>
  {insights_html}
  
  <rect x="420" y="130" width="340" height="200" rx="12" fill="rgba(251,191,36,0.04)" stroke="rgba(251,191,36,0.12)" stroke-width="1"/>
  <text x="435" y="155" fill="#fbbf24" font-size="13" font-weight="600" font-family="Inter">📊 Data Points</text>
  {data_html}
  
  <rect x="40" y="350" width="720" height="100" rx="12" fill="rgba(129,140,248,0.04)" stroke="rgba(129,140,248,0.12)" stroke-width="1"/>
  <text x="55" y="375" fill="#818cf8" font-size="13" font-weight="600" font-family="Inter">📋 Summary</text>
  <text x="55" y="398" fill="#c8c8e0" font-size="12" font-family="Inter">{summary[:80]}</text>
  <text x="55" y="420" fill="#c8c8e0" font-size="12" font-family="Inter">{summary[80:160]}</text>
  
  <text x="40" y="490" fill="#6b6b8a" font-size="11" font-family="Inter">🏷 {' • '.join(themes[:3])}</text>
  <text x="40" y="520" fill="#6b6b8a" font-size="11" font-family="Inter">Generated by Hermes Agent 🤖 • Speed Reading Việt Nam</text>
</svg>'''


def generate_notebook_html(notebook, article_title, article_source, filename):
    """Tạo trang HTML notebook hoàn chỉnh"""
    insights = notebook.get('key_insights', [])
    quotes = notebook.get('key_quotes', [])
    data_points = notebook.get('data_points', [])
    themes = notebook.get('themes', [])
    visual = notebook.get('visual_concept', '')
    outline = notebook.get('presentation_outline', [])
    script = notebook.get('video_script', '')
    hashtags = notebook.get('hashtags', [])
    summary = notebook.get('summary', '')
    
    svg_filename = filename.replace('.html', '.svg')
    svg_path = NOTEBOOKS_DIR / svg_filename
    
    # Generate SVG infographic
    svg_content = generate_infographic_svg(notebook, article_title)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_content, encoding='utf-8')
    
    insights_html = ''.join(f'<div class="nb-item insight"><span class="nb-icon">💡</span><span>{insight}</span></div>' for insight in insights)
    quotes_html = ''.join(f'<div class="nb-item quote"><span class="nb-icon">💬</span><span>"{q}"</span></div>' for q in quotes)
    data_html = ''.join(f'<div class="nb-item data"><span class="nb-icon">📊</span><span>{d}</span></div>' for d in data_points)
    outline_html = ''.join(f'<div class="outline-item"><span class="outline-num">{i+1}</span><span>{step}</span></div>' for i, step in enumerate(outline))
    script_paragraphs = ''.join(f'<p>{p.strip()}</p>' for p in script.split('\n') if p.strip())
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📓 {article_title[:60]} | NotebookLM</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/style.css">
    <style>
        .nb-header {{ margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
        .nb-meta {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; font-size: .85em; color: #8b8ba7; }}
        .nb-badge {{ display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;background:rgba(129,140,248,0.12);color:#818cf8;font-size:.8em;font-weight:600;}}
        .nb-title {{ font-size: clamp(1.3em,3vw,1.8em); font-weight: 700; line-height: 1.4; margin-bottom: 8px; }}
        .nb-section {{ margin-bottom: 28px; }}
        .nb-section h2 {{ font-size: 1.15em; font-weight: 600; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
        .nb-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }}
        .nb-item {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px 16px; display: flex; gap: 10px; align-items: flex-start; font-size: .92em; line-height: 1.5; }}
        .nb-item.insight {{ border-left: 3px solid #34d399; }}
        .nb-item.quote {{ border-left: 3px solid #fbbf24; font-style: italic; }}
        .nb-item.data {{ border-left: 3px solid #818cf8; }}
        .nb-icon {{ flex-shrink: 0; font-size: 1.1em; }}
        .nb-summary {{ background: rgba(129,140,248,0.04); border: 1px solid rgba(129,140,248,0.1); border-radius: 14px; padding: 20px; font-size: 1em; line-height: 1.8; color: #c8c8e0; }}
        .outline-item {{ display: flex; gap: 14px; align-items: center; padding: 12px 16px; background: rgba(255,255,255,0.02); border-radius: 10px; margin-bottom: 8px; }}
        .outline-num {{ display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: rgba(129,140,248,0.12); color: #818cf8; border-radius: 8px; font-weight: 700; font-size: .8em; flex-shrink: 0; }}
        .nb-script {{ background: rgba(0,0,0,0.2); border-radius: 14px; padding: 24px; font-size: 1.05em; line-height: 2; color: #e4e4f0; border-left: 4px solid rgba(129,140,248,0.3); }}
        .nb-script p {{ margin-bottom: 10px; }}
        .nb-visual {{ margin-top: 20px; }}
        .nb-visual img {{ max-width: 100%; border-radius: 14px; border: 1px solid rgba(255,255,255,0.06); }}
        .nb-visual-concept {{ background: rgba(168,85,247,0.04); border: 1px solid rgba(168,85,247,0.1); border-radius: 12px; padding: 16px; color: #c8c8e0; font-size: .9em; line-height: 1.6; }}
        .article-nav {{ display: flex; justify-content: space-between; margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.06); }}
        .article-nav a {{ color: #818cf8; text-decoration: none; font-weight: 500; }}
        @media (max-width:768px) {{ .nb-grid {{ grid-template-columns: 1fr; }} .nb-script {{ padding: 16px; }} }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-glow-2"></div>
    <div class="container report-page">
        <a href="../index.html" class="back">← Quay về Dashboard</a>
        
        <div class="nb-header">
            <div class="nb-meta">
                <span class="nb-badge">📓 NotebookLM</span>
                <span>📖 {article_source}</span>
                <span>{datetime.now().strftime("%d/%m/%Y")}</span>
            </div>
            <h1 class="nb-title">{article_title}</h1>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">{''.join(f'<span style="display:inline-block;padding:3px 10px;background:rgba(99,102,241,0.08);color:#818cf8;border-radius:6px;font-size:.75em;font-weight:500;">{t}</span>' for t in themes[:5])}</div>
        </div>
        
        <div class="nb-section">
            <h2>📋 Tóm tắt</h2>
            <div class="nb-summary">{summary}</div>
        </div>
        
        <div class="nb-section">
            <h2>💡 Key Insights</h2>
            <div class="nb-grid">{insights_html}</div>
        </div>
        
        <div class="nb-section">
            <h2>💬 Trích dẫn quan trọng</h2>
            <div class="nb-grid">{quotes_html}</div>
        </div>
        
        <div class="nb-section">
            <h2>📊 Số liệu đáng chú ý</h2>
            <div class="nb-grid">{data_html}</div>
        </div>
        
        <div class="nb-section">
            <h2>📋 Dàn bài trình bày</h2>
            {outline_html}
        </div>
        
        <div class="nb-section">
            <h2>🎬 Kịch bản video</h2>
            <div class="nb-script">{script_paragraphs}</div>
            <div style="margin-top:12px;color:#fbbf24;font-size:.9em;">🏷 {" ".join(hashtags)}</div>
        </div>
        
        <div class="nb-section">
            <h2>🎨 Hình tổng hợp thông tin</h2>
            <div class="nb-visual">
                <img src="{svg_filename}" alt="Infographic" loading="lazy">
            </div>
            <div class="nb-visual-concept">
                <strong>🎨 Ý tưởng thiết kế:</strong><br>{visual}
            </div>
        </div>
        
        <div class="article-nav">
            <a href="../index.html">← Dashboard</a>
            <a href="#" onclick="window.print()">🖨 In / Lưu PDF</a>
        </div>
    </div>
    <footer>
        <p>© 2026 <a href="https://speedreading.vn">Speed Reading Việt Nam</a></p>
        <p>Hotline: 0899.320.202 | Email: admin@speedreading.vn</p>
    </footer>
</body>
</html>'''


def update_index(article_title, notebook_filename, themes):
    """Cập nhật notebooks_index.json"""
    index = []
    if NOTEBOOKS_JSON.exists():
        try: index = json.loads(NOTEBOOKS_JSON.read_text())
        except: pass
    
    entry = {
        'title': article_title,
        'filename': notebook_filename,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'themes': themes[:3],
    }
    index.append(entry)
    NOTEBOOKS_JSON.write_text(json.dumps(index, ensure_ascii=False, indent=2))
    print(f"✅ notebooks_index.json: {len(index)} notebooks")


def process_article(article_path):
    """Xử lý 1 bài nghiên cứu → Notebook"""
    print(f"\n📓 Xử lý: {Path(article_path).name}")
    
    article = extract_article_content(article_path)
    if not article['content']:
        print(f"   ⚠️ Không đọc được nội dung")
        return False
    
    print(f"   📄 {article['title'][:60]}...")
    
    # Generate notebook
    print(f"   🧠 Đang tạo Notebook...")
    notebook = generate_notebook(article)
    if not notebook or 'error' in notebook:
        print(f"   ❌ Lỗi tạo notebook")
        return False
    
    print(f"   ✅ Notebook: {len(notebook.get('key_insights',[]))} insights, {len(notebook.get('key_quotes',[]))} quotes")
    
    # Generate HTML
    date_str = datetime.now().strftime('%Y-%m-%d')
    slug = slugify(article['title'])
    filename = f'{date_str}-notebook-{slug}.html'
    
    html = generate_notebook_html(notebook, article['title'], article['source'], filename)
    out = NOTEBOOKS_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f"   ✅ Trang HTML: {filename}")
    
    # Update index
    update_index(article['title'], filename, notebook.get('themes', []))
    
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description='NotebookLM Pipeline')
    parser.add_argument('--article', help='Đường dẫn file HTML bài nghiên cứu')
    parser.add_argument('--random', type=int, help='Số bài ngẫu nhiên để xử lý')
    args = parser.parse_args()
    
    if args.article:
        process_article(args.article)
    elif args.random:
        articles = sorted(ARTICLES_DIR.glob('*.html'))
        import random
        selected = random.sample(articles, min(args.random, len(articles)))
        print(f"📚 Chọn {len(selected)}/{len(articles)} bài ngẫu nhiên")
        for a in selected:
            process_article(a)
    else:
        print("❌ Cần --article hoặc --random")
        sys.exit(1)
    
    print(f"\n🔗 https://vanthuonghi.github.io/speedreading-insights/notebooks/")


if __name__ == '__main__':
    main()