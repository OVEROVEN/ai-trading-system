#!/usr/bin/env python3
"""
TradingView Charting Library 權限申請和替代方案指南
"""

import webbrowser
import sys
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"[INFO] {title}")
    print('='*60)

def show_official_access_process():
    """顯示官方權限申請流程"""
    print_header("官方 Charting Library 權限申請")
    
    print("TradingView Charting Library 主倉庫是私有的，需要申請權限。")
    print("\n步驟 1: 申請權限")
    print("• 訪問: https://www.tradingview.com/advanced-charts/")
    print("• 點擊 'Get Library' 按鈕")
    print("• 填寫申請表單")
    print("• 等待 TradingView 團隊審核")
    
    print("\n步驟 2: 獲得權限後")
    print("• GitHub 倉庫: https://github.com/tradingview/charting_library")
    print("• 文檔和教程: https://github.com/tradingview/charting-library-tutorial")
    print("• 範例代碼: https://github.com/tradingview/charting-library-examples")
    
    print("\n[WARNING] 申請可能需要幾天時間")

def show_lightweight_charts_alternative():
    """顯示 Lightweight Charts 替代方案"""
    print_header("替代方案: TradingView Lightweight Charts")
    
    print("TradingView Lightweight Charts 是開源的輕量級圖表庫：")
    print("• 完全免費和開源")
    print("• 高性能，檔案小")
    print("• 支援 K線、線圖、面積圖")
    print("• GitHub: https://github.com/tradingview/lightweight-charts")
    
    print("\n優點：")
    print("✅ 無需申請權限")
    print("✅ 商業使用免費")
    print("✅ 積極維護")
    print("✅ 豐富的文檔")
    
    print("\n限制：")
    print("❌ 功能較完整版本少")
    print("❌ 無內建技術指標")
    print("❌ 自定義能力有限")

def download_lightweight_charts():
    """下載 Lightweight Charts"""
    print_header("下載 TradingView Lightweight Charts")
    
    import requests
    import zipfile
    from pathlib import Path
    
    try:
        # 獲取最新版本
        api_url = "https://api.github.com/repos/tradingview/lightweight-charts/releases/latest"
        print("[INFO] 正在獲取最新版本...")
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        release_info = response.json()
        version = release_info["tag_name"]
        
        print(f"[FOUND] 最新版本: {version}")
        
        # 下載 ZIP
        zip_url = f"https://github.com/tradingview/lightweight-charts/archive/refs/tags/{version}.zip"
        print(f"[DOWNLOAD] 正在下載: {zip_url}")
        
        response = requests.get(zip_url, timeout=30)
        response.raise_for_status()
        
        # 保存文件
        zip_path = Path(f"lightweight-charts-{version}.zip")
        zip_path.write_bytes(response.content)
        
        print(f"[SUCCESS] 下載完成: {zip_path}")
        
        # 解壓到 static 目錄
        extract_dir = Path("static/lightweight-charts")
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_lightweight")
        
        # 找到解壓的目錄
        temp_dir = Path("temp_lightweight")
        for item in temp_dir.iterdir():
            if item.is_dir() and "lightweight-charts" in item.name:
                # 移動 dist 目錄內容
                dist_dir = item / "dist"
                if dist_dir.exists():
                    import shutil
                    if extract_dir.exists():
                        shutil.rmtree(extract_dir)
                    shutil.copytree(dist_dir, extract_dir)
                    print(f"[INSTALL] 安裝到: {extract_dir}")
                break
        
        # 清理
        zip_path.unlink()
        import shutil
        shutil.rmtree(temp_dir)
        
        print("[SUCCESS] Lightweight Charts 安裝完成！")
        return True
        
    except Exception as e:
        print(f"[ERROR] 下載失敗: {e}")
        return False

