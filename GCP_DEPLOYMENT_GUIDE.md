# 🚀 Google Cloud Run 部署指南

## 📋 您需要做什麼

### 步驟1: 設置Google Cloud專案 (3分鐘)

1. **前往 Google Cloud Console**
   - 訪問：https://console.cloud.google.com
   - 使用您的Google帳號登入

2. **創建或選擇專案**
   - 點擊頂部的專案選擇器
   - 點「新專案」或選擇現有專案
   - **記下專案ID** (例如：my-trading-app-12345)

3. **啟用必要的API**
   - 在Console中搜索「Cloud Run」
   - 點擊啟用Cloud Run API
   - 搜索「Cloud Build」
   - 點擊啟用Cloud Build API

### 步驟2: 設置認證 (2分鐘)

**選項A - 使用Cloud Shell (推薦，最簡單)**
- 在Google Cloud Console點擊右上角的「Activate Cloud Shell」圖標
- 等待Shell啟動完成
- 就可以直接部署了！

**選項B - 本機部署 (需要安裝gcloud)**
- 下載並安裝 Google Cloud SDK
- 執行 `gcloud auth login`
- 執行 `gcloud config set project YOUR_PROJECT_ID`

## 🎯 提供給我的資訊

**您只需要告訴我：**

1. **專案ID**: 您在Google Cloud創建的專案ID
   - 範例：`my-trading-app-12345`

2. **服務名稱偏好** (可選)
   - 預設：`auto-trade-ai`
   - 或您想要的名稱

3. **部署區域偏好** (可選) 
   - 預設：`asia-northeast1` (東京，速度快)
   - 其他選項：`us-central1`, `europe-west1`

## 🔧 我會為您準備的

### 自動生成的文件：
1. **Dockerfile.cloudrun** - 優化的容器配置
2. **deploy-to-cloudrun.sh** - 一鍵部署腳本
3. **cloud-run-config.yaml** - 服務配置
4. **環境變數設置腳本**

### 自動設置的功能：
- ✅ 完整的AI交易系統
- ✅ 兌換碼功能 (已修復UUID問題)
- ✅ 所有API端點
- ✅ 健康檢查和監控
- ✅ 自動HTTPS
- ✅ 全球CDN

## 💰 費用說明

**Google Cloud Run免費額度：**
- ✅ 每月200萬次請求免費
- ✅ 每月40萬GB-秒的記憶體免費
- ✅ 每月180萬CPU-秒免費

**您的AI交易系統預估使用量：**
- 🔹 個人使用：完全在免費額度內 ($0/月)
- 🔹 中等使用：約$1-5/月
- 🔹 高流量使用：約$5-20/月

## 🚀 部署流程

### 我會執行的步驟：
1. **生成優化的Dockerfile** - 針對Cloud Run優化
2. **創建部署腳本** - 包含所有環境變數
3. **執行部署命令** - 透過gcloud CLI
4. **設置域名和HTTPS** - 自動配置
5. **測試所有功能** - 確保兌換碼等功能正常
6. **提供完整URL** - 給您最終的服務地址

### 整個過程只需要：
- ⏰ **5-8分鐘**完成部署
- 🎯 **零停機**上線
- 🔒 **自動HTTPS**
- 🌍 **全球CDN**

## 📝 示例

**您告訴我：**
```
專案ID: my-ai-trading-2024
服務名稱: auto-trade-system  
區域: asia-northeast1
```

**我會執行：**
```bash
gcloud run deploy auto-trade-system \
  --source . \
  --project my-ai-trading-2024 \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 900 \
  --set-env-vars ENVIRONMENT=production,DATABASE_URL=sqlite:///tmp/trading.db
```

**部署完成後您會獲得：**
```
✅ 服務URL: https://auto-trade-system-xxx-an.a.run.app
✅ API文檔: https://auto-trade-system-xxx-an.a.run.app/docs
✅ 健康檢查: https://auto-trade-system-xxx-an.a.run.app/health
✅ 兌換碼API: https://auto-trade-system-xxx-an.a.run.app/api/redemption
```

## 🎊 準備好了嗎？

**請提供您的專案ID，我立即開始部署！**

範例回覆：
> 專案ID：my-trading-project-2024
> 服務名稱：auto-trade (或使用預設)
> 區域：asia-northeast1 (或使用預設)

我會立即為您生成所有配置文件並執行部署！🚀