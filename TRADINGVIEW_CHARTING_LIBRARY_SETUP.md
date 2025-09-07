# TradingView Charting Library 設置指南

## 🎯 概述

本指南將協助您設置 TradingView Charting Library 以支援台股數據顯示。我們的混合架構中，美股使用 TradingView Widget，台股使用 Charting Library + TWSE/TPEx 開放資料。

## ⚠️ 重要說明

**TradingView Charting Library 需要授權**
- 這不是免費的開源軟件
- 需要從 TradingView 官方購買授權
- 用於商業用途需要付費許可證

## 📋 前置需求

### 1. 獲取 TradingView Charting Library

有兩種方式獲取：

#### 方式一：官方購買 (推薦)
1. 前往 [TradingView Charting Library](https://www.tradingview.com/charting-library/)
2. 聯繫 TradingView 銷售團隊
3. 購買適合的授權方案
4. 下載正式版本

#### 方式二：開發測試版本
1. 前往 [GitHub Release](https://github.com/tradingview/charting_library/releases)
2. 下載最新的 `charting_library.standalone.js`
3. ⚠️ 此版本僅用於開發測試，商業使用需購買授權

### 2. 檢查系統需求

```bash
# Node.js 版本 (建議 16+)
node --version

# Python 版本 (建議 3.8+)
python --version

# FastAPI 相關套件
pip list | grep fastapi
```

## 🚀 安裝步驟

### 步驟 1：創建靜態文件目錄

```bash
# 在項目根目錄下創建靜態文件夾
mkdir -p static/charting_library
cd static/charting_library
```

### 步驟 2：放置 Charting Library 文件

將下載的 TradingView Charting Library 文件放置如下：

```
static/
└── charting_library/
    ├── charting_library.min.js     # 主要庫文件
    ├── bundles/                    # 資源包
    ├── datafeeds/                  # 數據源示例
    │   └── udf/                    # UDF 兼容層
    ├── static/                     # 靜態資源
    └── custom.css                  # 自定義樣式 (可選)
```

### 步驟 3：配置 FastAPI 靜態文件服務

編輯 `src/api/main.py`：

```python
from fastapi.staticfiles import StaticFiles

# 添加靜態文件服務
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 步驟 4：創建 .gitkeep 文件

```bash
# 確保目錄結構被追踪但不追踪大文件
touch static/charting_library/.gitkeep
echo "charting_library/" >> static/charting_library/.gitkeep
```

## 🔧 配置設定

### 1. 環境變量配置

在 `.env` 文件中添加：

```env
# TradingView Charting Library
TRADINGVIEW_CHARTING_ENABLED=true
TRADINGVIEW_CHARTING_VERSION=20.043

# 台股數據源配置
TWSE_API_BASE=https://www.twse.com.tw/exchangeReport/
TPEX_API_BASE=https://www.tpex.org.tw/web/stock/
```

### 2. 自定義樣式 (可選)

創建 `static/charting_library/custom.css`：

```css
/* 深色主題自定義 */
.chart-container {
    background-color: #1e222d;
}

.tv-lightweight-charts {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 台股專用顏色 */
.tw-stock-up {
    color: #089981;
}

.tw-stock-down {
    color: #f23645;
}
```

## 📊 驗證安裝

### 1. 檢查文件結構

```bash
# 確認文件結構
ls -la static/charting_library/
```

應該看到：
```
charting_library.min.js
bundles/
datafeeds/
static/
```

### 2. 測試 API 端點

```bash
# 啟動服務器
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 測試 Charting Library 配置端點
curl http://localhost:8000/api/charting/config

# 測試台股符號解析
curl http://localhost:8000/api/charting/symbols/2330.TW
```

### 3. 測試混合圖表

```bash
# 測試美股 (TradingView Widget)
curl http://localhost:8000/chart/hybrid/AAPL

# 測試台股 (Charting Library)
curl http://localhost:8000/chart/hybrid/2330.TW
```

## 🎨 使用方法

### 1. 基本使用

```python
# 使用混合圖表
from src.visualization.hybrid_tradingview import get_hybrid_chart

chart = get_hybrid_chart()

# 美股 - 自動使用 Widget
us_chart = chart.create_hybrid_chart("AAPL")

# 台股 - 自動使用 Charting Library
tw_chart = chart.create_hybrid_chart("2330.TW")
```

### 2. 高級配置

```python
# 自定義主題和數據
chart_html = chart.create_hybrid_chart(
    symbol="2330.TW",
    theme="dark",
    stock_data=stock_data,
    ai_recommendations=ai_recommendations,
    strategy_info=strategy_info
)
```

## 🚨 常見問題

### Q1: Charting Library 無法載入
**原因**: 文件路徑錯誤或文件不存在

**解決方案**:
```bash
# 檢查文件是否存在
ls -la static/charting_library/charting_library.min.js

# 檢查 FastAPI 靜態文件配置
curl http://localhost:8000/static/charting_library/charting_library.min.js
```

### Q2: 台股數據無法顯示
**原因**: TWSE/TPEx API 連接問題

**解決方案**:
```bash
# 測試台股數據獲取
python -c "
import asyncio
from src.data_fetcher.twse_tpex_datafeed import get_taiwan_datafeed

async def test():
    datafeed = get_taiwan_datafeed()
    info = await datafeed.get_symbol_info('2330.TW')
    print(info)

asyncio.run(test())
"
```

### Q3: 符號切換功能不正常
**原因**: 市場檢測邏輯錯誤

**解決方案**:
```python
# 測試符號檢測
from src.visualization.hybrid_tradingview import get_hybrid_chart

chart = get_hybrid_chart()
print(f"AAPL 是台股: {chart.is_taiwan_stock('AAPL')}")      # False
print(f"2330.TW 是台股: {chart.is_taiwan_stock('2330.TW')}")  # True
```

### Q4: JavaScript 錯誤
**原因**: TradingView 對象未正確載入

**解決方案**: 檢查瀏覽器控制台，確認：
1. `charting_library.min.js` 成功載入
2. `TradingView.widget` 對象可用
3. 沒有 CORS 錯誤

## 📚 API 文檔

### Charting Library 端點

```
GET  /api/charting/config           # 配置信息
GET  /api/charting/symbols          # 符號搜尋
GET  /api/charting/symbols/{symbol} # 符號解析
GET  /api/charting/history          # 歷史數據
GET  /api/charting/server_time      # 服務器時間
```

### 混合圖表端點

```
GET  /chart/hybrid/{symbol}         # 混合圖表 (自動檢測市場)
POST /chart/hybrid/{symbol}         # 帶數據的混合圖表
```

## 🔍 除錯指南

### 1. 啟用除錯模式

```python
# 在 src/api/main.py 中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 檢查數據流

```bash
# 檢查 TWSE 數據
curl "http://localhost:8000/api/charting/test/2330.TW"

# 檢查歷史數據
curl "http://localhost:8000/api/charting/history?symbol=2330.TW&from=1704067200&to=1704153600&resolution=1D"
```

### 3. 瀏覽器開發者工具

1. 開啟瀏覽器開發者工具 (F12)
2. 檢查 Console 是否有 JavaScript 錯誤
3. 檢查 Network 頁籤確認 API 請求
4. 確認靜態文件正確載入

## 🎯 性能優化

### 1. 快取配置

```python
# 在 src/data_fetcher/twse_tpex_datafeed.py 中調整
self.cache_ttl = 300  # 5分鐘快取
```

### 2. 並發請求優化

```python
# 使用 aiohttp 的連接池
async with aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(limit=10)
) as session:
    # API 請求
```

## 📖 進階功能

### 1. 自定義指標

可以在 Charting Library 中添加自定義技術指標：

```javascript
// 在 hybrid_tradingview.py 的 JavaScript 部分
widget.onChartReady(() => {
    // 添加自定義 RSI
    widget.chart().createStudy('RSI', false, false, [14], null, {
        'RSI.RSI.color': '#2196F3'
    });
});
```

### 2. 即時數據更新

```python
# WebSocket 支援 (未來功能)
@app.websocket("/ws/taiwan/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    # 即時數據推送邏輯
```

## 🚀 部署建議

### 1. 生產環境

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 2. Docker 部署

```dockerfile
# 在現有 Dockerfile 中添加
COPY static/ /app/static/
EXPOSE 8000
```

### 3. CDN 配置

考慮將靜態文件放到 CDN：

```python
# 配置 CDN URL
CHARTING_LIBRARY_CDN = "https://your-cdn.com/charting_library/"
```

## 📝 授權和合規

### 重要提醒

1. **商業使用**: 必須購買 TradingView 授權
2. **開放數據**: TWSE/TPEx 數據使用符合開放資料規範
3. **版權遵守**: 不得違反 TradingView 的使用條款

### 授權檢查

```bash
# 檢查授權狀態 (如果已配置)
curl http://localhost:8000/api/license/status
```

---

## 🎉 完成設定

設定完成後，您的系統將支援：

✅ **美股**: TradingView Widget (即時數據)  
✅ **台股**: Charting Library + TWSE/TPEx 開放資料  
✅ **自動切換**: 根據符號格式自動選擇渲染方式  
✅ **合規性**: 完全符合台股開放資料使用規範  

如有問題，請參考常見問題部分或檢查系統日誌。