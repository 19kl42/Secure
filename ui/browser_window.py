from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QToolBar, QLineEdit, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from ui.privacy_shield import PrivacyShieldDialog
from ui.passkey_dialog import PasskeyManagerDialog
from core.interceptor import PrivacyInterceptor
from core.passkey_handler import PasskeyHandler

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyBrowser - Privacy First")
        self.resize(1024, 768)

        # Core logic setup
        self.passkey_handler = PasskeyHandler()
        self.interceptor = PrivacyInterceptor(self)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # Engine setup
        self.browser = QWebEngineView()
        try:
            self.browser.page().webAuthUxRequested.connect(self.passkey_handler.on_passkey_requested)
        except AttributeError:
            print("警告: 使用中のPyQt6バージョンは webAuthUxRequested をサポートしていません。")

        self.browser.setUrl(QUrl("https://duckduckgo.com"))
        self.setCentralWidget(self.browser)

        # Navigation Bar
        navbar = QToolBar("Navigation")
        self.addToolBar(navbar)

        back_btn = QAction("←", self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction("↻", self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        shield_btn = QAction("🛡️ Shield", self)
        shield_btn.triggered.connect(self.show_privacy_shield)
        navbar.addAction(shield_btn)
        
        passkey_btn = QAction("🔑 Passkeys", self)
        passkey_btn.triggered.connect(self.show_passkey_manager)
        navbar.addAction(passkey_btn)

        self.browser.urlChanged.connect(self.update_url_bar)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = f"https://duckduckgo.com/?q={url}"
        self.browser.setUrl(QUrl(url))

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

    def show_privacy_shield(self):
        current_url = self.browser.url()
        host = current_url.host()
        if not host:
            return
        
        stats = self.interceptor.get_stats(host)
        dialog = PrivacyShieldDialog(self, host, stats)
        dialog.exec()

    def show_passkey_manager(self):
        history = self.passkey_handler.get_history()
        dialog = PasskeyManagerDialog(self, history)
        dialog.exec()
