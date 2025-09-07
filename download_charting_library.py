#!/usr/bin/env python3
"""
從 GitHub 下載 TradingView Charting Library 開發版本
"""

import requests
import zipfile
import shutil
import os
from pathlib import Path
import json

CHARTING_LIBRARY_DIR = Path("static/charting_library")
TEMP_DIR = Path("temp_download")
GITHUB_API_URL = "https://api.github.com/repos/tradingview/charting_library/releases/latest"

def get_latest_release_info():
    """獲取最新版本信息"""
    print("[INFO] 正在獲取最新版本信息...")
    
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        
        release_info = response.json()
        version = release_info["tag_name"]
        
        print(f"[FOUND] 最新版本: {version}")
        print(f"[DATE] 發布日期: {release_info['published_at'][:10]}")
        
        # 查找下載連結
        download_assets = []
        for asset in release_info.get("assets", []):
            if asset["name"].endswith(('.zip', '.tar.gz')):
                download_assets.append({
                    'name': asset["name"],
                    'url': asset["browser_download_url"],
                    'size': asset["size"]
                })
        
        if not download_assets:
            print("[ERROR] 未找到可下載的文件")
            return None
        
        return {
            'version': version,
            'assets': download_assets,
            'html_url': release_info['html_url']
        }
        
    except requests.RequestException as e:
        print(f"[ERROR] 獲取版本信息失敗: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 解析版本信息失敗: {e}")
        return None

