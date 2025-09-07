# 🚀 如何啟動台股整合交易系統

## 🎯 最快啟動方式 (推薦)

```bash
# 1. 進入專案目錄
cd C:\Users\user\Undemy\auto_trade

# 2. 啟動台股整合系統
uv run python start_taiwan_system.py
```

這會自動：
- ✅ 檢查依賴項
- ✅ 啟動 API 服務器 
- ✅ 打開瀏覽器到 API 文檔
- ✅ 顯示新台股功能介紹

## 🌐 訪問方式

啟動後可以訪問：

### 📊 API 文檔 (主要介面)
```
http://localhost:8000/docs
```

### 📈 TradingView 圖表範例
```
# 台積電圖表
http://localhost:8000/chart/custom/2330.TW

# 鴻海圖表  
http://localhost:8000/chart/custom/2317.TW

# Apple 圖表
http://localhost:8000/chart/custom/AAPL
```

### 🇹🇼 台股API測試
```
# 台股市場總覽
GET http://localhost:8000/api/taiwan/market-overview

# 搜尋台積電
GET http://localhost:8000/api/taiwan/stocks/search?query=台積

# 台積電資訊
GET http://localhost:8000/api/taiwan/stocks/2330.TW/info
```

## 🔄 其他啟動方式

### 方式一：傳統啟動
```bash
uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 方式二：原系統選單
```bash
uv run python start_system.py
```

### 方式三：直接啟動 (不用 uv)
```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🛠️ 如果遇到問題

### 依賴項問題
```bash
# 安裝基本依賴
uv add fastapi uvicorn pandas yfinance pytz

# 安裝台股數據源 (可選，但推薦)
uv add twstock

# 安裝 Redis 快取 (可選)
uv add redis
```

### 端口占用
如果 8000 端口被占用，修改啟動命令：
```bash
uv run python -m uvicorn src.api.main:app --reload --port 8001
```

### 權限問題
Windows 上可能需要管理員權限，或者使用：
```bash
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

## 🎯 快速測試新功能

1. **啟動系統** (選擇上面任一方式)

2. **打開瀏覽器** 到 http://localhost:8000/docs

3. **測試台股搜尋**:
   - 找到 `/api/taiwan/stocks/search`
   - 點擊 "Try it out"
   - 輸入 `query: 台積`
   - 點擊 "Execute"

4. **測試市場切換**:
   - 找到 `/api/market/switch`
   - 點擊 "Try it out"  
   - 輸入 `{"market": "TW"}`
   - 點擊 "Execute"

5. **查看圖表**:
   - 訪問 http://localhost:8000/chart/custom/2330.TW
   - 應該看到台積電的 TradingView 圖表

## 📊 新功能亮點

### 🇹🇼 台股支援
- ✅ 自動符號偵測 (`2330` → `2330.TW`)
- ✅ 上市/上櫃區分 (`.TW` / `.TWO`)
- ✅ 即時報價與歷史數據
- ✅ 台股交易時間感知

### 📈 TradingView 整合
- ✅ 完整 Datafeed 支援
- ✅ 美股/台股統一介面
- ✅ K線、成交量、RSI 顯示
- ✅ 響應式設計

### 🔄 智慧市場切換
- ✅ 自動偵測最佳市場
- ✅ 交易時間狀態監控
- ✅ 符號格式標準化

### 💾 多層快取系統
- ✅ 記憶體 → Redis → 檔案
- ✅ 智慧 TTL 管理
- ✅ 效能大幅提升

## 🆘 需要幫助？

如果遇到任何問題：

1. **檢查控制台輸出** - 看是否有錯誤訊息
2. **檢查依賴項** - 運行 `start_taiwan_system.py` 會自動檢查
3. **檢查端口** - 確認 8000 端口未被佔用
4. **重新啟動** - 停止服務器 (Ctrl+C) 並重新啟動

## 🎉 開始探索！

台股整合系統已就緒，包含：
- 🇺🇸 美股支援 (原有功能)
- 🇹🇼 台股完整支援 (新功能)  
- 📊 TradingView 專業圖表
- 🤖 AI 分析與建議
- 📈 策略回測
- 💾 智慧快取

立即開始：`uv run python start_taiwan_system.py` 🚀