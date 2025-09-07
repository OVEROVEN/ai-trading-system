# 🔐 Google OAuth 設置指引

## 您需要完成以下步驟：

### 1. Google Cloud Console 設置

1. **前往**: https://console.cloud.google.com/
2. **創建項目** 或選擇現有項目
3. **啟用API**: 搜尋並啟用 "Google+ API"
4. **創建憑證**:
   - 前往 APIs & Services > Credentials
   - 點擊 "Create Credentials" > "OAuth 2.0 Client IDs"
   - 選擇 "Web application"
   - 設置以下回調URL:

```
授權的JavaScript來源：
http://localhost:3000

授權的重新導向URI：
http://localhost:3000/auth/google/callback
```

### 2. 獲取憑證後

完成設置後，您將獲得：
- **Client ID**: 形如 `123456789-abcdefg.apps.googleusercontent.com`
- **Client Secret**: 形如 `GOCSPX-abcdefghijklmnopqrstuvwx`

### 3. 更新 .env 文件

將憑證添加到 .env 文件中：

```env
# 將這兩行替換為您從 Google Cloud Console 獲取的真實值
GOOGLE_CLIENT_ID=您的真實Client_ID
GOOGLE_CLIENT_SECRET=您的真實Client_Secret
```

### 4. 重啟服務器

更新 .env 後，重啟後端服務器：
```bash
# 停止當前服務器 (Ctrl+C)
# 然後重新啟動
source .venv/bin/activate && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 測試Google登入

1. 前往 http://localhost:3000
2. 點擊 "Login" 按鈕
3. 點擊 "使用 Google 登入" 按鈕
4. 應該會跳轉到Google授權頁面

## 🚨 常見問題

**Q: "已封鎖存取權：授權錯誤"**
A: 這通常表示：
- Client ID 或 Client Secret 不正確
- 回調URL配置不匹配
- Google Cloud Console中的OAuth同意畫面未正確設置

**Q: "redirect_uri_mismatch"**
A: 確保Google Cloud Console中配置的回調URI完全匹配：
`http://localhost:3000/auth/google/callback`

**Q: Google OAuth按鈕不工作**
A: 檢查瀏覽器控制台錯誤，通常是憑證配置問題

---

**下一步**: 按照上述步驟設置後，Google登入功能就可以正常工作了！