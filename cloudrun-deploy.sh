#!/bin/bash
# Google Cloud Run部署腳本

# 1. 設置專案
gcloud config set project your-project-id

# 2. 啟用服務
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 3. 構建並部署
gcloud run deploy auto-trade-ai \
  --source . \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 900 \
  --set-env-vars ENVIRONMENT=production,DEBUG=false,DATABASE_URL=sqlite:///tmp/trading.db

# 4. 設置敏感環境變數
gcloud run services update auto-trade-ai \
  --region asia-northeast1 \
  --set-env-vars OPENAI_API_KEY=YOUR_KEY,JWT_SECRET_KEY=YOUR_SECRET
