import sys
import os

# 追加: Pythonモジュール検索パスに現在のディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.browser_window import BrowserWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MyBrowser")
    
    window = BrowserWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
