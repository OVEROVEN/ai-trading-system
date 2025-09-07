# Google OAuth 設置指南

## 📋 概述

本系統支持 Google OAuth 2.0 第三方登入功能，用戶可以使用 Google 帳號快速註冊和登入。

## 🔧 設置步驟

### 1. 創建 Google Cloud 項目

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新項目或選擇現有項目
3. 啟用 `Google+ API` 或 `Google Identity Services`

### 2. 配置 OAuth 2.0 憑證

1. 在 Google Cloud Console 中，前往 **APIs & Services** > **Credentials**
2. 點擊 **Create Credentials** > **OAuth 2.0 Client IDs**
3. 選擇應用程式類型：**Web Application**
4. 配置授權回調 URI：
   - 開發環境：`http://localhost:3000/auth/google/callback`
   - 生產環境：`https://yourdomain.com/auth/google/callback`

### 3. 獲取憑證信息

完成配置後，您將獲得：
- **Client ID**: 類似 `123456789-abcdef.apps.googleusercontent.com`
- **Client Secret**: 類似 `GOCSPX-abcdefghijklmnopqrstuvwx`

### 4. 配置環境變量

在 `.env` 文件中設置以下環境變量：

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-actual-google-client-id-from-console
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret-from-console
```

## 🔍 API 端點

### 檢查 OAuth 狀態
```bash
GET /api/auth/google/status
```

響應：
```json
{
  "google_oauth_enabled": true,
  "client_id": "123456789-ab..."
}
```

### 啟動 OAuth 登入
```bash
GET /api/auth/google/login?redirect_uri=http://localhost:3000/auth/google/callback
```

響應：
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "state": "csrf_protection_token",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}
```

### 處理 OAuth 回調
```bash
POST /api/auth/google/callback
Content-Type: application/json

{
  "code": "authorization_code_from_google",
  "state": "csrf_protection_token",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}
```

響應：
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "user_uuid",
    "email": "user@gmail.com",
    "full_name": "User Name",
    "is_premium": false
  }
}
```

## 🔄 OAuth 流程

1. **前端調用登入端點**: `GET /api/auth/google/login`
2. **獲取授權 URL**: 系統返回 Google 授權頁面 URL
3. **用戶授權**: 用戶在 Google 頁面中授權應用
4. **Google 重定向**: Google 將用戶重定向到回調 URL 並帶上授權碼
5. **前端調用回調端點**: `POST /api/auth/google/callback` 並傳遞授權碼
6. **系統驗證和創建用戶**: 
   - 使用授權碼交換訪問令牌
   - 獲取用戶信息
   - 創建或更新用戶記錄
   - 生成 JWT token
7. **返回用戶信息**: 前端獲得用戶信息和認證 token

## 🛡️ 安全特性

### CSRF 保護
- 每次登入請求都會生成唯一的 `state` 參數
- 回調時驗證 `state` 參數，防止 CSRF 攻擊

### 用戶數據處理
- **新用戶**: 自動創建帳戶並分配免費配額
- **現有用戶**: 更新最後登入時間
- **郵箱衝突**: 如果郵箱已被其他帳戶使用，返回錯誤提示

### Token 安全
- 生成的 JWT token 包含用戶 ID、郵箱和訂閱狀態
- Token 有效期為 24 小時
- 支持 token 刷新機制

## 🧪 測試

### 檢查配置狀態
```bash
curl -X GET "http://localhost:8000/api/auth/google/status"
```

### 測試登入流程
```bash
# 1. 獲取授權 URL
curl -X GET "http://localhost:8000/api/auth/google/login"

# 2. 手動在瀏覽器中完成 Google 授權
# 3. 獲取授權碼後調用回調端點
curl -X POST "http://localhost:8000/api/auth/google/callback" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "4/0AQlEd8y...",
    "state": "state_from_step_1",
    "redirect_uri": "http://localhost:3000/auth/google/callback"
  }'
```

## 🚨 故障排除

### OAuth 未配置
如果看到 "Google OAuth 未配置" 錯誤：
1. 檢查 `.env` 文件中的 `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET`
2. 確保值不是占位符文本
3. 重啟 API 服務器

### 回調 URI 不匹配
如果看到 "redirect_uri_mismatch" 錯誤：
1. 檢查 Google Cloud Console 中配置的回調 URI
2. 確保請求中的 `redirect_uri` 與配置完全匹配
3. 注意 HTTP vs HTTPS 的區別

### 無效授權碼
如果看到 "invalid_grant" 錯誤：
1. 授權碼只能使用一次
2. 授權碼有時效限制（約 10 分鐘）
3. 重新啟動 OAuth 流程獲取新的授權碼

## 📱 前端集成

### React 示例
```typescript
// 啟動 OAuth 登入
const handleGoogleLogin = async () => {
  const response = await fetch('/api/auth/google/login');
  const data = await response.json();
  
  // 重定向到 Google 授權頁面
  window.location.href = data.authorization_url;
};

// 處理 OAuth 回調 (在回調頁面中)
const handleOAuthCallback = async () => {
  const params = new URLSearchParams(window.location.search);
  const code = params.get('code');
  const state = params.get('state');
  
  if (code && state) {
    const response = await fetch('/api/auth/google/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        state,
        redirect_uri: window.location.origin + '/auth/google/callback'
      }),
    });
    
    const userData = await response.json();
    // 存儲 token 並重定向到主頁面
    localStorage.setItem('token', userData.access_token);
    window.location.href = '/dashboard';
  }
};
```

## 📊 系統整合

OAuth 登入完成後，用戶將獲得：
- ✅ 免費 AI 分析配額（新用戶 3 次，每日 1 次）
- ✅ 完整的股票搜索和圖表功能
- ✅ 個人化儀表板和設置
- ✅ 訂閱升級選項

## 🔄 下一步

完成 Google OAuth 集成後，可以繼續實現：
1. 📧 郵件驗證系統
2. 💳 付費訂閱整合
3. 📱 前端用戶界面
4. 📊 用戶行為分析

---

**注意**: 在生產環境中，確保使用 HTTPS 並配置適當的 CORS 策略。