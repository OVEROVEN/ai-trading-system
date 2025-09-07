#!/bin/bash
# 完整AI交易系統部署

echo "🔧 準備部署完整AI交易系統..."
gcloud config set project ai-trading-system-470613

echo "📦 從本地代碼構建並部署..."
gcloud run deploy auto-trade-ai \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "ENVIRONMENT=production,VERSION=1.0.0"

echo "🎯 部署完成!"
gcloud run services describe auto-trade-ai --format='value(status.url)'
