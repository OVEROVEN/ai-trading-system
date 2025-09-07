# 🚀 AI Trading Dashboard Frontend

## 📁 項目結構

```
auto_trade/
├── frontend/                    # 新增的前端目錄
│   ├── app/
│   │   ├── layout.tsx          # 主布局
│   │   ├── page.tsx            # 主頁面 (儀表板)
│   │   └── globals.css         # 全局樣式
│   ├── components/             # React組件
│   │   ├── StockSearch.tsx     # 股票搜索
│   │   ├── TradingChart.tsx    # TradingView圖表
│   │   ├── MarketData.tsx      # 市場數據面板
│   │   ├── AIAnalysis.tsx      # AI分析面板
│   │   ├── PerformancePanel.tsx# 性能面板
│   │   ├── FeatureCards.tsx    # 功能卡片
│   │   └── StatusBar.tsx       # 狀態欄
│   ├── package.json            # 前端依賴
│   ├── next.config.js          # Next.js配置
│   └── tailwind.config.ts      # Tailwind配置
├── src/                        # 原有後端代碼
├── start_ai_dashboard.bat      # 完整啟動腳本 ⭐
├── quick_start.bat            # 快速啟動腳本 ⭐
└── ...其他原有文件
```

## 🚀 啟動方式

### 方法1: 使用完整啟動腳本 (推薦)
```bash
# 雙擊執行
start_ai_dashboard.bat
```

### 方法2: 使用快速啟動
```bash  
# 雙擊執行
quick_start.bat
```

### 方法3: 手動啟動
```bash
# 後端 API (Terminal 1)
uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 前端 (Terminal 2)  
cd frontend
npm install  # 首次需要
npm run dev
```

## 🌐 訪問地址

- **🎛️ AI儀表板**: http://localhost:3000
- **📋 API文檔**: http://localhost:8000/docs
- **⚡ 後端API**: http://localhost:8000
- **💚 健康檢查**: http://localhost:8000/health

## 🎯 界面功能

### 📊 完全按照您的設計圖片實現

✅ **深藍色漸變背景**
✅ **🚀 標題和三個狀態指示器**  
✅ **股票搜索 + 熱門股票按鈕**
✅ **大型TradingView專業圖表**
✅ **三個數據面板布局** (市場數據 | AI分析 | 性能)
✅ **四個功能卡片** (技術分析 | 形態識別 | AI洞察 | 多市場)
✅ **底部系統狀態欄**
✅ **響應式設計** (適配所有設備)

### 🔥 核心特色

1. **股票搜索**: 支援美股和台股 (AAPL, 2330.TW)
2. **TradingView整合**: 深色主題專業K線圖
3. **AI智能分析**: GPT-4驅動的投資建議
4. **實時數據**: 價格、技術指標、AI建議
5. **Widget同步**: 解決了您提到的切換問題
6. **現代UI**: 玻璃擬態、平滑動畫效果

## 🔄 Widget同步解決方案

**問題**: 切換股票時其他Widget不同步
**解決**: 
- 統一的`selectedSymbol`狀態管理
- 所有組件自動響應股票切換
- API數據統一分發到各個面板

## 🛠️ 技術棧

- **Next.js 14**: React應用框架
- **TypeScript**: 類型安全開發
- **Tailwind CSS**: 現代化樣式
- **TradingView Widget**: 專業圖表
- **FastAPI整合**: 無縫後端對接

## 📱 響應式設計

- **桌面**: 完整三列布局
- **平板**: 自適應兩列
- **手機**: 單列堆疊布局

## 🎨 設計亮點

- **專業深色主題**: 藍黑漸變背景
- **玻璃擬態效果**: 半透明面板
- **平滑動畫**: 懸停和過渡效果
- **現代化圖標**: Emoji + 狀態指示器
- **直觀操作**: 一鍵分析、熱門股票按鈕

## 🔧 開發說明

前端完全整合到現有`auto_trade`專案中，無需額外設置。所有API調用都指向現有的FastAPI後端，充分利用現有的：

- 股票數據獲取
- 技術分析引擎  
- AI智能分析
- TradingView圖表服務

## 🎯 下一步

系統已完全就緒！您現在擁有：
- ✅ 專業的交易儀表板界面
- ✅ 完整的前後端整合
- ✅ 解決了Widget同步問題
- ✅ 響應式現代化設計

**立即體驗您的AI交易儀表板！** 🚀