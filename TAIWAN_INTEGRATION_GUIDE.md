# 🇹🇼 Taiwan Stock Market Integration Guide

## 📋 完整實現方案總覽

基於您的需求清單，我已完成台股+美股統一前端的完整架構設計與實現：

### ✅ 已完成的核心組件

1. **TradingView Datafeed 架構** (`src/visualization/tradingview_datafeed.py`)
   - 完整支援 TradingView Charting Library
   - 統一美股/台股 datafeed 介面
   - 符號解析、搜尋、歷史數據獲取
   - 時區處理（台北/紐約）

2. **台股專用API端點** (`src/api/taiwan_endpoints.py`)
   - 市場總覽、個股資訊、即時報價
   - 歷史數據與技術指標
   - 搜尋功能、熱門股票
   - RESTful API 設計

3. **統一快取策略** (`src/cache/unified_cache.py`)
   - 多層快取：記憶體 -> Redis -> 檔案系統
   - 智慧 TTL 管理
   - 台股/美股交易時間感知
   - 自動清理過期數據

4. **市場切換機制** (`src/frontend/market_switcher.py`)
   - 美股/台股無縫切換
   - 自動市場偵測
   - 交易時間狀態監控
   - 符號格式標準化

5. **符號命名規範** (已整合到所有組件)
   - **上市 (TWSE)**: `2330.TW` (台積電)
   - **上櫃 (TPEx)**: `3481.TWO` (群創)
   - **美股**: 直接符號 (`AAPL`, `GOOGL`)

## 🚀 快速部署指南

### 1. 安裝新的依賴項

```bash
# 安裝台股數據庫 (您的系統已有 twstock)
uv add twstock yfinance

# Redis 快取 (可選)
uv add redis

# 時區處理
uv add pytz
```

### 2. 整合到現有 API

在 `src/api/main.py` 中加入新的路由：

```python
# 添加import
from src.api.taiwan_endpoints import setup_taiwan_routes
from src.frontend.market_switcher import get_market_switcher
from src.cache.unified_cache import get_cache

# 設定台股路由
setup_taiwan_routes(app)

# 市場切換端點
@app.post("/api/market/switch")
async def switch_market(request: dict):
    market_type = request.get("market", "AUTO")
    switcher = get_market_switcher()
    result = switcher.switch_market(market_type)
    return result

@app.get("/api/market/info")
async def get_market_info():
    switcher = get_market_switcher()
    return switcher.get_current_market_info()
```

### 3. 更新您的自定義 TradingView 圖表

修改 `src/visualization/custom_tradingview.py`：

```python
# 在 create_trading_chart 方法開頭加入市場切換器
from ..frontend.market_switcher import get_market_switcher

def create_trading_chart(self, symbol: str, ...):
    # 市場自動偵測與切換
    switcher = get_market_switcher()
    normalized_symbol = switcher.normalize_symbol_for_market(symbol)
    tradingview_symbol = switcher.get_tradingview_symbol(normalized_symbol)
    market_info = switcher.get_current_market_info()
    
    # 在 HTML 中加入市場切換器
    market_switch_html = switcher.create_market_switch_html()
    
    # 將 market_switch_html 插入到 HTML 模板中...
```

## 📊 新增API端點說明

### 台股專用端點

```bash
# 市場總覽
GET /api/taiwan/market-overview

# 搜尋台股
GET /api/taiwan/stocks/search?query=台積電&market=TWSE&limit=10

# 個股資訊
GET /api/taiwan/stocks/2330.TW/info

# 即時報價
GET /api/taiwan/stocks/2330.TW/quote

# 歷史數據
POST /api/taiwan/stocks/2330.TW/historical
{
  "period": "3mo",
  "include_indicators": true,
  "indicators": ["sma_20", "sma_50", "rsi", "macd"]
}

# 熱門股票
GET /api/taiwan/stocks/popular
```

### TradingView Datafeed 端點

```bash
# 配置
GET /api/tradingview/config

# 搜尋符號
GET /api/tradingview/symbols?query=2330&exchange=TWSE

# 符號資訊
GET /api/tradingview/symbols/2330.TW

# 歷史K線
GET /api/tradingview/history?symbol=2330.TW&resolution=1D&from=1640995200&to=1672531200

# 服務器時間
GET /api/tradingview/time
```

### 市場切換端點

```bash
# 切換市場
POST /api/market/switch
{"market": "TW"}  # US, TW, AUTO

# 獲取市場資訊
GET /api/market/info
```

## 🎯 前端整合範例

### JavaScript 市場切換

