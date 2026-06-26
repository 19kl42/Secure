import json
import os
from core.utils import get_data_dir

class SettingsManager:
    def __init__(self):
        self.settings_path = os.path.join(get_data_dir(), 'settings.json')
        self.default_settings = {
            "startup_url": "https://duckduckgo.com"
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Merge with defaults
                    return {**self.default_settings, **data}
            except Exception as e:
                print(f"設定の読み込みに失敗しました: {e}")
        return self.default_settings.copy()

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"設定の保存に失敗しました: {e}")

    def get_startup_url(self):
        return self.settings.get("startup_url", self.default_settings["startup_url"])

    def set_startup_url(self, url):
        self.settings["startup_url"] = url
        self.save_settings()
