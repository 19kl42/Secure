from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QToolBar, QLineEdit, QTabWidget, QWidget, QVBoxLayout, QStyle
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
from core.blocklist_manager import BlocklistManager

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyBrowser - Privacy First")
        self.resize(1024, 768)

        # QSS - Chrome風のモダンなライトテーマ
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f1f3f4;
            }
            QToolBar {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #dadce0;
                padding: 4px;
                spacing: 8px;
            }
            QToolButton {
                background-color: transparent;
                border-radius: 16px;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #f1f3f4;
            }
            QLineEdit {
                background-color: #f1f3f4;
                border: 1px solid transparent;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 14px;
                selection-background-color: #c6d8eb;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 1px solid #4285f4;
            }
            QTabWidget::pane {
                border: none;
                border-top: 1px solid #dadce0;
            }
            QTabBar::tab {
                background-color: #f1f3f4;
                color: #5f6368;
                border: none;
                border-right: 1px solid #dadce0;
                padding: 8px 16px;
                min-width: 120px;
                max-width: 240px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-top: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #202124;
                border-top: 1px solid #dadce0;
                border-left: 1px solid #dadce0;
                border-right: 1px solid #dadce0;
                margin-top: 0px;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8eaed;
            }
            QTabBar::close-button {
                image: url(''); /* デフォルトを消してOSネイティブっぽくするか、文字で代替可能 */
            }
        """)

        # Core logic setup
        self.settings = SettingsManager()
        self.news_fetcher = NewsFetcher()
        self.news_fetcher.fetch_feeds_background()
        
        self.blocklist_manager = BlocklistManager()
        self.blocklist_manager.update_list_background()
        
        self.passkey_handler = PasskeyHandler()
        self.interceptor = PrivacyInterceptor(self.blocklist_manager, self)
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
        navbar.setMovable(False)
        self.addToolBar(navbar)

        # アイコンの取得
        style = self.style()
        icon_back = style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack)
        icon_forward = style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward)
        icon_reload = style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        icon_add = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        back_btn = QAction(icon_back, "Back", self)
        back_btn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        navbar.addAction(back_btn)

        forward_btn = QAction(icon_forward, "Forward", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        navbar.addAction(forward_btn)

        reload_btn = QAction(icon_reload, "Reload", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        navbar.addAction(reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("検索または URL を入力")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        
        new_tab_btn = QAction("＋", self)
        new_tab_btn.setToolTip("新しいタブを開く")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab("", "New Tab"))
        navbar.addAction(new_tab_btn)

        shield_btn = QAction("🛡️", self)
        shield_btn.setToolTip("Privacy Shield")
        shield_btn.triggered.connect(self.show_privacy_shield)
        navbar.addAction(shield_btn)
        
        passkey_btn = QAction("🔑", self)
        passkey_btn.setToolTip("Passkeys")
        passkey_btn.triggered.connect(self.show_passkey_manager)
        navbar.addAction(passkey_btn)
        
        settings_btn = QAction("⚙️", self)
        settings_btn.setToolTip("Settings")
        settings_btn.triggered.connect(self.show_settings)
        navbar.addAction(settings_btn)

        # ショートカットキーの設定
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self.add_new_tab("", "New Tab"))
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.focus_url_bar)

        # 初期タブを作成
        startup_url = self.settings.get_startup_url()
        self.add_new_tab(startup_url, "Homepage")

    def focus_url_bar(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()

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
            html = self.news_fetcher.get_html()
            browser.setHtml(html, QUrl("about:newtab"))
            label = "News Hub"
            
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.titleChanged.connect(lambda title, browser=browser:
                                     self.tabs.setTabText(self.tabs.indexOf(browser), title[:20] + "..." if len(title) > 20 else title))
        
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_url_bar(qurl, browser))
        
        # 新しいタブが開かれたらURLバーに自動フォーカス
        self.url_bar.setFocus()
        self.url_bar.selectAll()
                                   
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
            self.url_bar.setText("")
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
            pass
