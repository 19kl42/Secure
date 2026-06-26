from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("ブラウザ設定")
        self.resize(400, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>起動ページ (ホームページ) のURL:</b>"))
        
        self.url_input = QLineEdit()
        self.url_input.setText(self.settings_manager.get_startup_url())
        layout.addWidget(self.url_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def save_settings(self):
        new_url = self.url_input.text()
        if new_url and not new_url.startswith("http"):
            new_url = "https://" + new_url
        self.settings_manager.set_startup_url(new_url)
        self.accept()
