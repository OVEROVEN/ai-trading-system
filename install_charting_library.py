#!/usr/bin/env python3
"""
TradingView Charting Library 安裝輔助工具
此腳本提供多種安裝方式和檢查功能
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
import json

CHARTING_LIBRARY_DIR = Path("static/charting_library")
GITHUB_API_URL = "https://api.github.com/repos/tradingview/charting_library/releases/latest"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"📚 {title}")
    print('='*60)

def print_warning():
    print_header("重要授權說明")
    print("⚠️  TradingView Charting Library 需要授權")
    print("   • 商業使用必須購買官方授權")
    print("   • 開發測試版本功能有限制")
    print("   • 請遵守 TradingView 使用條款")
    print("\n官方網站: https://www.tradingview.com/charting-library/")

def check_existing_installation():
    """檢查現有安裝"""
    print_header("檢查現有安裝")
    
    required_files = [
        "charting_library.min.js",
        "bundles",
        "datafeeds",
        "static"
    ]
    
    if not CHARTING_LIBRARY_DIR.exists():
        print("❌ Charting Library 目錄不存在")
        return False
    
    missing_files = []
    for file_name in required_files:
        file_path = CHARTING_LIBRARY_DIR / file_name
        if not file_path.exists():
            missing_files.append(file_name)
        else:
            print(f"✅ 找到: {file_name}")
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Charting Library 已正確安裝")
        return True

def download_development_version():
    """下載開發測試版本"""
    print_header("下載開發測試版本")
    print("⚠️  此版本僅用於開發測試，商業使用需購買授權")
    
    try:
        print("正在獲取最新版本資訊...")
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        
        release_info = response.json()
        version = release_info["tag_name"]
        
        print(f"最新版本: {version}")
        
        # 找到下載連結
        download_url = None
        for asset in release_info.get("assets", []):
            if asset["name"].endswith(".zip"):
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            print("❌ 未找到下載連結")
            return False
        
        print(f"下載連結: {download_url}")
        print("正在下載...")
        
        # 下載文件
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        # 保存到臨時文件
        temp_zip = Path("charting_library_temp.zip")
        temp_zip.write_bytes(response.content)
        
        print("正在解壓縮...")
        
        # 解壓縮
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(CHARTING_LIBRARY_DIR.parent)
        
        # 清理臨時文件
        temp_zip.unlink()
        
        print("✅ 下載並安裝成功")
        return True
        
    except requests.RequestException as e:
        print(f"❌ 下載失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 安裝失敗: {e}")
        return False

def create_mock_files():
    """創建模擬文件用於測試"""
    print_header("創建模擬文件")
    print("創建基本的模擬文件用於系統測試...")
    
    # 創建主要 JS 文件 (模擬)
    main_js_content = """
/* TradingView Charting Library - Mock Version for Testing */
/* 此為測試用模擬文件，實際部署需要官方授權版本 */

console.log('TradingView Charting Library Mock Version Loaded');

// 模擬 TradingView 物件
window.TradingView = window.TradingView || {};

window.TradingView.widget = function(options) {
    console.log('TradingView Widget Mock Initialized', options);
    
    // 模擬基本功能
    return {
        onChartReady: function(callback) {
            setTimeout(() => {
                console.log('Chart Ready (Mock)');
                if (callback) callback();
            }, 1000);
        },
        chart: function() {
            return {
                createStudy: function(name, visible, inputs) {
                    console.log('Creating study:', name);
                }
            };
        },
        subscribe: function(event, callback) {
            console.log('Subscribed to:', event);
        }
    };
};

