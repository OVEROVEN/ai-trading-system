#!/bin/bash
# 立即執行的Cloud Run更新命令
# 直接複製貼上到Cloud Shell執行

echo "🚀 正在更新AI交易系統..."

gcloud run services update auto-trade-ai \
  --region=asia-northeast1 \
  --project=ai-trading-system-470613 \
  --set-env-vars="TARGET=🚀 AI Trading System - Professional Version,MESSAGE=歡迎使用AI交易分析系統,STATUS=operational,VERSION=1.0.0,SYSTEM=AI Trading Analysis Platform"

echo "✅ 更新完成！正在獲取服務URL..."

gcloud run services describe auto-trade-ai \
  --region=asia-northeast1 \
  --project=ai-trading-system-470613 \
  --format='value(status.url)'

echo "🎉 您的AI交易系統已更新！"