#!/usr/bin/env python3
"""
TradingView Charting Library 設置工具 (簡化版)
避免 Unicode 編碼問題
"""

import os
import sys
from pathlib import Path

CHARTING_LIBRARY_DIR = Path("static/charting_library")

def check_installation():
    """檢查安裝狀態"""
    print("\n[CHECK] 檢查 TradingView Charting Library 安裝狀態")
    print("=" * 60)
    
    required_files = [
        "charting_library.min.js",
        "bundles",
        "datafeeds",
        "static"
    ]
    
    if not CHARTING_LIBRARY_DIR.exists():
        print("[INFO] Charting Library 目錄不存在")
        CHARTING_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
        print("[CREATED] 已創建目錄:", CHARTING_LIBRARY_DIR.absolute())
    
    missing_files = []
    existing_files = []
    
    for file_name in required_files:
        file_path = CHARTING_LIBRARY_DIR / file_name
        if file_path.exists():
            existing_files.append(file_name)
            print(f"[FOUND] {file_name}")
        else:
            missing_files.append(file_name)
            print(f"[MISSING] {file_name}")
    
    if not missing_files:
        print("\n[SUCCESS] TradingView Charting Library 已正確安裝")
        return True
    else:
        print(f"\n[WARNING] 缺少 {len(missing_files)} 個必要文件")
        return False

def create_mock_files():
    """創建測試用模擬文件"""
    print("\n[SETUP] 創建模擬文件用於開發測試")
    print("=" * 60)
    print("[WARNING] 這些是測試用模擬文件")
    print("[WARNING] 生產環境需要官方授權版本")
    
    # 創建目錄
    (CHARTING_LIBRARY_DIR / "bundles").mkdir(parents=True, exist_ok=True)
    (CHARTING_LIBRARY_DIR / "datafeeds" / "udf").mkdir(parents=True, exist_ok=True)
    (CHARTING_LIBRARY_DIR / "static").mkdir(parents=True, exist_ok=True)
    
    # 創建主要 JS 文件 (模擬版本)
    mock_js_content = """
/* TradingView Charting Library - Mock Version for Testing */
console.log('TradingView Charting Library Mock Version Loaded');

window.TradingView = window.TradingView || {};

window.TradingView.widget = function(options) {
    console.log('TradingView Widget Mock Initialized', options);
    
    var containerId = options.container_id || 'tv_chart_container';
    var container = document.getElementById(containerId);
    
    if (container) {
        container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #1e222d; color: #fff; font-family: Arial;">' +
            '<div style="text-align: center;">' +
            '<h3>TradingView Charting Library (模擬版)</h3>' +
            '<p>符號: ' + (options.symbol || 'N/A') + '</p>' +
            '<p>這是測試用模擬版本</p>' +
            '<p>生產環境需要官方授權版本</p>' +
            '</div>' +
            '</div>';
    }
    
    return {
        onChartReady: function(callback) {
            setTimeout(function() {
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

window.Datafeeds = window.Datafeeds || {};
window.Datafeeds.UDFCompatibleDatafeed = function(datafeedUrl) {
    console.log('UDF Datafeed Mock:', datafeedUrl);
    return {};
};

console.log('TradingView Mock Library Ready');
"""
    
    # 寫入文件
    (CHARTING_LIBRARY_DIR / "charting_library.min.js").write_text(
        mock_js_content, encoding='utf-8'
    )
    
    (CHARTING_LIBRARY_DIR / "bundles" / "README.txt").write_text(
        "Mock bundles directory"
    )
    
    (CHARTING_LIBRARY_DIR / "datafeeds" / "udf" / "README.txt").write_text(
        "Mock UDF datafeeds"
    )
    
    (CHARTING_LIBRARY_DIR / "static" / "README.txt").write_text(
        "Mock static resources"
    )
    
    print(f"[CREATED] {CHARTING_LIBRARY_DIR / 'charting_library.min.js'}")
    print(f"[CREATED] {CHARTING_LIBRARY_DIR / 'bundles'}")
    print(f"[CREATED] {CHARTING_LIBRARY_DIR / 'datafeeds'}")
    print(f"[CREATED] {CHARTING_LIBRARY_DIR / 'static'}")
    print("\n[SUCCESS] 模擬文件創建完成")

def show_installation_guide():
    """顯示安裝指南"""
    print("\n[GUIDE] TradingView Charting Library 安裝指南")
    print("=" * 60)
    
    print("\n[IMPORTANT] 授權要求:")
    print("• TradingView Charting Library 需要購買授權")
    print("• 商業使用必須獲得官方授權")
    print("• 開發測試可使用 GitHub 版本")
    
    print(f"\n[LOCATION] 安裝位置:")
    print(f"  {CHARTING_LIBRARY_DIR.absolute()}")
    
    print(f"\n[STRUCTURE] 需要的文件結構:")
    print("  charting_library/")
    print("  ├── charting_library.min.js")
    print("  ├── bundles/")
    print("  ├── datafeeds/")
    print("  │   └── udf/")
    print("  └── static/")
    
    print(f"\n[SOURCES] 獲取方式:")
    print("  1. 官方購買: https://www.tradingview.com/charting-library/")
    print("  2. GitHub (開發版): https://github.com/tradingview/charting_library/releases")
    
    print(f"\n[COMMANDS] 手動下載示例:")
    print("  # 下載到當前目錄")
    print("  curl -L -o charting_library.zip [GitHub下載連結]")
    print("  unzip charting_library.zip -d static/")

def test_integration():
    """測試系統整合"""
    print("\n[TEST] 測試系統整合")
    print("=" * 60)
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.visualization.hybrid_tradingview import get_hybrid_chart
        
        chart = get_hybrid_chart()
        
        print("[TEST] 測試台股圖表生成...")
        html_content = chart.create_hybrid_chart("2330.TW", theme="dark")
        
        if "charting_library.min.js" in html_content:
            print("[PASS] 台股 Charting Library 整合")
        else:
            print("[FAIL] 台股 Charting Library 整合")
            return False
        
        print("[TEST] 測試美股圖表生成...")
        html_content = chart.create_hybrid_chart("AAPL", theme="dark")
        
        if "TradingView.widget" in html_content and "s3.tradingview.com" in html_content:
            print("[PASS] 美股 Widget 整合")
        else:
            print("[FAIL] 美股 Widget 整合")
            return False
        
        print("\n[SUCCESS] 所有整合測試通過")
        return True
        
    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("TradingView Charting Library 設置工具")
    print("=" * 60)
    
    # 檢查當前安裝狀態
    is_installed = check_installation()
    
    if is_installed:
        print("\n[INFO] Charting Library 已安裝")
        test_integration()
    else:
        print("\n[OPTION] 選擇設置方式:")
        print("1. 創建模擬文件 (用於開發測試)")
        print("2. 顯示手動安裝指南")
        print("3. 退出")
        
        try:
            choice = input("\n請選擇 (1-3): ").strip()
            
            if choice == "1":
                create_mock_files()
                print("\n[NEXT] 運行測試:")
                print("  python test_hybrid_simple.py")
                
            elif choice == "2":
                show_installation_guide()
                
            elif choice == "3":
                print("再見!")
                
            else:
                print("[ERROR] 無效選擇")
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
        except EOFError:
            print("\n\n操作已取消")

if __name__ == "__main__":
    main()