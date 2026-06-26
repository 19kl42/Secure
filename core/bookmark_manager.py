import json
import os

class BookmarkManager:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bookmarks.json')
        self.bookmarks = self.load_bookmarks()

    def load_bookmarks(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"ブックマークの読み込みに失敗: {e}")
        return []

    def save_bookmarks(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"ブックマークの保存に失敗: {e}")

    def add_bookmark(self, title, url):
        # 既に存在する場合は無視
        if not self.is_bookmarked(url):
            self.bookmarks.append({"title": title, "url": url})
            self.save_bookmarks()
            return True
        return False

    def remove_bookmark(self, url):
        original_count = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b.get('url') != url]
        if len(self.bookmarks) < original_count:
            self.save_bookmarks()
            return True
        return False

    def is_bookmarked(self, url):
        for b in self.bookmarks:
            if b.get('url') == url:
                return True
        return False
