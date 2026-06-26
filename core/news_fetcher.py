import json
import os
from core.utils import get_data_dir
import threading
import urllib.request
import xml.etree.ElementTree as ET

class NewsFetcher:
    def __init__(self):
        self.cache_path = os.path.join(get_data_dir(), 'news_cache.json')
        self.feeds = [
            {"name": "JPCERT/CC (Security Alerts)", "url": "https://www.jpcert.or.jp/rss/jpcert.rdf"},
            {"name": "ZDNet Japan (Security)", "url": "https://japan.zdnet.com/rss/news/security/"},
            {"name": "ITmedia (Security)", "url": "https://rss.itmedia.co.jp/rss/2.0/enterprise_security.xml"}
        ]
        self.cached_news = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_cache(self, data):
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.cached_news = data
        except Exception as e:
            print(f"ニュースキャッシュの保存に失敗: {e}")

    def fetch_feeds_background(self):
        thread = threading.Thread(target=self._fetch_feeds_sync)
        thread.daemon = True
        thread.start()

    def _fetch_feeds_sync(self):
        all_news = []
        for feed in self.feeds:
            try:
                req = urllib.request.Request(feed["url"], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    xml_data = response.read()
                    
                root = ET.fromstring(xml_data)
                
                # RSS 2.0 (channel/item) または RDF 1.0 (item)
                items = root.findall('.//item') or root.findall('.//{http://purl.org/rss/1.0/}item')
                
                for item in items[:10]: # 各フィード最大10件
                    title = item.find('title')
                    link = item.find('link')
                    if title is None and '{http://purl.org/rss/1.0/}title' in item.tag:
                        pass # namespace parsing can be tricky, using basic text
                    
                    # 簡易的な名前空間対応抽出
                    t_text = "".join(item.itertext()).strip()
                    
                    # ちゃんとタグを探す（名前空間無視の簡易手法）
                    title_elem = next((e for e in item.iter() if 'title' in e.tag.lower()), None)
                    link_elem = next((e for e in item.iter() if 'link' in e.tag.lower()), None)
                    
                    if title_elem is not None and link_elem is not None:
                        all_news.append({
                            "source": feed["name"],
                            "title": title_elem.text,
                            "link": link_elem.text
                        })
            except Exception as e:
                print(f"フィード取得エラー ({feed['name']}): {e}")
                
        if all_news:
            self.save_cache(all_news)

    def get_html(self):
        html = """
        <html>
        <head>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f5f5f7; color: #1d1d1f; margin: 40px; }
                h1 { text-align: center; color: #0071e3; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .news-item { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #e5e5ea; }
                .news-item:last-child { border-bottom: none; }
                .source { font-size: 0.8em; color: #86868b; text-transform: uppercase; font-weight: bold; margin-bottom: 4px; display: block; }
                a { color: #1d1d1f; text-decoration: none; font-size: 1.1em; font-weight: 500; }
                a:hover { color: #0071e3; }
            </style>
        </head>
        <body>
            <h1>🛡️ Security & Tech News</h1>
            <div class="container">
        """
        
        if not self.cached_news:
            html += "<p>ニュースを読み込み中です...（新しいタブを開き直すかリロードしてください）</p>"
        else:
            for news in self.cached_news:
                html += f"""
                <div class="news-item">
                    <span class="source">{news['source']}</span>
                    <a href="{news['link']}">{news['title']}</a>
                </div>
                """
                
        html += """
            </div>
        </body>
        </html>
        """
        return html