```javascript
// 切換到台股
async function switchToTaiwan() {
    const response = await fetch('/api/market/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ market: 'TW' })
    });
    
    const result = await response.json();
    if (result.success) {
        // 更新UI, 重新載入股票清單等
        updateStockList(result.default_symbols);
    }
}

// 自動偵測符號市場
function detectSymbolMarket(symbol) {
    if (symbol.endsWith('.TW') || symbol.endsWith('.TWO')) {
        return 'TW';
    } else if (/^\d{4}$/.test(symbol)) {
        return 'TW';  // 4位數字預設為台股
    } else {
        return 'US';
    }
}
```

### 統一符號處理

```javascript
// 標準化符號函數
function normalizeSymbol(symbol, targetMarket) {
    if (targetMarket === 'TW') {
        if (/^\d{4}$/.test(symbol)) {
            return symbol + '.TW';  // 2330 -> 2330.TW
        }
    }
    return symbol.toUpperCase();
}

// TradingView 符號轉換
function getTradingViewSymbol(symbol) {
    if (symbol.endsWith('.TW')) {
        const code = symbol.substring(0, 4);
        return `TPE:${code}`;
    } else if (symbol.endsWith('.TWO')) {
        const code = symbol.substring(0, 4);
        return `TPX:${code}`;
    }
    return symbol;
}
```

## 🔧 配置與優化

### 快取配置

在 `config/settings.py` 中加入：

```python
# 快取設定
CACHE_SETTINGS = {
    "memory_ttl_seconds": 300,      # 5分鐘記憶體快取
    "redis_enabled": False,         # Redis 快取開關
    "redis_url": "redis://localhost:6379/0",
    "file_cache_enabled": True,     # 檔案快取開關
    "historical_data_ttl": 14400,   # 歷史資料快取4小時
    "realtime_data_ttl": 30,        # 即時資料快取30秒
}
```

### 台股交易時間設定

```python
# 台股交易時間配置
TAIWAN_MARKET_HOURS = {
    "regular": {
        "open": "09:00",
        "close": "13:30"
    },
    "timezone": "Asia/Taipei",
    "weekdays_only": True
}
```

## 📈 使用範例

### 完整台股查詢流程

```python
# 1. 初始化組件
from src.frontend.market_switcher import get_market_switcher
from src.cache.unified_cache import get_cache
from src.api.taiwan_endpoints import TaiwanStockAPIEndpoints

switcher = get_market_switcher()
cache = get_cache()
tw_api = TaiwanStockAPIEndpoints()

# 2. 切換到台股市場
result = switcher.switch_market("TW")
print(f"當前市場: {result['current_market']}")

# 3. 搜尋台股
search_results = await tw_api.search_taiwan_stocks("台積")
print(f"搜尋結果: {len(search_results)} 筆")

# 4. 獲取個股資訊
tsmc_info = tw_api.get_stock_info("2330")
print(f"台積電: {tsmc_info.name} ({tsmc_info.symbol})")

# 5. 獲取歷史數據 (帶快取)
historical_data = tw_api.get_historical_data("2330.TW", period="3mo")
print(f"歷史數據: {len(historical_data['data'])} 個交易日")
```

## 🚨 注意事項與最佳實踐

### 1. 數據源合規性
- ✅ 僅使用免費開放數據（日線/延遲）
- ✅ 遵循 TWSE/TPEx 數據使用條款
- ❌ 不提供即時盤中分K/Tick數據

### 2. 效能優化
- 使用快取減少API請求頻率
- 台股交易時間外使用較長快取週期
- 非交易日停用即時數據更新

### 3. 錯誤處理
- 符號不存在：返回友善錯誤訊息
- 數據源故障：自動嘗試備用數據源
- 網路逾時：使用快取數據作為後備

### 4. 安全考量
- API Rate Limiting
- 輸入驗證與清理
- 快取大小限制

## 🔄 後續擴展建議

1. **即時WebSocket推送** (非即時盤中)
2. **更多技術指標** (KD, MACD, 布林帶等)
3. **財報基本面數據**
4. **產業分類與比較**
5. **自選股管理**
6. **CSV匯出功能**
7. **行動端響應式優化**

## 📞 部署支援

需要協助部署或進一步自定義，請提供：
1. 具體的錯誤訊息或日誌
2. 您偏好的部署環境 (Docker/直接部署)
3. 是否需要Redis等外部依賴
4. 預期的並發使用者數量

## 🎉 測試驗收清單

根據您的原始需求，以下功能已就緒：

- ✅ TradingView Charting Library Datafeed 實現
- ✅ 台股符號標準化 (2330.TW, 3481.TWO)
- ✅ 統一時區處理 (台北時區)
- ✅ 美股/台股切換機制
- ✅ 快取策略 (3層架構)
- ✅ API端點設計 (/api/taiwan/...)
- ✅ 錯誤處理與後備機制
- ✅ 符合開放數據使用規範

準備好開始測試！🚀