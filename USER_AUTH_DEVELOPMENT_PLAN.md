# 🚀 用戶認證與API管理系統開發規劃

## 📋 項目概述

為AI交易系統新增完整的用戶管理、認證、API配額管理和付費系統，支援雲端部署和多用戶使用。

---

## 🏗️ 系統架構設計

### 核心組件架構
```
Frontend (React/Vue) → FastAPI (Auth) → Database (用戶數據)
                    ↓
FastAPI (Trading API) → Redis (會話/配額) → PostgreSQL (交易數據)
                    ↓
外部服務 (Google OAuth, Stripe支付)
```

### 技術堆疊
- **後端認證**: FastAPI + JWT + OAuth2
- **數據庫**: PostgreSQL (用戶表) + Redis (會話管理)
- **第三方登入**: Google OAuth2, Facebook (可選)
- **支付系統**: Stripe 或 PayPal
- **前端**: React (推薦) 或 Vue.js
- **部署**: Docker + AWS/Azure

---

## 📊 數據庫設計

### 新增用戶相關表

#### 1. Users 表 (用戶主表)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- 本地註冊用戶
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    
    -- 帳號狀態
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    
    -- 註冊資訊
    registration_method VARCHAR(20) DEFAULT 'local', -- local, google, facebook
    registration_date TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    
    -- API 配置
    personal_openai_key TEXT, -- 加密存儲用戶自己的API key
    api_key_is_valid BOOLEAN DEFAULT NULL,
    
    -- 用量統計
    free_api_calls_remaining INTEGER DEFAULT 3,
    total_api_calls INTEGER DEFAULT 0,
    
    -- 時間戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. User_OAuth 表 (第三方登入)
```sql
CREATE TABLE user_oauth (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL, -- google, facebook
    provider_user_id VARCHAR(100) NOT NULL,
    provider_email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);
```

#### 3. API_Usage 表 (API使用記錄)
```sql
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    
    -- AI相關使用
    ai_model_used VARCHAR(50),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    
    -- 請求詳情
    request_time TIMESTAMP DEFAULT NOW(),
    response_time_ms INTEGER,
    user_ip VARCHAR(45),
    user_agent TEXT,
    
    -- 配額扣除
    quota_deducted BOOLEAN DEFAULT FALSE,
    
    INDEX(user_id, request_time),
    INDEX(endpoint, request_time)
);
```

