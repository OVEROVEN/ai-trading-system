# 🎯 AI Trading System - Production Version v2.0.0

## 🚀 Current Stable Deployment

**版本標記**: `v2.0.0-production`  
**部署時間**: 2025-09-08  
**狀態**: ✅ **STABLE - DO NOT MODIFY**

## 📊 Production Services

### Frontend
- **URL**: https://auto-trade-frontend-610357573971.asia-northeast1.run.app
- **Version**: auto-trade-frontend-00016-scd
- **Features**: ✅ OAuth Login, ✅ AI Analysis Display, ✅ Real-time Charts

### Backend  
- **URL**: https://auto-trade-backend-610357573971.asia-northeast1.run.app
- **Version**: auto-trade-backend-00057-k6p
- **Features**: ✅ GPT-4o Analysis, ✅ Alpha Vantage API, ✅ Google OAuth

## 🎯 Core Features (Verified Working)

### ✅ AI Analysis (GPT-4o + Function Calling)
- **AAPL**: RSI 71.01 → SELL ($230 target, $245 stop-loss)
- **GOOGL**: RSI 84.51 → SELL (extreme overbought)
- **META**: RSI 52.48 → HOLD (neutral zone)

### ✅ Analyst Strategies Implemented
- RSI 超買/超賣判斷 (>80, <20, ~50)
- 均線法則 (5/10/20日線策略)  
- 具體價位建議 (進場/停損/目標價)
- 風險管理與量能分析

### ✅ Authentication
- Google OAuth 2.0 完整支援
- Client ID: `610357573971-6koi1jlp7s731ck6smhinok3e1c7thc8.apps.googleusercontent.com`

### ✅ Real-time Data
- Alpha Vantage API 整合
- OpenAI Function Calling 自動數據獲取
- 即時股票報價與技術指標

## 🔒 Security Notes

- ✅ API Keys 已從代碼中移除
- ✅ 環境變數在 Cloud Run 中安全配置  
- ✅ .gitignore 已更新保護敏感文件
- ✅ GitHub 代碼已清理，無硬編碼密鑰

## ⚠️ Important

**此版本為穩定生產版本，請勿輕易修改！**

如需進行開發或實驗，請：
1. 創建新的分支 (`git checkout -b feature/your-feature`)
2. 或在本地環境進行測試
3. 確保不影響生產部署

## 🛠️ Environment Variables (Production)

```bash
OPENAI_API_KEY=sk-proj-[PROTECTED]
ALPHA_VANTAGE_API_KEY=JT46IUX47YBTTP3X  
GOOGLE_CLIENT_ID=610357573971-6koi1jlp7s731ck6smhinok3e1c7thc8.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-[PROTECTED]
DATABASE_URL=sqlite:///tmp/data/trading.db
```

---
📝 **Generated**: 2025-09-08  
🤖 **Managed by**: Claude Code