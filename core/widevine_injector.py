import os
import platform

def inject_widevine():
    """
    PCにインストールされているGoogle ChromeからWidevine DRMモジュールを自動検出し、
    MyBrowserのエンジンにパスを渡してDRMを有効化します。
    """
    # 現在のChromiumフラグを取得
    flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
    
    if "widevine-cdm-path" in flags:
        return # 既に設定済み

    # macOSのChromeの標準インストールパス
    base_path = "/Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Versions"
    
    if not os.path.exists(base_path):
        print("[Widevine] Google Chromeがインストールされていません。")
        return

    # バージョンフォルダを取得し、最新のものを優先
    versions = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d != "Current"]
    
    # 簡単なバージョンソート（文字列ソートでも100番台なので概ね正しくソートされる）
    versions.sort(reverse=True)

    # CPUアーキテクチャの判定 (M1/M2/M3 なら arm64, Intel なら x64)
    arch = "mac_arm64" if platform.machine() == "arm64" else "mac_x64"
    
    cdm_path = None
    cdm_version = "4.10.2710.0" # デフォルトのフォールバックバージョン
    for version in versions:
        potential_path = os.path.join(base_path, version, "Libraries", "WidevineCdm", "_platform_specific", arch, "libwidevinecdm.dylib")
        if os.path.exists(potential_path):
            cdm_path = potential_path
            
            # バージョン情報の取得 (NetflixなどのDRM認証に必須)
            import json
            manifest_path = os.path.join(base_path, version, "Libraries", "WidevineCdm", "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                        if "version" in manifest:
                            cdm_version = manifest["version"]
                except Exception:
                    pass
            break
            
    if cdm_path:
        print(f"[Widevine] 自動検出完了: {cdm_path} (Version: {cdm_version})")
        new_flags = f"{flags} --widevine-cdm-path=\"{cdm_path}\" --widevine-cdm-version=\"{cdm_version}\""
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = new_flags.strip()
    else:
        print(f"[Widevine] 指定アーキテクチャ({arch})のCDMが見つかりませんでした。")
