from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class PrivacyInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocklist_manager, parent=None):
        super().__init__(parent)
        self.blocklist_manager = blocklist_manager
        
        # サイトごとのトラッキングデータを保持 (Key: First Party Host)
        self.site_stats = {}

    def get_stats(self, host):
        if host not in self.site_stats:
            self.site_stats[host] = {
                "blocked": [],
                "third_party": set()
            }
        return self.site_stats[host]

    def interceptRequest(self, info):
        req_host = info.requestUrl().host()
        first_party_host = info.firstPartyUrl().host()
        
        if not first_party_host:
            first_party_host = req_host

        stats = self.get_stats(first_party_host)

        # ブロック判定 (O(1) の高速検索 + サブドメイン階層検索)
        if self.blocklist_manager.is_blocked(req_host):
            print(f"[BLOCKED] トラッカー/マルウェアをブロック: {req_host}")
            if req_host not in stats["blocked"]:
                stats["blocked"].append(req_host)
            info.block(True)
            return
        
        # サードパーティ判定 (簡易的)
        if req_host and first_party_host and not req_host.endswith(first_party_host):
            stats["third_party"].add(req_host)
