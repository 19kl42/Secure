import json
import os

class PasskeyHandler:
    def __init__(self):
        self.history_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.json')
        self.passkey_history = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"パスキー履歴の読み込みに失敗しました: {e}")
        return set()

    def save_history(self):
        try:
            # setはそのままJSONにできないのでlistに変換
            os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.passkey_history), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"パスキー履歴の保存に失敗しました: {e}")

    def get_history(self):
        return self.passkey_history

    def on_passkey_requested(self, request):
        rp_id = request.relyingPartyId()
        print(f"[WebAuthn] パスキーが要求されました: {rp_id}")
        if rp_id not in self.passkey_history:
            self.passkey_history.add(rp_id)
            self.save_history()
