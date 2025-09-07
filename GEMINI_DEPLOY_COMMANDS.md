# 🚀 給Gemini的Google Cloud部署指令

## 📋 一鍵複製貼上指令

### 1. 設置專案和啟用API
```bash
# 設置您的專案ID（替換為實際的專案ID）
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 啟用必要的API服務
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# 創建Docker倉庫
gcloud artifacts repositories create auto-trade-repo --repository-format=docker --location=asia-northeast1
```

### 2. 一鍵部署到Cloud Run
```bash
# 直接從原始碼部署
gcloud run deploy auto-trade-ai \
    --source . \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false,DATABASE_URL=sqlite:///tmp/trading.db"
```

### 3. 設置環境變數（部署完成後執行）
```bash
# 設置OpenAI API Key（必需）
gcloud run services update auto-trade-ai \
    --region asia-northeast1 \
    --set-env-vars "OPENAI_API_KEY=sk-proj-您的OpenAI_API_Key"

# 設置Google OAuth密鑰（如果需要）
gcloud run services update auto-trade-ai \
    --region asia-northeast1 \
    --set-env-vars "GOOGLE_CLIENT_SECRET=您的Google_Client_Secret"
```

### 4. 獲取部署結果
```bash
# 獲取服務URL
gcloud run services describe auto-trade-ai --region=asia-northeast1 --format='value(status.url)'

# 測試健康檢查
SERVICE_URL=$(gcloud run services describe auto-trade-ai --region=asia-northeast1 --format='value(status.url)')
curl $SERVICE_URL/health
```

## 🎯 完整自動化腳本（推薦）
如果您偏好使用準備好的腳本：
```bash
# 執行自動部署腳本
chmod +x deploy-to-gcloud.sh
./deploy-to-gcloud.sh
```

## 📊 部署後可用端點
- **API文檔**: https://your-service-url/docs
- **健康檢查**: https://your-service-url/health  
- **股票分析**: https://your-service-url/analyze/AAPL
- **WebSocket**: wss://your-service-url/stream/AAPL

## 💰 費用預估
- 免費額度：每月200萬次請求
- 超出後：約$0.40/百萬次請求
- 預估月費：$5-20（一般使用）

## 🛠️ 故障排除
如果部署失敗：
```bash
# 查看詳細日誌
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# 重新部署
gcloud run deploy auto-trade-ai --source . --region asia-northeast1
```

---

**🎉 複製以上指令給Gemini，即可完成AI交易系統的Google Cloud部署！**