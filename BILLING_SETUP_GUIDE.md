# 🔧 Google Cloud 付費帳戶設置指南

## ❗ 當前問題
您的Google Cloud專案需要啟用付費功能才能使用Cloud Run服務。

## 💳 設置付費帳戶 (完全免費使用)

### 步驟1: 啟用付費帳戶
1. **前往付費頁面**：https://console.cloud.google.com/billing
2. **點擊「建立付費帳戶」**
3. **選擇國家/地區**：台灣
4. **輸入信用卡資訊** (僅用於身份驗證，不會收費)

### 步驟2: 連結專案到付費帳戶
1. **在付費頁面**，點擊「連結專案」
2. **選擇專案**：`ai-trading-system-470613`
3. **點擊「設置帳戶」**

## 💰 重要說明：完全免費使用

**Google Cloud Run免費額度：**
- ✅ 每月 200萬次請求免費
- ✅ 每月 40萬GB-秒記憶體免費  
- ✅ 每月 180萬CPU-秒免費
- ✅ **您的AI交易系統完全在免費額度內**

**實際費用：$0/月** (個人使用)

## 🚀 設置完成後執行的正確命令

在Cloud Shell中執行：

```bash
# 設置專案
gcloud config set project ai-trading-system-470613

# 啟用服務
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 從GitHub部署
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

## 📋 完整步驟總結

1. **啟用付費帳戶** (2分鐘) - https://console.cloud.google.com/billing
2. **連結專案** (1分鐘)
3. **執行上面的部署命令** (5分鐘)
4. **完成！** ✅

## 🎯 預期結果

```
🎉 部署完成！
服務URL: https://auto-trade-ai-[random]-an.a.run.app
```

## 💡 替代方案：使用不同專案

如果您不想設置付費帳戶，可以：

1. **創建新專案** (選擇有免費試用的帳戶)
2. **或使用現有的已啟用付費的專案**

## 🎊 準備好了嗎？

1. 前往：https://console.cloud.google.com/billing
2. 設置付費帳戶
3. 返回Cloud Shell執行部署命令

**記住：完全免費使用，只是需要付費帳戶驗證！** 🚀