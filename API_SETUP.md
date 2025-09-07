# API 設定指南 (API Setup Guide)

本地開發環境需要以下 API 密鑰。部分密鑰已從 Google Cloud 提取，部分需要您申請。

## 🔑 已配置的 API 密鑰

### ✅ OpenAI API
- **狀態**: 已從 Google Cloud 提取
- **用途**: AI 分析和策略建議
- **配置**: 已在 `.env.local` 中設定

### ✅ Google OAuth
- **狀態**: 已從 Google Cloud 提取  
- **用途**: 用戶登入驗證
- **配置**: 已在 `.env.local` 中設定

## 🔧 需要申請的 API 密鑰 (可選)

### 📈 Alpha Vantage (股票數據)
```bash
# 1. 訪問: https://www.alphavantage.co/support/#api-key
# 2. 免費註冊獲取 API Key
# 3. 更新 .env.local:
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 💰 Financial Modeling Prep (財務數據)
```bash
# 1. 訪問: https://financialmodelingprep.com/developer/docs
# 2. 註冊並獲取 API Key
# 3. 更新 .env.local:
FMP_API_KEY=your_fmp_api_key_here
```

### 🇹🇼 台股相關 API (台灣股市)
```bash
# 系統支援台灣證交所公開資料
# 無需額外 API 密鑰，但需要網路連接
TWSE_API_ENABLED=true
```

## 🚀 快速開始 (無額外 API)

系統可以在不申請額外 API 的情況下運行：

1. **使用內建示範數據**
2. **Yahoo Finance 免費數據** (已內建)
3. **台股公開資料** (免費)

```bash
# 直接啟動開發環境
./dev-start.sh
```

## ⚙️ API 密鑰設定方式

### 方法 1: 環境文件
編輯 `.env.local` 文件：
```bash
# 在文件中添加您的 API 密鑰
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
```

### 方法 2: 直接設定環境變數
```bash
export ALPHA_VANTAGE_API_KEY=your_key_here
export FMP_API_KEY=your_key_here
```

## 🧪 測試 API 連接

啟動後可以測試 API 連接：

```bash
# 測試後端 API
curl http://localhost:8000/api/health

# 測試股票數據
curl http://localhost:8000/api/stocks/AAPL

# 測試 AI 分析 (需要 OpenAI API)
curl -X POST http://localhost:8000/api/analysis/ai \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "analysis_type": "technical"}'
```

## 🔒 安全提醒

- ✅ `.env.local` 已被 `.gitignore` 忽略
- ✅ 生產環境 API 密鑰存儲在 Google Secret Manager
- ❌ 請勿將 API 密鑰提交到版本控制
- ❌ 請勿在公共場所分享 API 密鑰

## 🆘 故障排除

### 問題 1: OpenAI API 錯誤
```bash
# 檢查 API 密鑰是否正確
echo $OPENAI_API_KEY
```

### 問題 2: 股票數據無法獲取
```bash
# 檢查網路連接
curl -I https://query1.finance.yahoo.com

# 檢查 API 限制
# Alpha Vantage: 5 calls/minute (free tier)
# FMP: 250 calls/day (free tier)
```

### 問題 3: 資料庫連接問題
```bash
# 檢查資料庫狀態
docker-compose -f docker-compose.local.yml ps postgres

# 檢查資料庫連接
docker exec -it trading_postgres_dev psql -U postgres -d trading_db_local -c "\dt"
```

---

需要協助設定 API 密鑰或遇到問題？請聯繫開發團隊！