def create_current_solution():
    """創建當前可用的解決方案"""
    print_header("當前可用解決方案")
    
    print("基於現有限制，我建議以下解決方案：")
    print("\n方案 1: 使用現有模擬版本 (推薦)")
    print("✅ 已安裝並可用")
    print("✅ 支援混合架構測試")
    print("✅ 美股使用 Widget，台股使用自定義實現")
    print("• 位置: static/charting_library/ (已安裝)")
    
    print("\n方案 2: 申請官方權限")
    print("• 適用於正式商業項目")
    print("• 需要等待審核")
    print("• 獲得完整功能")
    
    print("\n方案 3: 使用 Lightweight Charts")
    print("• 開源免費")
    print("• 適用於簡單圖表需求")
    print("• 可立即使用")
    
    return input("\n選擇方案 (1-3) 或 'q' 退出: ").strip()

def test_current_installation():
    """測試當前安裝"""
    print_header("測試當前安裝")
    
    charting_dir = Path("static/charting_library")
    
    if not charting_dir.exists():
        print("[ERROR] Charting Library 目錄不存在")
        return False
    
    required_files = [
        "charting_library.min.js",
        "bundles",
        "datafeeds",
        "static"
    ]
    
    all_exist = True
    for file_name in required_files:
        file_path = charting_dir / file_name
        if file_path.exists():
            print(f"[FOUND] {file_name}")
        else:
            print(f"[MISSING] {file_name}")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] 當前模擬版本可正常使用")
        print("\n測試建議:")
        print("1. 運行: python test_hybrid_simple.py")
        print("2. 啟動服務器: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        print("3. 訪問: http://localhost:8000/chart/hybrid/2330.TW")
        return True
    else:
        print("\n[WARNING] 安裝不完整")
        return False

def open_official_links():
    """開啟官方連結"""
    print_header("開啟官方連結")
    
    links = [
        ("TradingView 官方申請頁面", "https://www.tradingview.com/advanced-charts/"),
        ("Charting Library 文檔", "https://www.tradingview.com/charting-library/"),
        ("Lightweight Charts GitHub", "https://github.com/tradingview/lightweight-charts"),
        ("Tutorial Repository", "https://github.com/tradingview/charting-library-tutorial"),
        ("Examples Repository", "https://github.com/tradingview/charting-library-examples")
    ]
    
    for name, url in links:
        print(f"[LINK] {name}")
        print(f"       {url}")
        try:
            open_link = input(f"       要開啟此連結嗎？ [y/N]: ").strip().lower()
            if open_link == 'y':
                webbrowser.open(url)
                print(f"       [OPENED] 已在瀏覽器中開啟")
        except:
            pass
        print()

def main():
    """主函數"""
    print("TradingView Charting Library 獲取工具")
    print("=" * 60)
    print("[INFO] TradingView Charting Library 主倉庫需要申請權限")
    print("[INFO] 我們有多種解決方案可選")
    
    while True:
        print("\n選項:")
        print("1. 查看官方權限申請流程")
        print("2. 了解 Lightweight Charts 替代方案") 
        print("3. 下載 Lightweight Charts")
        print("4. 測試當前模擬版本")
        print("5. 開啟相關官方連結")
        print("6. 查看可用解決方案總結")
        print("7. 退出")
        
        try:
            choice = input("\n請選擇 (1-7): ").strip()
            
            if choice == "1":
                show_official_access_process()
            elif choice == "2":
                show_lightweight_charts_alternative()
            elif choice == "3":
                success = download_lightweight_charts()
                if success:
                    print("\n[INFO] Lightweight Charts 可用於創建輕量級台股圖表")
            elif choice == "4":
                test_current_installation()
            elif choice == "5":
                open_official_links()
            elif choice == "6":
                result = create_current_solution()
                if result == 'q':
                    break
            elif choice == "7":
                print("再見！")
                break
            else:
                print("[ERROR] 無效選擇")
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            break
        except EOFError:
            print("\n\n操作已取消")
            break

if __name__ == "__main__":
    main()