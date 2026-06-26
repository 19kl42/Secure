from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton

class PasskeyManagerDialog(QDialog):
    def __init__(self, parent, passkey_history):
        super().__init__(parent)
        self.setWindowTitle("パスキー (WebAuthn) 利用履歴")
        self.resize(400, 300)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>パスキーが要求・利用されたサイト一覧:</b>"))
        
        history_list = QListWidget()
        if not passkey_history:
            history_list.addItem("履歴はありません。")
        else:
            for rp_id in sorted(passkey_history):
                history_list.addItem(f"・{rp_id}")
                
        layout.addWidget(history_list)
        
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        self.setLayout(layout)
