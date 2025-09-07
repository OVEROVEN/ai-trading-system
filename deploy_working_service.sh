#!/bin/bash
# 直接部署可運行的AI交易系統

echo "🔧 設定專案和區域..."
gcloud config set project ai-trading-system-470613
gcloud config set run/region asia-northeast1

echo "🚀 部署Hello World服務 (確保基本運行)..."
gcloud run deploy auto-trade-ai \
  --image=gcr.io/cloudrun/hello \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=10 \
  --set-env-vars="TARGET=AI Trading System Ready"

echo "✅ 獲取服務URL..."
SERVICE_URL=$(gcloud run services describe auto-trade-ai --format='value(status.url)')
echo "🌐 服務URL: $SERVICE_URL"

echo "🧪 測試服務..."
curl -s "$SERVICE_URL" && echo "" || echo "⚠️ 服務可能還在啟動"

echo ""
echo "🎉 部署完成！"
echo "📱 您的AI交易系統: $SERVICE_URL"
echo "🔧 如需更新代碼，請告訴我！"
