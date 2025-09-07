# 🚀 AI 股票交易分析系統 - 使用手冊

## 📋 目錄
1. [系統概述](#系統概述)
2. [快速開始](#快速開始)
3. [功能說明](#功能說明)
4. [API 使用](#api-使用)
5. [策略開發](#策略開發)
6. [常見問題](#常見問題)

## 🎯 系統概述

本系統是一個完整的 AI 驅動股票交易分析平台，提供：

### 核心功能
- **多市場支援**: 美股 (NYSE/NASDAQ) 和台股 (TWSE)
- **技術分析**: 15+ 技術指標，包含 RSI、MACD、布林帶等
- **模式識別**: 自動檢測頭肩頂、雙頂、突破等技術型態
- **AI 分析**: OpenAI GPT-4 智能分析和建議
- **策略回測**: 多種交易策略的歷史績效測試
- **即時數據**: WebSocket 即時價格和分析推送

### 技術架構
- **後端**: FastAPI + Python
- **數據**: yfinance (美股) + 多源台股數據
- **AI**: OpenAI GPT-4 API
- **數據庫**: PostgreSQL + TimescaleDB
- **部署**: Docker 容器化

## 🚀 快速開始

### 1. 環境準備
```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數 (可選)
cp .env.example .env
# 編輯 .env 檔案，添加 OpenAI API Key
```

### 2. 啟動系統
```bash
# 方法 1: 使用啟動腳本
python start_system.py

# 方法 2: 直接啟動
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 驗證安裝
- 瀏覽器開啟: http://localhost:8000/docs
- 檢查健康狀態: http://localhost:8000/health

## 💡 功能說明

### 📊 技術分析功能

**支援指標**:
- 趨勢指標: SMA, EMA, MACD
- 振盪指標: RSI, Stochastic, Williams %R
- 波動指標: 布林帶, ATR
- 量價指標: OBV, Volume Ratio

**模式識別**:
- 反轉型態: 頭肩頂、雙頂雙底、V型反轉
- 整理型態: 三角形、楔形、矩形
- 突破型態: 支撐阻力突破、通道突破

### 🤖 AI 智能分析

**GPT-4 分析**:
- 技術面分析和解讀
- 市場情緒評估
- 交易建議生成
- 風險評估

**圖表分析** (GPT-4 Vision):
- 自動圖表型態識別
- 關鍵價位標註
- 視覺化分析報告

### 📈 回測系統

**內建策略**:
1. **RSI + MACD 策略**: 結合超買超賣和趨勢確認
2. **移動平均交叉**: 金叉死叉交易系統

**績效指標**:
- 報酬率指標: 總報酬、年化報酬
- 風險指標: 夏普比率、最大回撤、波動率
- 交易統計: 勝率、獲利因子、平均獲利/虧損

## 🔧 API 使用

### 基本端點

#### 1. 系統狀態
```bash
GET /health
# 回應: 系統健康狀態和服務可用性
```

#### 2. 股票分析
```bash
POST /analyze/{symbol}
# 參數:
{
  "symbol": "AAPL",
  "period": "3mo",
  "include_ai": true,
  "include_patterns": true
}
```

#### 3. 策略回測
```bash
POST /backtest
# 參數:
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "strategy_name": "rsi_macd",
  "strategy_params": {
    "rsi_oversold": 30,
    "rsi_overbought": 70
  },
  "initial_capital": 100000,
  "commission": 0.001425
}
```

#### 4. 即時數據流
```javascript
// WebSocket 連接
const ws = new WebSocket('ws://localhost:8000/stream/AAPL');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('即時數據:', data);
};
```

### Python 範例

```python
import requests

# 分析股票
response = requests.post('http://localhost:8000/analyze/AAPL', json={
    'symbol': 'AAPL',
    'period': '3mo',
    'include_ai': True
})

if response.status_code == 200:
    data = response.json()
    print(f"當前價格: ${data['current_price']}")
    print(f"RSI: {data['technical_indicators']['rsi']}")
    
# 策略回測
backtest_data = {
    'symbol': 'AAPL',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'strategy_name': 'rsi_macd',
    'initial_capital': 100000
}

response = requests.post('http://localhost:8000/backtest', json=backtest_data)
if response.status_code == 200:
    result = response.json()
    print(f"總報酬率: {result['performance_metrics']['total_return_pct']:.2f}%")
```

## 🛠️ 策略開發

### 創建自定義策略

1. **繼承基礎類別**
```python
from src.backtesting.backtest_engine import TradingStrategy

class MyCustomStrategy(TradingStrategy):
    def __init__(self, param1=10, param2=20):
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data):
        # 實現訊號生成邏輯
        df = data.copy()
        df['signal'] = 0  # 0=持有, 1=買入, -1=賣出
        df['signal_strength'] = 0.0  # 訊號強度 0-1
        df['signal_source'] = 'MyStrategy'
        
        # 你的策略邏輯
        # ...
        
        return df
    
    def get_strategy_name(self):
        return f"MyCustomStrategy_{self.param1}_{self.param2}"
```

2. **註冊到系統**
```python
# 在 src/backtesting/backtest_engine.py 的 StrategyFactory 中添加
strategies = {
    'rsi_macd': RSIMACDStrategy,
    'ma_crossover': MovingAverageCrossoverStrategy,
    'my_custom': MyCustomStrategy,  # 新增
}
```

### 策略開發指南

**訊號生成原則**:
- `signal = 1`: 買入訊號
- `signal = -1`: 賣出訊號  
- `signal = 0`: 持有/無訊號

**必要欄位**:
- `signal`: 交易訊號
- `signal_strength`: 訊號強度 (0-1)
- `signal_source`: 訊號來源標識

**最佳實踐**:
- 避免未來函數 (look-ahead bias)
- 考慮交易成本和滑價
- 實施適當的風險管理
- 進行充分的回測驗證

## ❓ 常見問題

### Q1: 如何獲取台股數據？
A: 系統自動支援 `.TW` 後綴的台股代號，如 `2330.TW` (台積電)

### Q2: OpenAI API 是必需的嗎？
A: 不是必需的，AI 分析功能是可選的。沒有 API Key 時其他功能正常運作。

### Q3: 如何添加新的技術指標？
A: 在 `src/analysis/technical_indicators.py` 中添加新的計算函數。

### Q4: 回測結果不準確怎麼辦？
A: 檢查數據質量、確認策略邏輯、考慮交易成本和市場環境。

### Q5: 如何部署到生產環境？
A: 使用 Docker 容器化部署，配置適當的環境變數和數據庫。

## 📧 技術支援

如有問題或建議，請參考：
- API 文檔: http://localhost:8000/docs
- 範例代碼: `/examples/` 資料夾
- 測試腳本: 各種 `test_*.py` 檔案

---

**更新日期**: 2025-08-15  
**版本**: v1.0.0