def download_file(url, filename):
    """下載文件"""
    print(f"[DOWNLOAD] 正在下載: {filename}")
    print(f"[URL] {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        TEMP_DIR.mkdir(exist_ok=True)
        file_path = TEMP_DIR / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r[PROGRESS] {progress:.1f}% ({downloaded:,}/{total_size:,} bytes)", end='')
        
        print(f"\n[SUCCESS] 下載完成: {file_path}")
        return file_path
        
    except requests.RequestException as e:
        print(f"\n[ERROR] 下載失敗: {e}")
        return None
    except Exception as e:
        print(f"\n[ERROR] 保存文件失敗: {e}")
        return None

def extract_archive(file_path):
    """解壓縮文件"""
    print(f"[EXTRACT] 正在解壓縮: {file_path.name}")
    
    try:
        extract_dir = TEMP_DIR / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        if file_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        else:
            print(f"[ERROR] 不支援的文件格式: {file_path.suffix}")
            return None
        
        print(f"[SUCCESS] 解壓縮完成: {extract_dir}")
        return extract_dir
        
    except Exception as e:
        print(f"[ERROR] 解壓縮失敗: {e}")
        return None

def find_charting_library_files(extract_dir):
    """尋找 Charting Library 文件"""
    print("[SEARCH] 正在尋找 Charting Library 文件...")
    
    # 可能的文件夾名稱
    possible_dirs = [
        "charting_library",
        "charting-library", 
        "dist",
        "build"
    ]
    
    charting_dir = None
    
    # 遞歸搜索 charting_library.min.js
    for root, dirs, files in os.walk(extract_dir):
        if "charting_library.min.js" in files:
            charting_dir = Path(root)
            print(f"[FOUND] Charting Library 目錄: {charting_dir}")
            break
        
        # 檢查可能的目錄名稱
        for possible_dir in possible_dirs:
            if possible_dir in dirs:
                test_dir = Path(root) / possible_dir
                if (test_dir / "charting_library.min.js").exists():
                    charting_dir = test_dir
                    print(f"[FOUND] Charting Library 目錄: {charting_dir}")
                    break
        
        if charting_dir:
            break
    
    if not charting_dir:
        print("[ERROR] 未找到 Charting Library 文件")
        print("[INFO] 可用文件列表:")
        for root, dirs, files in os.walk(extract_dir):
            level = root.replace(str(extract_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # 只顯示前5個文件
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... 還有 {len(files) - 5} 個文件")
        return None
    
    return charting_dir

def install_charting_library(source_dir):
    """安裝 Charting Library"""
    print(f"[INSTALL] 正在安裝到: {CHARTING_LIBRARY_DIR}")
    
    try:
        # 備份現有文件（如果存在）
        if CHARTING_LIBRARY_DIR.exists():
            backup_dir = Path("static/charting_library_backup")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.move(str(CHARTING_LIBRARY_DIR), str(backup_dir))
            print(f"[BACKUP] 已備份現有文件到: {backup_dir}")
        
        # 複製新文件
        shutil.copytree(str(source_dir), str(CHARTING_LIBRARY_DIR))
        
        # 驗證安裝
        required_files = [
            "charting_library.min.js",
            "bundles",
            "datafeeds", 
            "static"
        ]
        
        missing_files = []
        for file_name in required_files:
            file_path = CHARTING_LIBRARY_DIR / file_name
            if file_path.exists():
                print(f"[VERIFIED] {file_name}")
            else:
                missing_files.append(file_name)
                print(f"[MISSING] {file_name}")
        
        if missing_files:
            print(f"[WARNING] 缺少部分文件: {', '.join(missing_files)}")
            return False
        else:
            print("[SUCCESS] TradingView Charting Library 安裝完成")
            return True
            
    except Exception as e:
        print(f"[ERROR] 安裝失敗: {e}")
        return False

def cleanup():
    """清理臨時文件"""
    if TEMP_DIR.exists():
        print("[CLEANUP] 清理臨時文件...")
        shutil.rmtree(TEMP_DIR)
        print("[SUCCESS] 清理完成")

def main():
    """主函數"""
    print("TradingView Charting Library GitHub 下載器")
    print("=" * 60)
    print("[WARNING] 此版本僅用於開發測試")
    print("[WARNING] 商業使用需要購買官方授權")
    
    try:
        # 1. 獲取版本信息
        release_info = get_latest_release_info()
        if not release_info:
            return False
        
        print(f"\n[RELEASE] GitHub Release 頁面: {release_info['html_url']}")
        
        # 2. 選擇下載文件
        assets = release_info['assets']
        if len(assets) == 1:
            selected_asset = assets[0]
            print(f"[AUTO] 自動選擇: {selected_asset['name']}")
        else:
            print("\n[SELECT] 可用下載:")
            for i, asset in enumerate(assets):
                size_mb = asset['size'] / (1024 * 1024)
                print(f"  {i + 1}. {asset['name']} ({size_mb:.1f} MB)")
            
            while True:
                try:
                    choice = int(input("\n請選擇下載文件 (1-{}): ".format(len(assets))))
                    if 1 <= choice <= len(assets):
                        selected_asset = assets[choice - 1]
                        break
                    else:
                        print("[ERROR] 無效選擇")
                except ValueError:
                    print("[ERROR] 請輸入數字")
        
        # 3. 下載文件
        downloaded_file = download_file(selected_asset['url'], selected_asset['name'])
        if not downloaded_file:
            return False
        
        # 4. 解壓縮
        extract_dir = extract_archive(downloaded_file)
        if not extract_dir:
            return False
        
        # 5. 尋找 Charting Library 文件
        charting_dir = find_charting_library_files(extract_dir)
        if not charting_dir:
            return False
        
        # 6. 安裝
        success = install_charting_library(charting_dir)
        
        # 7. 清理
        cleanup()
        
        if success:
            print("\n[COMPLETE] 安裝完成！")
            print("\n[NEXT] 下一步:")
            print("  1. 運行測試: python test_hybrid_simple.py")
            print("  2. 啟動服務器: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
            print("  3. 測試頁面: http://localhost:8000/chart/hybrid/2330.TW")
            return True
        else:
            print("\n[ERROR] 安裝失敗")
            return False
            
    except KeyboardInterrupt:
        print("\n\n[CANCEL] 下載已取消")
        cleanup()
        return False
    except Exception as e:
        print(f"\n[ERROR] 未預期的錯誤: {e}")
        cleanup()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)