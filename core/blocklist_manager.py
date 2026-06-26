import json
import os
from core.utils import get_data_dir
import threading
import urllib.request
import time

class BlocklistManager:
    def __init__(self):
        # 従来の簡易リスト
        self.basic_blocklist_path = os.path.join(get_data_dir(), 'blocklist.json')
        # 外部から取得した大規模リスト
        self.compiled_blocklist_path = os.path.join(get_data_dir(), 'compiled_blocklist.json')
        
        # StevenBlack hosts (Ads & Malware)
        self.list_url = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
        
        self.blocked_domains = set()
        self.load_local_lists()

    def load_local_lists(self):
        # 簡易リストの読み込み
        if os.path.exists(self.basic_blocklist_path):
            try:
                with open(self.basic_blocklist_path, 'r', encoding='utf-8') as f:
                    basic_list = json.load(f)
                    for domain in basic_list:
                        self.blocked_domains.add(domain)
            except Exception as e:
                print(f"簡易ブロックリストの読み込みに失敗: {e}")

        # コンパイル済みリストの読み込み
        if os.path.exists(self.compiled_blocklist_path):
            try:
                with open(self.compiled_blocklist_path, 'r', encoding='utf-8') as f:
                    compiled_list = json.load(f)
                    for domain in compiled_list:
                        self.blocked_domains.add(domain)
            except Exception as e:
                print(f"コンパイル済みリストの読み込みに失敗: {e}")

    def update_list_background(self):
        # ファイルが存在し、最終更新から24時間以内ならスキップ
        if os.path.exists(self.compiled_blocklist_path):
            file_age = time.time() - os.path.getmtime(self.compiled_blocklist_path)
            if file_age < 86400: # 24時間
                return
                
        thread = threading.Thread(target=self._download_and_compile)
        thread.daemon = True
        thread.start()

    def _download_and_compile(self):
        try:
            req = urllib.request.Request(self.list_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                
            new_domains = set()
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # コメントや空行を無視
                if not line or line.startswith('#'):
                    continue
                    
                # hosts形式 (0.0.0.0 domain.com) をパース
                parts = line.split()
                if len(parts) >= 2 and (parts[0] == '0.0.0.0' or parts[0] == '127.0.0.1'):
                    domain = parts[1]
                    if domain != '0.0.0.0' and domain != 'localhost' and domain != 'broadcasthost':
                        new_domains.add(domain)
            
            if new_domains:
                # メモリ上のセットを更新 (スレッドセーフティのために元の要素を残しつつ統合)
                self.blocked_domains.update(new_domains)
                
                # キャッシュに保存
                os.makedirs(os.path.dirname(self.compiled_blocklist_path), exist_ok=True)
                with open(self.compiled_blocklist_path, 'w', encoding='utf-8') as f:
                    json.dump(list(new_domains), f, indent=2)
                print(f"ブロックリストを更新しました (合計: {len(self.blocked_domains)}件)")

        except Exception as e:
            print(f"ブロックリストのダウンロードに失敗: {e}")

    def is_blocked(self, host):
        if not host:
            return False
            
        # O(1) ハッシュ検索
        if host in self.blocked_domains:
            return True
            
        # サブドメインの階層を遡ってチェック (例: a.b.ads.com -> b.ads.com -> ads.com)
        parts = host.split('.')
        for i in range(1, len(parts) - 1):
            parent_domain = '.'.join(parts[i:])
            if parent_domain in self.blocked_domains:
                return True
                
        return False
