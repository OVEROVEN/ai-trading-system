# 🔐 Google Cloud 存取 GitHub Repository 設定指南

## 🚀 方法1: GitHub Integration (最推薦)

### 步驟 1: 連接 GitHub 與 Google Cloud Build

1. **前往 Google Cloud Console**
   - 打開: https://console.cloud.google.com/cloud-build/triggers
   - 選擇你的專案

2. **連接 GitHub Repository**
   - 點擊「Connect Repository」
   - 選擇「GitHub (Cloud Build GitHub App)」
   - 授權 Google Cloud 存取你的 GitHub 帳戶
   - 選擇 `OVEROVEN/auto_trade` repository

3. **創建觸發器 (可選)**
   - 名稱: `auto-trade-deploy`
   - 觸發條件: Push to `master` branch
   - 配置: Cloud Build configuration file (`cloudbuild.yaml`)

### 步驟 2: 一鍵部署命令

```bash
# 設置專案ID (替換成你的專案ID)
export PROJECT_ID="your-project-id"

# 設置 gcloud 專案
gcloud config set project $PROJECT_ID

# 啟用必要的 API
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 直接從 GitHub 部署
gcloud run deploy auto-trade-ai \
  --source https://github.com/OVEROVEN/auto_trade \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 900 \
  --set-env-vars "ENVIRONMENT=production,DATABASE_URL=sqlite:///tmp/trading.db,OPENAI_API_KEY=your-openai-key"
```

## 🔑 方法2: Personal Access Token (Private Repo)

### 如果你的 Repository 是私有的:

1. **創建 GitHub Personal Access Token**
   - 前往: https://github.com/settings/tokens
   - 點擊「Generate new token (classic)」
   - 選擇權限: `repo` (Full control of private repositories)
   - 複製 token

2. **在 Google Cloud 中設置 Secret**
   ```bash
   # 儲存 GitHub token 為 Secret
   echo -n "your-github-token" | gcloud secrets create github-token --data-file=-
   ```

3. **修改 cloudbuild.yaml 使用 token**
   ```yaml
   steps:
   - name: 'gcr.io/cloud-builders/git'
     entrypoint: 'bash'
     args:
     - '-c'
     - |
       git clone https://$(gcloud secrets versions access latest --secret="github-token"):@github.com/OVEROVEN/auto_trade.git
       cd auto_trade
       # 繼續建置步驟...
   ```

## ⚡ 方法3: 最簡單 - Cloud Shell 一鍵部署

### 立即執行這個命令:

1. **打開 Google Cloud Shell**
   - 前往: https://console.cloud.google.com
   - 點擊右上角 `>_` Cloud Shell 圖標

2. **執行一鍵部署**
   ```bash
   # 複製貼上這個完整命令
   curl -sSL https://raw.githubusercontent.com/OVEROVEN/auto_trade/master/deploy-to-cloudrun.sh | bash
   ```

   如果上述命令不存在，使用這個：
   ```bash
   # 設置專案ID (請替換)
   export PROJECT_ID="your-project-id-here"
   
   # 自動部署腳本
   gcloud config set project $PROJECT_ID
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   
   # 下載並部署
   wget https://github.com/OVEROVEN/auto_trade/archive/refs/heads/master.zip
   unzip master.zip
   cd auto_trade-master
   
   # 建立 Dockerfile
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
ENV PORT=8000
EXPOSE $PORT
CMD python -m uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
EOF
   
   # 部署到 Cloud Run
   gcloud run deploy auto-trade-ai \
     --source . \
     --region asia-northeast1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 1 \
     --timeout 900 \
     --set-env-vars "ENVIRONMENT=production,DATABASE_URL=sqlite:///tmp/trading.db"
   
   # 顯示結果
   SERVICE_URL=$(gcloud run services describe auto-trade-ai --region=asia-northeast1 --format='value(status.url)')
   echo "🎉 部署完成！"
   echo "🌐 服務URL: $SERVICE_URL"
   echo "📚 API文檔: $SERVICE_URL/docs"
   echo "💚 健康檢查: $SERVICE_URL/health"
   ```

## 🔒 方法4: Service Account (企業級)

### 對於企業或團隊使用:

1. **創建 Service Account**
   ```bash
   gcloud iam service-accounts create github-deploy \
     --display-name="GitHub Deployment Service Account"
   ```

2. **授予權限**
   ```bash
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   ```

3. **創建並下載金鑰**
   ```bash
   gcloud iam service-accounts keys create github-deploy-key.json \
     --iam-account=github-deploy@$PROJECT_ID.iam.gserviceaccount.com
   ```

4. **在 GitHub Secrets 中設置**
   - 前往: https://github.com/OVEROVEN/auto_trade/settings/secrets/actions
   - 新增: `GOOGLE_CLOUD_SA_KEY` = (金鑰檔案內容)
   - 新增: `PROJECT_ID` = (你的專案ID)

## 🎯 推薦流程

### 對你來說最簡單的方式:

1. **確保 Repository 是 Public** (如果可以的話)
2. **使用方法3 - Cloud Shell 一鍵部署**
3. **只需要提供你的 Google Cloud 專案ID**

### 你需要提供給我:
- Google Cloud 專案 ID (例如: `my-trading-app-123456`)
- 偏好的服務名稱 (預設: `auto-trade-ai`)
- 偏好的區域 (預設: `asia-northeast1`)

## 🚨 重要提醒

### 環境變數設置:
部署時記得設置你的 OpenAI API Key:
```bash
--set-env-vars "OPENAI_API_KEY=your-actual-openai-key,ENVIRONMENT=production"
```

### 費用控制:
```bash
--memory 1Gi --cpu 1 --max-instances 10 --concurrency 80
```

準備好專案ID，我就可以立即幫你部署！🚀