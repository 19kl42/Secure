from PyQt6.QtWebEngineCore import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.browser_window = None

    def set_browser_window(self, window):
        self.browser_window = window

    def createWindow(self, _type):
        """リンクが別ウィンドウ（target='_blank'）で開かれる際に呼ばれる"""
        if self.browser_window:
            # メインウィンドウに新しいタブを作成し、そのページインスタンスを返す
            new_view = self.browser_window.add_new_tab("")
            return new_view.page()
        return super().createWindow(_type)
