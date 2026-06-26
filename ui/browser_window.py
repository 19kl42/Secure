from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QToolBar, QLineEdit, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from ui.privacy_shield import PrivacyShieldDialog
from ui.passkey_dialog import PasskeyManagerDialog
from ui.settings_dialog import SettingsDialog
from core.interceptor import PrivacyInterceptor
from core.passkey_handler import PasskeyHandler
from core.engine import CustomWebEnginePage
from core.settings_manager import SettingsManager
from core.news_fetcher import NewsFetcher

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyBrowser - Privacy First")
        self.resize(1024, 768)

        # Core logic setup
        self.settings = SettingsManager()
        self.news_fetcher = NewsFetcher()
        self.news_fetcher.fetch_feeds_background() # バックグラウンドでニュース更新
        
        self.passkey_handler = PasskeyHandler()
        self.interceptor = PrivacyInterceptor(self)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # Tabs setup
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # Navigation Bar
        navbar = QToolBar("Navigation")
        self.addToolBar(navbar)

        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        navbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        navbar.addAction(forward_btn)

        reload_btn = QAction("↻", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        navbar.addAction(reload_btn)

        new_tab_btn = QAction("＋", self)
        new_tab_btn.setToolTip("新しいタブを開く")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab("", "New Tab")) # 空URLでニュースタブ
        navbar.addAction(new_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        shield_btn = QAction("🛡️ Shield", self)
        shield_btn.triggered.connect(self.show_privacy_shield)
        navbar.addAction(shield_btn)
        
        passkey_btn = QAction("🔑 Passkeys", self)
        passkey_btn.triggered.connect(self.show_passkey_manager)
        navbar.addAction(passkey_btn)
        
        settings_btn = QAction("⚙️ Settings", self)
        settings_btn.triggered.connect(self.show_settings)
        navbar.addAction(settings_btn)

        # 初期タブを作成 (起動ページ設定を読み込む)
        startup_url = self.settings.get_startup_url()
        self.add_new_tab(startup_url, "Homepage")

    def add_new_tab(self, url="", label="New Tab"):
        browser = QWebEngineView()
        page = CustomWebEnginePage(self.profile, browser)
        page.set_browser_window(self)
        browser.setPage(page)
        
        try:
            page.webAuthUxRequested.connect(self.passkey_handler.on_passkey_requested)
        except AttributeError:
            pass 

        if url:
            browser.setUrl(QUrl(url))
        else:
            # URLが空の場合はニュースハブのHTMLを流し込む
            html = self.news_fetcher.get_html()
            browser.setHtml(html, QUrl("about:newtab"))
            label = "News Hub"
            
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.titleChanged.connect(lambda title, browser=browser:
                                     self.tabs.setTabText(self.tabs.indexOf(browser), title[:20] + "..." if len(title) > 20 else title))
        
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_url_bar(qurl, browser))
                                   
        return browser

    def close_tab(self, i):
        if self.tabs.count() < 2:
            return 
        widget = self.tabs.widget(i)
        self.tabs.removeTab(i)
        widget.deleteLater()

    def current_browser(self):
        return self.tabs.currentWidget()

    def current_tab_changed(self, i):
        browser = self.current_browser()
        if browser and browser.url():
            self.update_url_bar(browser.url(), browser)

    def update_url_bar(self, qurl, browser=None):
        if browser != self.current_browser():
            return
        
        url_str = qurl.toString()
        if url_str == "about:newtab":
            self.url_bar.setText("") # ニュースハブの場合は空にする
        else:
            self.url_bar.setText(url_str)
        self.url_bar.setCursorPosition(0)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url:
            return
            
        if not url.startswith("http"):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = f"https://duckduckgo.com/?q={url}"
        
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(url))

    def show_privacy_shield(self):
        browser = self.current_browser()
        if not browser:
            return
        current_url = browser.url()
        host = current_url.host()
        if not host and current_url.toString() != "about:newtab":
            return
            
        stats = self.interceptor.get_stats(host) if host else {"blocked": [], "third_party": []}
        dialog = PrivacyShieldDialog(self, host or "News Hub", stats)
        dialog.exec()

    def show_passkey_manager(self):
        history = self.passkey_handler.get_history()
        dialog = PasskeyManagerDialog(self, history)
        dialog.exec()
        
    def show_settings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec():
            # 設定が保存されたあとの処理（必要であれば）
            pass
