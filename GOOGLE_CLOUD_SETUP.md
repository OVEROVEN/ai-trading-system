# 🚀 Google Cloud Run 一鍵部署指南

## 📋 您需要做的事情 (5分鐘內完成)

### 方案A: 使用Cloud Shell (最簡單，推薦) ⭐

1. **前往 Google Cloud Console**
   - 訪問：https://console.cloud.google.com
   - 使用Google帳號登入

2. **創建專案** 
   - 點擊頂部的專案選擇器
   - 點「新專案」
   - 輸入專案名稱 (例如：`my-trading-system`)
   - **記下專案ID** (例如：`my-trading-system-12345`)

3. **開啟Cloud Shell**
   - 點擊右上角的 `>_` 圖標 (Activate Cloud Shell)
   - 等待Shell啟動完成

4. **上傳代碼到Cloud Shell**
   ```bash
   # 在Cloud Shell中執行
   git clone https://github.com/OVEROVEN/auto_trade.git
   cd auto_trade
   ```

5. **一鍵部署**
   ```bash
   # 替換YOUR_PROJECT_ID為您的專案ID
   bash deploy-cloudrun.sh YOUR_PROJECT_ID
   ```

### 方案B: 本機部署 (需要安裝gcloud)

1. **安裝Google Cloud SDK**
   - 下載：https://cloud.google.com/sdk/docs/install
   - 安裝完成後重新啟動終端機

2. **登入並設置專案**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **執行部署**
   ```bash
   bash deploy-cloudrun.sh YOUR_PROJECT_ID
   ```

## 🎯 現在告訴我您的專案ID

**格式範例：**
```
專案ID：my-trading-system-12345
服務名稱：auto-trade (可選，預設auto-trade-ai)
區域：asia-northeast1 (可選，預設東京)
```

**或者只需要：**
```
專案ID：my-trading-system-12345
```

## 🚀 我會立即為您執行

收到您的專案ID後，我會：

1. ✅ **生成完整部署命令**
2. ✅ **執行gcloud部署**
3. ✅ **測試所有功能**
4. ✅ **提供完整的服務URL**

**預計時間：3-5分鐘**

## 📊 部署後您會獲得

```
🌐 服務URL: https://auto-trade-ai-xxx-an.a.run.app
📚 API文檔: https://auto-trade-ai-xxx-an.a.run.app/docs
💚 健康檢查: https://auto-trade-ai-xxx-an.a.run.app/health
🎫 兌換碼API: https://auto-trade-ai-xxx-an.a.run.app/api/redemption
```

## 💰 費用說明

**Google Cloud Run 免費額度：**
- 每月 200萬次請求免費
- 每月 40萬GB-秒記憶體免費 
- 每月 180萬CPU-秒免費

**您的使用預估：完全免費** (個人使用在免費額度內)

## ⚙️ 可選：設置AI功能

如果您需要AI分析功能，部署完成後可以設置：

```bash
gcloud run services update auto-trade-ai \
  --region asia-northeast1 \
  --set-env-vars "OPENAI_API_KEY=您的OpenAI金鑰"
```

## 🎊 準備好了嗎？

**請回覆您的Google Cloud專案ID，我立即開始部署！** 🚀

範例回覆：
> 專案ID：my-trading-project-2024

或

> my-trading-project-2024

我會立即為您完成整個部署過程！