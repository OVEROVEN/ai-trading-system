#!/bin/bash
# Google Cloud Run自動部署腳本 - AI交易系統
# 使用方法: bash deploy-cloudrun.sh YOUR_PROJECT_ID [SERVICE_NAME] [REGION]

set -e  # 遇到錯誤立即停止

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置參數
PROJECT_ID=${1:-"your-project-id"}
SERVICE_NAME=${2:-"auto-trade-ai"}
REGION=${3:-"asia-northeast1"}

echo -e "${BLUE}🚀 AI交易系統 - Google Cloud Run部署${NC}"
echo "=================================="
echo -e "專案ID: ${GREEN}$PROJECT_ID${NC}"
echo -e "服務名稱: ${GREEN}$SERVICE_NAME${NC}"
echo -e "部署區域: ${GREEN}$REGION${NC}"
echo ""

# 檢查參數
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}❌ 錯誤: 請提供您的Google Cloud專案ID${NC}"
    echo "使用方法: bash deploy-cloudrun.sh YOUR_PROJECT_ID [SERVICE_NAME] [REGION]"
    echo "範例: bash deploy-cloudrun.sh my-trading-project auto-trade asia-northeast1"
    exit 1
fi

# 檢查gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ 錯誤: 未找到gcloud CLI${NC}"
    echo "請安裝Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${YELLOW}📋 步驟1: 設置Google Cloud專案${NC}"
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}📋 步驟2: 啟用必要的API服務${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo -e "${YELLOW}📋 步驟3: 構建並部署到Cloud Run${NC}"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --dockerfile Dockerfile.cloudrun \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --max-instances 10 \
    --concurrency 80 \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false,DATABASE_URL=sqlite:///tmp/trading.db"

# 獲取服務URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo -e "${GREEN}🎉 部署成功！${NC}"
echo "=================================="
echo -e "🌐 服務URL: ${BLUE}$SERVICE_URL${NC}"
echo -e "📚 API文檔: ${BLUE}$SERVICE_URL/docs${NC}"
echo -e "💚 健康檢查: ${BLUE}$SERVICE_URL/health${NC}"
echo -e "🎫 兌換碼API: ${BLUE}$SERVICE_URL/api/redemption${NC}"
echo ""

echo -e "${YELLOW}⚙️  設置敏感環境變數 (可選)${NC}"
echo "如果您需要AI功能，請執行以下命令設置API金鑰："
echo ""
echo "gcloud run services update $SERVICE_NAME \\"
echo "  --region $REGION \\"
echo "  --set-env-vars \"OPENAI_API_KEY=YOUR_OPENAI_API_KEY,JWT_SECRET_KEY=YOUR_JWT_SECRET\""
echo ""

echo -e "${YELLOW}🧪 測試部署的服務${NC}"
echo "正在測試健康檢查端點..."

# 測試健康檢查
if curl -s -f "$SERVICE_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ 健康檢查通過！${NC}"
else
    echo -e "${YELLOW}⚠️  服務可能還在啟動中，請稍後再試${NC}"
fi

echo ""
echo -e "${GREEN}🎯 部署完成！您的AI交易系統已在Google Cloud Run上運行${NC}"
echo -e "${BLUE}立即開始使用: $SERVICE_URL/docs${NC}"

# 生成管理命令參考
echo ""
echo -e "${YELLOW}📝 管理命令參考:${NC}"
echo "檢查服務狀態: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "查看日誌: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "更新服務: gcloud run services update $SERVICE_NAME --region=$REGION"
echo "刪除服務: gcloud run services delete $SERVICE_NAME --region=$REGION"