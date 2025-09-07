# 台股TradingView Widget 測試指南

## 🎯 測試目標

驗證台股Widget在HTTPS環境下是否能正常顯示實際的股價數據。

---

## 方法1: 在線測試 (推薦，最簡單)

### 1.1 使用CodePen測試

**步驟:**
1. 打開 [CodePen](https://codepen.io/pen/)
2. 點擊 "HTML" 標籤
3. 複製並貼上 `codepen_test.html` 的內容
4. 點擊右下角 "Run" 按鈕
5. 觀察結果

**期望結果:**
- ✅ Widget載入成功
- ✅ 顯示 "TWSE:2330" 而不是 "TPE:2330"
- ✅ OHLC數據顯示實際數字，不是 "∅"
- ✅ 可以看到台積電的K線圖

### 1.2 使用JSFiddle測試

**步驟:**
1. 打開 [JSFiddle](https://jsfiddle.net/)
2. 在HTML部分貼上測試代碼
3. 點擊 "Run" 運行
4. 檢查結果

---

## 方法2: 本地HTTPS服務器

### 2.1 使用Python HTTPS服務器

```bash
# 啟動HTTPS測試服務器
uv run python test_https_server.py

# 然後訪問: https://localhost:8443/demo_charts/2330_fixed.html
```

**注意:** 瀏覽器會顯示證書警告，點擊「繼續訪問」即可。

### 2.2 使用Node.js http-server

```bash
# 安裝http-server
npm install -g http-server

# 啟動HTTPS服務器
http-server -S -C server.crt -K server.key -p 8443

# 訪問: https://localhost:8443/demo_charts/2330_fixed.html
```

---

## 方法3: 部署到免費託管服務

### 3.1 使用GitHub Pages

1. 創建GitHub倉庫
2. 上傳demo_charts目錄
3. 啟用GitHub Pages (Settings > Pages)
4. 訪問: `https://你的用戶名.github.io/倉庫名/demo_charts/2330_fixed.html`

### 3.2 使用Netlify

1. 訪問 [Netlify](https://netlify.com)
2. 拖拽demo_charts文件夾到部署區域
3. 獲得HTTPS URL，例如: `https://random-name.netlify.app/2330_fixed.html`

### 3.3 使用Vercel

1. 訪問 [Vercel](https://vercel.com)
2. 上傳項目文件
3. 自動獲得HTTPS域名

---

## 方法4: API服務器測試

### 4.1 啟動FastAPI服務器

```bash
# 啟動API服務器
uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 訪問API端點 (HTTP版本，數據可能受限)
http://localhost:8000/chart/taiwan-widget/2330
```

### 4.2 使用ngrok創建HTTPS隧道

```bash
# 安裝ngrok: https://ngrok.com/download
# 啟動API服務器後運行:
ngrok http 8000

# 使用ngrok提供的HTTPS URL測試
https://random-string.ngrok.io/chart/taiwan-widget/2330
```

---

## 🧪 測試檢查清單

### 基本功能測試
- [ ] Widget是否載入
- [ ] 符號顯示是否正確 (TWSE:2330)
- [ ] 界面是否美觀 (深色主題)
- [ ] 右側信息面板是否顯示

### 數據顯示測試  
- [ ] OHLC數據是否顯示實際數字
- [ ] K線圖是否正常顯示
- [ ] 成交量是否顯示
- [ ] RSI指標是否工作

### 交互功能測試
- [ ] 時間周期切換是否正常
- [ ] 圖表工具是否可用
- [ ] 符號搜索是否工作
- [ ] 右側按鈕切換是否正常

### 其他台股測試
測試其他台股符號:
- `TWSE:2454` (聯發科)
- `TWSE:0050` (台灣50)
- `TWSE:2881` (富邦金)

---

## 🚨 常見問題排除

### Q1: 仍然顯示 "∅" 數據
**可能原因:**
- 使用HTTP而非HTTPS
- 網絡連接問題
- TradingView服務暫時不可用

**解決方案:**
- 確保使用HTTPS環境
- 檢查網絡連接
- 稍後重試

### Q2: 顯示 "無效商品"
**可能原因:**
- 符號格式錯誤
- 市場休市時間

**解決方案:**
- 確認使用 TWSE:2330 格式
- 在台股交易時間測試

### Q3: Widget無法載入
**可能原因:**
- JavaScript被阻擋
- CORS政策限制

**解決方案:**
- 檢查瀏覽器控制台錯誤
- 使用標準的HTTPS環境

---

## ✅ 成功標準

如果以下條件全部達成，代表台股Widget實作成功:

1. **符號正確**: 顯示 `TWSE:2330` 而不是 `TPE:2330`
2. **數據顯示**: OHLC顯示實際數字 (例如: 開=580.00)
3. **圖表正常**: 可以看到台積電的實際K線走勢
4. **功能完整**: 技術指標、工具列都正常工作
5. **界面美觀**: 深色主題，響應式佈局

---

## 📊 測試結果記錄

| 測試方法 | 環境 | 符號格式 | 數據顯示 | 結果 |
|---------|------|----------|----------|------|
| CodePen | HTTPS | ✅/❌ | ✅/❌ | 成功/失敗 |
| 本地HTTPS | HTTPS | ✅/❌ | ✅/❌ | 成功/失敗 |
| GitHub Pages | HTTPS | ✅/❌ | ✅/❌ | 成功/失敗 |
| ngrok | HTTPS | ✅/❌ | ✅/❌ | 成功/失敗 |

---

## 🎉 預期結果

在HTTPS環境下，你應該看到:
- 台積電的實際股價 (約500-600 TWD範圍)
- 完整的K線圖表
- 正常的成交量數據
- 可用的技術指標 (RSI, MACD等)

這將證明我們的台股Widget解決方案完全成功，可以取代需要昂貴授權的TradingView Charting Library！