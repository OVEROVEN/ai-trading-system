# 🚀 AI交易系統 - 完整部署指南 (前端+後端)

## 📋 部署架構

```
┌─────────────────────┐    ┌─────────────────────┐
│   Next.js 前端       │◄──►│   FastAPI 後端       │
│   (Cloud Run)       │    │   (Cloud Run)       │
│   Port: 3000        │    │   Port: 8080        │
└─────────────────────┘    └─────────────────────┘
         │                           │
         └───────────┬───────────────┘
                     ▼
               🌐 用戶訪問
```

## 🎯 部署選項

### 選項1: 分離部署 (推薦生產環境)
前端和後端分別部署為獨立的Cloud Run服務

### 選項2: 統一部署 (推薦開發/測試)
只部署後端API，前端通過Next.js代理訪問

## 🚀 快速部署 (分離部署)

### 步驟1: 部署後端API
```bash
# 設置專案
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 啟用API服務
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# 創建倉庫
gcloud artifacts repositories create auto-trade-repo \
    --repository-format=docker \
    --location=asia-northeast1

# 部署後端
gcloud run deploy auto-trade-api \
    --source . \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false"

# 獲取後端URL
API_URL=$(gcloud run services describe auto-trade-api --region=asia-northeast1 --format='value(status.url)')
echo "後端URL: $API_URL"
```

### 步驟2: 部署前端
```bash
# 部署前端 (使用後端URL)
gcloud run deploy auto-trade-frontend \
    --source ./frontend \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --set-env-vars "NEXT_PUBLIC_API_URL=$API_URL"

# 獲取前端URL
FRONTEND_URL=$(gcloud run services describe auto-trade-frontend --region=asia-northeast1 --format='value(status.url)')
echo "前端URL: $FRONTEND_URL"
```

## 🎯 統一部署 (更簡單)

```bash
# 一鍵部署後端（包含前端代理）
gcloud run deploy auto-trade-ai \
    --source . \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false"
```

## 🔧 環境變數配置

### 後端必需變數
```bash
# 設置API密鑰
gcloud run services update auto-trade-api \
    --region asia-northeast1 \
    --set-env-vars "OPENAI_API_KEY=sk-proj-你的OpenAI密鑰"

# Google OAuth（可選）
gcloud run services update auto-trade-api \
    --region asia-northeast1 \
    --set-env-vars "GOOGLE_CLIENT_SECRET=你的Google密鑰"
```

### 前端必需變數
```bash
# 設置API端點（如果分離部署）
gcloud run services update auto-trade-frontend \
    --region asia-northeast1 \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://your-api-url.a.run.app"
```

## 📊 部署後驗證

### 1. 測試後端API
```bash
# 健康檢查
curl https://your-api-url.a.run.app/health

# API文檔
open https://your-api-url.a.run.app/docs

# 股票分析測試
curl -X POST "https://your-api-url.a.run.app/analyze/AAPL" \
    -H "Content-Type: application/json" \
    -d '{"symbol": "AAPL", "period": "1mo"}'
```

### 2. 測試前端界面
```bash
# 打開前端頁面
open https://your-frontend-url.a.run.app

# 或統一部署的情況下
open https://your-api-url.a.run.app
```

## 🛠️ 本地開發設置

### 同時運行前後端
```bash
# 終端1 - 啟動後端
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001

# 終端2 - 啟動前端
cd frontend
npm run dev
```

### 環境變數設置
```bash
# 後端 .env
OPENAI_API_KEY=sk-proj-你的密鑰
ENVIRONMENT=development

# 前端 frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 🎯 給Gemini的完整指令

### 分離部署指令
```bash
# 後端部署
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud artifacts repositories create auto-trade-repo --repository-format=docker --location=asia-northeast1

gcloud run deploy auto-trade-api \
    --source . \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false"

# 獲取API URL並部署前端
API_URL=$(gcloud run services describe auto-trade-api --region=asia-northeast1 --format='value(status.url)')
gcloud run deploy auto-trade-frontend \
    --source ./frontend \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --set-env-vars "NEXT_PUBLIC_API_URL=$API_URL"

# 設置環境變數
gcloud run services update auto-trade-api \
    --region asia-northeast1 \
    --set-env-vars "OPENAI_API_KEY=sk-proj-你的密鑰"
```

### 統一部署指令（推薦）
```bash
# 一鍵部署
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud run deploy auto-trade-ai \
    --source . \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false,OPENAI_API_KEY=sk-proj-你的密鑰"
```

## 📈 功能特性

部署成功後可用功能：

### 前端界面 🎨
- ✅ 響應式交易儀表板
- ✅ 股票搜索和切換
- ✅ 實時圖表顯示
- ✅ AI分析建議
- ✅ 多語言支持（中英文）
- ✅ Google OAuth登入
- ✅ 兌換碼系統

### 後端API 🔧
- ✅ RESTful API設計
- ✅ OpenAPI文檔 `/docs`
- ✅ 股票數據獲取
- ✅ 技術指標計算
- ✅ AI分析整合
- ✅ WebSocket實時數據
- ✅ 用戶認證系統

### 部署特性 ☁️
- ✅ 自動HTTPS證書
- ✅ 全球CDN加速
- ✅ 自動縮放（0-1000實例）
- ✅ 健康檢查和監控
- ✅ 滾動更新和回滾

## 💰 成本預估

### 免費額度（Google Cloud）
- **Cloud Run**: 每月2M請求
- **Cloud Build**: 每天120分鐘
- **Artifact Registry**: 0.5GB存儲

### 付費使用估算
- **輕量使用**: $5-15/月
- **中等使用**: $20-50/月
- **企業使用**: $100+/月

## 🛡️ 安全最佳實踐

### 1. API密鑰管理
- ✅ 使用Cloud Run環境變數
- ✅ 定期輪換API密鑰
- ✅ 限制API密鑰權限

### 2. 網路安全
- ✅ HTTPS強制加密
- ✅ CORS適當配置
- ✅ 請求限流防護

### 3. 身份認證
- ✅ JWT token認證
- ✅ Google OAuth整合
- ✅ 用戶權限管理

## 🔄 CI/CD 自動部署

### GitHub Actions 配置
```yaml
name: Deploy to Cloud Run
on:
  push:
    branches: [ master ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: google-github-actions/setup-gcloud@v0
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    - name: Deploy Backend
      run: gcloud run deploy auto-trade-api --source .
    
  deploy-frontend:
    needs: deploy-backend
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy Frontend  
      run: gcloud run deploy auto-trade-frontend --source ./frontend
```

## 🎉 部署完成！

恭喜！您的AI交易系統現已完全部署到Google Cloud。

### 📱 立即測試
1. **前端界面**: https://your-frontend-url.a.run.app
2. **API文檔**: https://your-api-url.a.run.app/docs
3. **健康檢查**: https://your-api-url.a.run.app/health

### 📊 監控和維護
- Google Cloud Console監控
- Cloud Logging日誌查看
- Cloud Monitoring指標追蹤
- 自動擴展和負載平衡

**🎊 您的企業級AI交易系統已準備好服務全球用戶！**