// 模擬數據源
window.Datafeeds = window.Datafeeds || {};
window.Datafeeds.UDFCompatibleDatafeed = function(datafeedUrl) {
    console.log('UDF Datafeed Mock:', datafeedUrl);
    return {};
};
"""
    
    # 創建目錄結構
    (CHARTING_LIBRARY_DIR / "bundles").mkdir(exist_ok=True)
    (CHARTING_LIBRARY_DIR / "datafeeds" / "udf").mkdir(parents=True, exist_ok=True)
    (CHARTING_LIBRARY_DIR / "static").mkdir(exist_ok=True)
    
    # 寫入主要文件
    (CHARTING_LIBRARY_DIR / "charting_library.min.js").write_text(
        main_js_content, encoding='utf-8'
    )
    
    # 創建其他必要文件
    (CHARTING_LIBRARY_DIR / "bundles" / "README.txt").write_text(
        "Mock bundles directory - 模擬資源包目錄"
    )
    
    (CHARTING_LIBRARY_DIR / "datafeeds" / "udf" / "README.txt").write_text(
        "Mock UDF datafeeds - 模擬 UDF 數據源"
    )
    
    (CHARTING_LIBRARY_DIR / "static" / "README.txt").write_text(
        "Mock static resources - 模擬靜態資源"
    )
    
    print("✅ 模擬文件創建完成")
    print("⚠️  這些是測試用模擬文件，實際使用需要官方授權版本")

def show_manual_installation():
    """顯示手動安裝說明"""
    print_header("手動安裝說明")
    
    print("📋 手動安裝步驟:")
    print("1. 從官方或 GitHub 獲取 Charting Library 文件")
    print("2. 將文件放置到以下目錄:")
    print(f"   {CHARTING_LIBRARY_DIR.absolute()}")
    print("\n📁 需要的文件結構:")
    print("   charting_library/")
    print("   ├── charting_library.min.js     # 主要庫文件")
    print("   ├── bundles/                    # 資源包")
    print("   ├── datafeeds/                  # 數據源示例")
    print("   │   └── udf/                    # UDF 兼容層")
    print("   └── static/                     # 靜態資源")
    
    print(f"\n🔗 相關連結:")
    print("   官方購買: https://www.tradingview.com/charting-library/")
    print("   GitHub (開發版): https://github.com/tradingview/charting_library/releases")

def test_installation():
    """測試安裝"""
    print_header("測試安裝")
    
    if not check_existing_installation():
        print("❌ 安裝檢查失敗")
        return False
    
    print("正在測試系統整合...")
    
    try:
        # 測試混合圖表
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.visualization.hybrid_tradingview import get_hybrid_chart
        
        chart = get_hybrid_chart()
        
        # 測試台股圖表生成
        html_content = chart.create_hybrid_chart("2330.TW", theme="dark")
        
        if "charting_library.min.js" in html_content:
            print("✅ 台股 Charting Library 整合測試通過")
        else:
            print("❌ 台股 Charting Library 整合測試失敗")
            return False
        
        # 測試美股圖表生成
        html_content = chart.create_hybrid_chart("AAPL", theme="dark")
        
        if "TradingView.widget" in html_content:
            print("✅ 美股 Widget 整合測試通過")
        else:
            print("❌ 美股 Widget 整合測試失敗")
            return False
        
        print("✅ 所有整合測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("TradingView Charting Library 安裝工具")
    print_warning()
    
    while True:
        print("\n📋 選擇安裝方式:")
        print("1. 檢查現有安裝")
        print("2. 下載開發測試版本 (GitHub)")
        print("3. 創建模擬文件用於測試")
        print("4. 顯示手動安裝說明")
        print("5. 測試安裝")
        print("6. 退出")
        
        choice = input("\n請選擇 (1-6): ").strip()
        
        if choice == "1":
            check_existing_installation()
        elif choice == "2":
            confirm = input("確定要下載開發版本嗎？(僅用於開發測試) [y/N]: ")
            if confirm.lower() == 'y':
                download_development_version()
        elif choice == "3":
            confirm = input("確定要創建模擬文件嗎？[y/N]: ")
            if confirm.lower() == 'y':
                create_mock_files()
        elif choice == "4":
            show_manual_installation()
        elif choice == "5":
            test_installation()
        elif choice == "6":
            print("再見！")
            break
        else:
            print("❌ 無效選擇，請重新輸入")

if __name__ == "__main__":
    main()