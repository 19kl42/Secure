from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton

class PrivacyShieldDialog(QDialog):
    def __init__(self, parent, host, stats):
        super().__init__(parent)
        self.setWindowTitle(f"Privacy Shield - {host}")
        self.resize(400, 300)
        layout = QVBoxLayout()
        
        title = QLabel(f"<b>{host} への連携情報</b>")
        layout.addWidget(title)
        
        info_label = QLabel(
            "<b>標準送信ヘッダー:</b><br>"
            "・User-Agent (ブラウザ・OS情報)<br>"
            "・Accept-Language (言語設定)<br>"
            "・IPアドレス<br>"
            "・(該当する場合) 1st Party Cookie"
        )
        layout.addWidget(info_label)
        
        layout.addWidget(QLabel(f"<b>ブロック済みのトラッカー ({len(stats['blocked'])}件):</b>"))
        blocked_list = QListWidget()
        for b in stats["blocked"]:
            blocked_list.addItem(b)
        layout.addWidget(blocked_list)
        
        layout.addWidget(QLabel(f"<b>許可されたサードパーティ通信 ({len(stats['third_party'])}件):</b>"))
        tp_list = QListWidget()
        for t in stats["third_party"]:
            tp_list.addItem(t)
        layout.addWidget(tp_list)
        
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
