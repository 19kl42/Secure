from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QToolBar, QLineEdit, QTabWidget, QWidget, QVBoxLayout, QStyle
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from ui.privacy_shield import PrivacyShieldDialog
from ui.passkey_dialog import PasskeyManagerDialog
from ui.settings_dialog import SettingsDialog
from core.interceptor import PrivacyInterceptor
from core.passkey_handler import PasskeyHandler
from core.engine import CustomWebEnginePage
from core.settings_manager import SettingsManager
from core.news_fetcher import NewsFetcher
from core.blocklist_manager import BlocklistManager
from core.bookmark_manager import BookmarkManager

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyBrowser - Privacy First")
        self.resize(1024, 768)

        # QSS - 究極のChromeデザイン完全模倣 (Chrome Refresh 2023 / Material You)
        # QSS - 究極のChromeデザイン完全模倣 (Chrome Refresh 2023 / Material You)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #dfe1e5; 
            }
            QToolBar {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #dadce0;
                padding: 4px 8px;
                spacing: 6px;
            }
            QToolButton {
                background-color: transparent;
                border-radius: 18px; 
                min-width: 36px;
                min-height: 36px;
                font-size: 18px;
                color: #5f6368;
            }
            QToolButton:hover {
                background-color: #f1f3f4;
            }
            QToolButton:pressed {
                background-color: #e8eaed;
            }
            QLineEdit {
                background-color: #f1f3f4;
                border: 2px solid transparent;
                border-radius: 18px;
                padding: 6px 20px;
                min-height: 24px;
                font-size: 14px;
                color: #202124;
                selection-background-color: #c6d8eb;
            }
            QLineEdit:hover {
                background-color: #e8eaed;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid #a8c7fa; 
            }
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: transparent; 
                color: #5f6368;
                border: none;
                padding: 10px 16px;
                min-width: 140px;
                max-width: 240px;
                border-radius: 12px;
                margin-top: 8px;
                margin-bottom: 4px;
                margin-left: 2px;
                margin-right: 2px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #202124;
                font-weight: 500;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d7d8dc;
            }
        """)

        # Core logic setup
        self.settings = SettingsManager()
        self.news_fetcher = NewsFetcher()
        self.news_fetcher.fetch_feeds_background()
        
        self.blocklist_manager = BlocklistManager()
        self.blocklist_manager.update_list_background()
        
        self.bookmark_manager = BookmarkManager()
        
        self.passkey_handler = PasskeyHandler()
        self.interceptor = PrivacyInterceptor(self.blocklist_manager, self)
        
        # プロファイルの設定 (Widevine等のプラグインを有効化)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setUrlRequestInterceptor(self.interceptor)
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)

        self.setup_ui()
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

        # アイコンの代わりにモダンなフォントによるUnicodeを使用
        back_btn = QAction("←", self)
        back_btn.setToolTip("戻る")
        back_btn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        navbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.setToolTip("進む")
        forward_btn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        navbar.addAction(forward_btn)

        reload_btn = QAction("↻", self)
        reload_btn.setToolTip("再読み込み")
        reload_btn.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        navbar.addAction(reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("検索または URL を入力")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.bookmark_btn = QAction("☆", self)
        self.bookmark_btn.setToolTip("ブックマークに追加")
        self.bookmark_btn.triggered.connect(self.toggle_bookmark)
        navbar.addAction(self.bookmark_btn)
        
        new_tab_btn = QAction("＋", self)
        new_tab_btn.setToolTip("新しいタブを開く")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab("", "New Tab"))
        navbar.addAction(new_tab_btn)

        shield_btn = QAction("🛡️", self)
        shield_btn.setToolTip("Privacy Shield")
        shield_btn.triggered.connect(self.show_privacy_shield)
        navbar.addAction(shield_btn)
        
        # Passkey Manager Button
        self.passkey_btn = QAction("🔑", self)
        self.passkey_btn.setToolTip("Passkeys")
        self.passkey_btn.triggered.connect(self.show_passkey_manager)
        navbar.addAction(self.passkey_btn)

        # ブックマークバーの構築
        self.bookmark_bar = QToolBar("Bookmarks")
        self.bookmark_bar.setMovable(False)
        self.bookmark_bar.setStyleSheet("QToolBar { border: none; padding: 2px 8px; background-color: #ffffff; border-bottom: 1px solid #dadce0; } QToolButton { font-size: 13px; border-radius: 12px; padding: 4px 8px; color: #5f6368; } QToolButton:hover { background-color: #f1f3f4; }")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.bookmark_bar)
        self.update_bookmark_bar()

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

    def update_url_bar(self, q, browser=None):
        if browser != self.current_browser():
            return
        url = q.toString()
        if url == "about:newtab":
            self.url_bar.setText("")
        else:
            self.url_bar.setText(url)
        self.url_bar.setCursorPosition(0)
        
        # ブックマーク状態の更新 (★の色付け)
        if hasattr(self, 'bookmark_btn'):
            if self.bookmark_manager.is_bookmarked(url):
                self.bookmark_btn.setText("★")
            else:
                self.bookmark_btn.setText("☆")

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url:
            return
            
        if not url.startswith('http'):
            # Google検索をデフォルトとする判定ロジック
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                import urllib.parse
                query = urllib.parse.quote(url)
                url = f'https://www.google.com/search?q={query}'
        
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(url))

    def toggle_bookmark(self):
        browser = self.current_browser()
        if not browser:
            return
        url = browser.url().toString()
        title = browser.title() or url
        
        if self.bookmark_manager.is_bookmarked(url):
            self.bookmark_manager.remove_bookmark(url)
        else:
            self.bookmark_manager.add_bookmark(title, url)
            
        self.update_bookmark_bar()
        self.update_url_bar(browser.url(), browser)

    def update_bookmark_bar(self):
        self.bookmark_bar.clear()
        for b in self.bookmark_manager.bookmarks:
            # タイトルが長い場合は切り詰める
            title = (b['title'][:15] + '..') if len(b['title']) > 15 else b['title']
            action = QAction(title, self)
            action.setToolTip(b['url'])
            action.setData(b['url'])
            action.triggered.connect(self._bookmark_clicked)
            self.bookmark_bar.addAction(action)

    def _bookmark_clicked(self):
        action = self.sender()
        if action:
            url = action.data()
            if self.current_browser():
                self.current_browser().setUrl(QUrl(url))
            else:
                self.add_new_tab(url, "Bookmark")

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