#### 4. User_Plans 表 (用戶訂閱方案)
```sql
CREATE TABLE user_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_name VARCHAR(50) NOT NULL, -- free, basic, premium, enterprise
    
    -- 配額設定
    monthly_api_calls INTEGER DEFAULT 0,
    current_period_calls INTEGER DEFAULT 0,
    
    -- 訂閱狀態
    status VARCHAR(20) DEFAULT 'active', -- active, cancelled, expired
    billing_cycle VARCHAR(20) DEFAULT 'monthly', -- monthly, yearly
    
    -- 時間管理
    current_period_start TIMESTAMP DEFAULT NOW(),
    current_period_end TIMESTAMP,
    next_billing_date TIMESTAMP,
    
    -- 支付資訊
    stripe_subscription_id VARCHAR(100),
    price_usd DECIMAL(8,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 5. Payment_History 表 (支付歷史)
```sql
CREATE TABLE payment_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(100),
    
    amount_usd DECIMAL(8,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL, -- succeeded, failed, pending
    
    description TEXT,
    receipt_url VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 認證系統設計

### JWT Token 策略
- **Access Token**: 15分鐘過期，包含用戶基本信息和權限
- **Refresh Token**: 7天過期，用於刷新Access Token
- **API Key Token**: 不過期，用於外部API調用

### Token 內容結構
```json
{
  "sub": "user_id",
  "username": "john_doe",
  "email": "john@example.com",
  "is_premium": true,
  "plan": "premium",
  "api_calls_remaining": 1000,
  "exp": 1234567890,
  "iat": 1234567890
}
```

### 密碼安全
- 使用 `bcrypt` 進行密碼哈希
- 密碼強度要求：8位以上，包含大小寫字母和數字
- 支援密碼重置功能（郵件驗證）

---

## 🎯 API配額管理系統

### 配額分級設計

#### 免費方案 (Free Tier)
- **AI分析次數**: 3次（註冊贈送）
- **技術指標分析**: 無限制
- **圖表生成**: 無限制  
- **回測功能**: 3次

#### 基礎方案 (Basic - $9.99/月)
- **AI分析次數**: 100次/月
- **所有技術分析**: 無限制
- **圖表功能**: 無限制
- **回測功能**: 50次/月
- **數據導出**: 支援

#### 高級方案 (Premium - $29.99/月)
- **AI分析次數**: 500次/月
- **高級AI模型**: 支援GPT-4o
- **實時WebSocket**: 支援
- **自定義策略**: 支援
- **優先客服**: 支援

#### 企業方案 (Enterprise - $99.99/月)
- **AI分析次數**: 2000次/月
- **所有功能**: 無限制
- **API密鑰管理**: 支援
- **白標部署**: 支援
- **專屬客服**: 支援

### 配額執行邏輯
```python
async def check_api_quota(user_id: int, endpoint: str) -> bool:
    """檢查用戶API配額是否充足"""
    user = await get_user_with_plan(user_id)
    
    if user.personal_openai_key and user.api_key_is_valid:
        return True  # 用戶使用自己的API key，不受限制
    
    if endpoint in AI_ENDPOINTS:
        return user.plan.current_period_calls > 0
    
    return True  # 非AI功能不受限制
```

---

## 🌐 第三方登入整合

### Google OAuth2 整合
```python
# OAuth2 配置
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"
GOOGLE_REDIRECT_URI = "https://your-domain.com/auth/google/callback"

# 登入流程
@app.get("/auth/google")
async def google_login():
    return RedirectResponse(google_oauth_url)

@app.get("/auth/google/callback")
async def google_callback(code: str):
    # 1. 交換授權碼獲取token
    # 2. 獲取用戶信息
    # 3. 創建或更新用戶
    # 4. 生成JWT token
    # 5. 重定向到前端
```

### 支援的第三方平台
1. **Google** - 優先實現
2. **Facebook** - 可選
3. **GitHub** - 面向開發者用戶（可選）

---

## 💳 支付系統設計

### Stripe 整合
```python
import stripe

# 創建訂閱
async def create_subscription(user_id: int, plan: str):
    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": user_id}
    )
    
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": PLAN_PRICE_IDS[plan]}]
    )
    
    return subscription
```

### 支付方案
- **月付**: 標準價格
- **年付**: 8.5折優惠
- **企業定製**: 聯繫客服

### 支付安全
- PCI DSS 合規（通過Stripe）
- 不存儲信用卡信息
- 支援多種支付方式：信用卡、PayPal、Apple Pay

---

## 🛡️ 安全考量

### API安全
- **速率限制**: Redis實現，每用戶每分鐘限制請求數
- **IP白名單**: 企業用戶可設置IP白名單
- **請求簽名**: 重要API支援HMAC簽名驗證

### 數據安全  
- **加密存儲**: 用戶API密鑰使用AES-256加密
- **HTTPS強制**: 所有API端點強制HTTPS
- **SQL注入防護**: 使用SQLAlchemy ORM
- **XSS防護**: 輸入輸出過濾

### 隱私保護
- **GDPR合規**: 支援用戶數據導出和刪除
- **日誌脫敏**: 敏感信息不記錄在日誌中
- **最小權限**: API只返回必要的用戶信息

---

## 📱 前端設計

### 頁面結構
```
/login          - 登入頁面
/register       - 註冊頁面  
/dashboard      - 用戶儀表板
/profile        - 個人設置
/billing        - 訂閱和付費管理
/api-keys       - API密鑰管理
/usage          - 用量統計
```

### 用戶體驗設計
- **響應式設計**: 支援桌面和移動端
- **深色模式**: 支援明/暗主題切換
- **載入狀態**: 清晰的載入和錯誤提示
- **引導教程**: 新用戶引導和功能介紹

---

## 🚀 開發路線圖

### 第一階段 (2-3週): 基礎認證
- [ ] 用戶數據庫設計和創建
- [ ] 基本註冊/登入API
- [ ] JWT token管理
- [ ] 密碼重置功能
- [ ] 基礎前端認證頁面

### 第二階段 (2-3週): 第三方登入
- [ ] Google OAuth2 整合
- [ ] 用戶資料同步
- [ ] 社交登入前端界面
- [ ] 帳號綁定功能

### 第三階段 (3-4週): API配額系統
- [ ] 配額檢查中介軟體
- [ ] 用量統計和記錄
- [ ] 方案管理系統
- [ ] 用戶儀表板

### 第四階段 (3-4週): 支付整合
- [ ] Stripe支付整合
- [ ] 訂閱管理
- [ ] 發票和收據
- [ ] 付費升級流程

### 第五階段 (2-3週): 高級功能
- [ ] API密鑰管理
- [ ] 使用量分析
- [ ] 管理員後台
- [ ] 性能優化

### 第六階段 (1-2週): 測試與部署
- [ ] 完整測試套件
- [ ] 安全測試
- [ ] 雲端部署腳本
- [ ] 監控和日誌

---

## 📊 估算成本

### 開發成本
- **總開發時間**: 15-20週
- **核心功能**: 12週
- **測試和優化**: 3-8週

### 運營成本 (月度)
- **數據庫**: AWS RDS $50-200/月
- **Redis**: AWS ElastiCache $20-100/月  
- **服務器**: AWS EC2 $100-500/月
- **Stripe手續費**: 2.9% + $0.30/筆
- **第三方服務**: ~$50/月

### 預期收入
- **基礎方案**: $9.99/月 × 用戶數
- **高級方案**: $29.99/月 × 用戶數
- **企業方案**: $99.99/月 × 用戶數

---

## 🎯 成功指標

### 技術指標
- **API響應時間**: < 200ms (95%ile)
- **系統可用性**: > 99.9%
- **用戶註冊流程**: < 30秒完成
- **支付成功率**: > 99%

### 業務指標  
- **用戶轉化率**: 免費 → 付費 > 5%
- **用戶留存率**: 月度 > 80%
- **客服響應**: < 2小時
- **系統擴展性**: 支援 10,000+ 並發用戶

---

## ⚡ 快速開始計劃

### 立即可開始的任務
1. **數據庫設計確認** - 審核表結構設計
2. **技術選型確認** - 確認前端框架選擇
3. **第三方帳號申請** - 申請Google OAuth2憑證
4. **開發環境準備** - 設置Docker開發環境

### 第一週目標
- 完成用戶數據庫表創建
- 實現基本的註冊/登入API
- 建立JWT token生成和驗證
- 創建簡單的前端登入頁面

---

## 📝 注意事項

### 重要提醒
- **數據遷移**: 現有交易數據需要與用戶關聯
- **API相容性**: 確保現有API端點向後相容
- **測試策略**: 分階段上線，先內測再公測
- **文檔更新**: 同步更新API文檔和用戶指南

### 風險控制
- **技術風險**: 預留備用方案
- **安全風險**: 定期安全審計  
- **業務風險**: 灰度發佈，逐步放量
- **合規風險**: 確保符合當地法規

---

*此開發計劃將根據實際開發進度和反饋持續更新優化。*