import json
import os
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class PrivacyInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocklist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'blocklist.json')
        self.blocked_domains_list = self.load_blocklist()
        
        # サイトごとのトラッキングデータを保持 (Key: First Party Host)
        self.site_stats = {}

    def load_blocklist(self):
        if os.path.exists(self.blocklist_path):
            try:
                with open(self.blocklist_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"ブロックリストの読み込みに失敗しました: {e}")
        return ["doubleclick.net", "google-analytics.com"]

    def get_stats(self, host):
        if host not in self.site_stats:
            self.site_stats[host] = {
                "blocked": [],
                "third_party": set()
            }
        return self.site_stats[host]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        req_host = info.requestUrl().host()
        first_party_host = info.firstPartyUrl().host()
        
        if not first_party_host:
            first_party_host = req_host

        stats = self.get_stats(first_party_host)

        # ブロック判定
        for domain in self.blocked_domains_list:
            if domain in url:
                print(f"[BLOCKED] トラッカーをブロックしました: {url}")
                if domain not in stats["blocked"]:
                    stats["blocked"].append(domain)
                info.block(True)
                return
        
        # サードパーティ判定 (簡易的)
        if req_host and first_party_host and not req_host.endswith(first_party_host):
            stats["third_party"].add(req_host)
