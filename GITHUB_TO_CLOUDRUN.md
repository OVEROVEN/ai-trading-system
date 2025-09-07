# 🚀 GitHub直接部署到Google Cloud Run (超簡單)

## ⚡ 最簡單方式：GitHub連結部署

### 方法1: 直接從GitHub URL部署 (推薦)

1. **打開Google Cloud Shell**
   - 前往：https://console.cloud.google.com
   - 點擊右上角 `>_` 啟動Cloud Shell

2. **一鍵部署命令** (複製貼上即可)

```bash
# 設置專案
gcloud config set project ai-trading-system-470613

# 啟用API
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 直接從GitHub部署
gcloud run deploy auto-trade-ai \
  --source https://github.com/OVEROVEN/auto_trade \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars "ENVIRONMENT=production,DATABASE_URL=sqlite:///tmp/trading.db"

# 獲取服務URL
gcloud run services describe auto-trade-ai --region=asia-northeast1 --format='value(status.url)'
```

### 方法2: 如果GitHub方式有問題，使用tar包部署

```bash
# 設置專案
gcloud config set project ai-trading-system-470613
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 下載並解壓縮代碼
curl -L https://github.com/OVEROVEN/auto_trade/archive/refs/heads/master.tar.gz -o auto_trade.tar.gz
tar -xzf auto_trade.tar.gz
cd auto_trade-master

# 創建requirements-core.txt (如果不存在)
cat > requirements-core.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
yfinance==0.2.28
pandas==2.1.4
numpy==1.24.4
matplotlib==3.7.4
seaborn==0.12.2
plotly==5.17.0
requests==2.31.0
aiofiles==23.2.1
python-dotenv==1.0.0
openai==1.3.8
websockets==12.0
httpx==0.25.2
sqlalchemy==2.0.23
sqlite3
EOF

# 創建Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements-core.txt .
RUN pip install --no-cache-dir -r requirements-core.txt
COPY src/ ./src/
COPY config/ ./config/
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV DATABASE_URL=sqlite:///tmp/trading.db
ENV PORT=8000
EXPOSE $PORT
CMD python -m uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
EOF

# 部署
gcloud run deploy auto-trade-ai \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars "ENVIRONMENT=production,DATABASE_URL=sqlite:///tmp/trading.db"

# 獲取結果
SERVICE_URL=$(gcloud run services describe auto-trade-ai --region=asia-northeast1 --format='value(status.url)')
echo "🎉 部署完成！"
echo "服務URL: $SERVICE_URL"
echo "API文檔: $SERVICE_URL/docs"
echo "健康檢查: $SERVICE_URL/health"
```

## 🎯 執行步驟

1. **打開**: https://console.cloud.google.com
2. **啟動Cloud Shell**: 點擊右上角 `>_`  
3. **選擇方法1或方法2**: 複製貼上完整命令
4. **等待5-8分鐘**: 自動完成部署
5. **獲得服務URL**: 立即可用！

## 📊 預期結果

```
🎉 部署完成！
服務URL: https://auto-trade-ai-[random]-an.a.run.app
API文檔: https://auto-trade-ai-[random]-an.a.run.app/docs
健康檢查: https://auto-trade-ai-[random]-an.a.run.app/health
```

## 💡 如果遇到問題

### 問題1: 找不到requirements-core.txt
**解決**: 使用方法2，會自動創建

### 問題2: 構建失敗
**解決**: 檢查GitHub倉庫是否公開，或使用方法2

### 問題3: 服務啟動失敗
**解決**: 檢查PORT環境變數設置

## 🎊 立即開始

**選擇最簡單的方法1，複製貼上一行命令即可！**

您準備好了嗎？打開Cloud Shell開始部署！🚀