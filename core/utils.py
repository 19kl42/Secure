import os
import sys

def get_data_dir():
    """
    アプリケーションのデータを安全に保存するためのディレクトリを取得します。
    Macアプリケーション（.app）内は書き込み禁止であるため、標準的なLibraryフォルダを利用します。
    """
    home = os.path.expanduser("~")
    # Mac標準のApplication Support配下にデータを保存
    data_dir = os.path.join(home, "Library", "Application Support", "MyBrowser")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_resource_path(relative_path):
    """
    PyInstallerでビルドした際の一時フォルダ (_MEIPASS) を考慮してリソースパスを解決します。
    ビルドしていない開発環境では通常のパスを返します。
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', relative_path)
