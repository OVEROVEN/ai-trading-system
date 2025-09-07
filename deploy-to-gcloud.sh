#!/bin/bash

# 🚀 Google Cloud Run 一鍵部署腳本
# AI交易系統自動部署到Google Cloud

set -e

echo "🚀 開始部署AI交易系統到Google Cloud Run..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置變數
PROJECT_ID=""
REGION="asia-northeast1" 
SERVICE_NAME="auto-trade-ai"
REPO_NAME="auto-trade-repo"

# 函數：打印有色輸出
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查是否安裝gcloud
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK 未安裝"
    echo "請安裝: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 獲取或設置專案ID
if [ -z "$PROJECT_ID" ]; then
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ -n "$CURRENT_PROJECT" ]; then
        echo "當前專案: $CURRENT_PROJECT"
        read -p "使用此專案進行部署? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PROJECT_ID=$CURRENT_PROJECT
        else
            read -p "請輸入您的Google Cloud專案ID: " PROJECT_ID
        fi
    else
        read -p "請輸入您的Google Cloud專案ID: " PROJECT_ID
    fi
fi

print_status "使用專案: $PROJECT_ID"

# 設置專案
gcloud config set project $PROJECT_ID

# 檢查認證
print_status "檢查Google Cloud認證..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_warning "需要登入Google Cloud"
    gcloud auth login
fi

# 啟用必要的API
print_status "啟用必要的Google Cloud API..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com

# 創建Artifact Registry (如果不存在)
print_status "設置Docker倉庫..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    print_status "創建Artifact Registry..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="AI Trading System Docker Repository"
else
    print_status "Docker倉庫已存在"
fi

# 部署到Cloud Run
print_status "部署到Cloud Run..."
echo "這可能需要幾分鐘時間..."

gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false,DATABASE_URL=sqlite:///tmp/trading.db"

# 獲取服務URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

print_status "部署完成！"
echo ""
echo "🌐 服務URL: $SERVICE_URL"
echo "📚 API文檔: $SERVICE_URL/docs"
echo "💚 健康檢查: $SERVICE_URL/health"
echo ""

# 測試服務
print_status "測試部署的服務..."
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    print_status "健康檢查通過！服務運行正常"
else
    print_warning "健康檢查失敗，服務可能還在啟動中"
fi

echo ""
echo "🎉 AI交易系統已成功部署到Google Cloud Run！"
echo ""
echo "📋 後續步驟："
echo "1. 設置OpenAI API Key:"
echo "   gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "   --set-env-vars \"OPENAI_API_KEY=你的API密鑰\""
echo ""
echo "2. 如需Google OAuth，設置客戶端密鑰:"
echo "   gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "   --set-env-vars \"GOOGLE_CLIENT_SECRET=你的密鑰\""
echo ""
echo "3. 訪問API文檔: $SERVICE_URL/docs"