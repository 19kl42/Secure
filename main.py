import sys
import os

# 追加: Pythonモジュール検索パスに現在のディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 修正: macOS(M1/Intel等の特定バージョン)のMetalシェーダーコンパイルエラーを回避
# WebEngineのGPUレンダリングで画面が表示されなくなるインシデント対策
# ＋画面複製・録画時にDRMコンテンツ(Netflix等)が真っ黒になるHDCPブロックを回避
# ＋Widevine DRMを有効化
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --enable-widevine"

from PyQt6.QtWidgets import QApplication
from ui.browser_window import BrowserWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Mac特有のネイティブスタイルを無効化しQSSを完全適用
    app.setApplicationName("MyBrowser")
    
    window = BrowserWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
