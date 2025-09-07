# 用戶認證與付費訂閱系統架構設計

## 🎯 功能需求

### 基本功能
- ✅ **未登入用戶**: 可瀏覽介面，AI分析功能關閉
- ✅ **登入系統**: Email註冊 + Google OAuth第三方登入
- ✅ **使用次數限制**: 新用戶3次免費 → 每日1次免費
- ✅ **付費訂閱**: 月費5美金，支持信用卡、綠界科技、藍新金流

### 技術架構

## 📊 數據庫設計

### 1. 用戶表 (users)
```sql
- id: UUID (Primary Key)
- email: String (唯一索引)
- password_hash: String (可為空，OAuth用戶)
- google_id: String (可為空，OAuth ID)
- full_name: String
- avatar_url: String (可為空)
- email_verified: Boolean (默認False)
- verification_token: String (可為空)
- created_at: DateTime
- updated_at: DateTime
- is_active: Boolean (默認True)
- last_login: DateTime (可為空)
```

### 2. 使用記錄表 (usage_records)  
```sql
- id: UUID (Primary Key)
- user_id: UUID (外鍵 → users.id)
- action_type: String (ai_analysis, chart_view, etc.)
- created_at: DateTime
- metadata: JSON (分析詳情、股票代碼等)
```

### 3. 訂閱表 (subscriptions)
```sql
- id: UUID (Primary Key) 
- user_id: UUID (外鍵 → users.id)
- plan_type: String (free, premium)
- status: String (active, cancelled, expired)
- started_at: DateTime
- expires_at: DateTime (可為空，終身)
- payment_method: String (credit_card, ecpay, newebpay)
- external_subscription_id: String (第三方訂閱ID)
```

### 4. 支付記錄表 (payments)
```sql
- id: UUID (Primary Key)
- user_id: UUID (外鍵)
- subscription_id: UUID (外鍵)
- amount: Decimal
- currency: String (USD, TWD)
- payment_method: String
- payment_provider: String (stripe, ecpay, newebpay)
- external_transaction_id: String
- status: String (pending, completed, failed, refunded)
- created_at: DateTime
```

### 5. 免費配額表 (free_quotas)
```sql
- id: UUID (Primary Key)
- user_id: UUID (外鍵)
- total_free_uses: Integer (新用戶3次)
- used_free_uses: Integer (已使用次數)
- daily_reset_date: Date (每日重置日期)
- created_at: DateTime
- updated_at: DateTime
```

## 🔐 認證系統架構

### JWT Token 設計
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "subscription_status": "free|premium",
  "exp": "過期時間",
  "iat": "發行時間"
}
```

### 權限等級
1. **Guest (未登入)**: 僅可瀏覽介面
2. **Free User (免費用戶)**: 有限AI分析次數
3. **Premium User (付費用戶)**: 無限制使用

## 💳 支付系統整合

### 1. Stripe (國際信用卡)
- 月費訂閱: $5/月
- Webhook處理訂閱狀態變更
- 自動續費管理

### 2. 綠界科技 ECPay (台灣)
- 支持信用卡、ATM、超商付款
- 定期定額扣款
- 即時付款通知

### 3. 藍新金流 NewebPay (台灣)
- 多元支付方式
- 定期扣款服務
- 金流狀態同步

## 🔄 系統流程

### 註冊流程
1. **Email註冊**: 
   - 輸入Email → 密碼 → 發送驗證郵件 → 驗證完成
2. **Google OAuth**:
   - 點擊Google登入 → 授權 → 自動創建帳戶

### AI使用流程
1. **檢查登入狀態**: 未登入 → 顯示登入提示
2. **檢查訂閱狀態**: 
   - 免費用戶 → 檢查配額
   - 付費用戶 → 直接允許
3. **記錄使用**: 每次AI分析記錄到usage_records

### 付費升級流程
1. **選擇方案**: 月費$5美金
2. **選擇支付方式**: Stripe/ECPay/NewebPay  
3. **完成支付**: 更新訂閱狀態
4. **開通服務**: 立即生效

## 🎨 前端UI設計

### 登入/註冊頁面
- 響應式設計，支持手機/桌面
- Email表單 + Google一鍵登入按鈕
- 多語言支持 (中文/英文)

### 用戶儀表板
- 顯示當前訂閱狀態
- 使用次數統計
- 付費升級入口
- 帳戶設定管理

### 權限控制組件
- AI分析按鈕: 根據權限顯示/隱藏
- 配額提示: 顯示剩餘使用次數
- 升級提示: 引導付費用戶升級

## 🛠️ 技術實現

### 後端 (FastAPI)
```python
# 新增模塊
src/auth/
  - models.py          # 數據庫模型
  - schemas.py         # Pydantic schemas
  - crud.py            # 數據庫操作
  - auth.py            # JWT認證邏輯
  - oauth.py           # Google OAuth
  - permissions.py     # 權限檢查

src/payments/
  - stripe_service.py  # Stripe整合
  - ecpay_service.py   # 綠界科技
  - newebpay_service.py # 藍新金流
  - webhook_handlers.py # 支付回調
```

### 前端 (Next.js)
```typescript
// 新增組件和頁面
components/auth/
  - LoginForm.tsx      # 登入表單
  - RegisterForm.tsx   # 註冊表單
  - GoogleAuthButton.tsx # Google登入
  - UserProfile.tsx    # 用戶資料

contexts/
  - AuthContext.tsx    # 認證狀態管理
  - SubscriptionContext.tsx # 訂閱狀態

pages/auth/
  - login.tsx          # 登入頁
  - register.tsx       # 註冊頁  
  - dashboard.tsx      # 用戶儀表板
```

## 📋 開發進度規劃

### Phase 1: 基礎認證系統
- ✅ 數據庫模型設計
- ✅ JWT認證實現
- ✅ Email註冊/登入
- ✅ 基礎權限控制

### Phase 2: Google OAuth整合
- ✅ Google OAuth配置
- ✅ 第三方登入流程
- ✅ 用戶資料同步

### Phase 3: 使用配額系統
- ✅ 免費配額追踪
- ✅ 使用記錄統計
- ✅ 每日重置邏輯

### Phase 4: 支付系統整合
- ✅ Stripe月費訂閱
- ✅ 綠界科技支付
- ✅ 藍新金流支付
- ✅ Webhook處理

### Phase 5: 前端UI實現
- ✅ 認證相關頁面
- ✅ 用戶儀表板
- ✅ 權限控制組件
- ✅ 響應式設計

### Phase 6: 整合測試
- ✅ 端到端測試
- ✅ 支付流程測試  
- ✅ 權限控制測試
- ✅ 多語言測試

## 🔒 安全考慮

### 數據保護
- 密碼使用bcrypt加密
- JWT Token設定適當過期時間
- 敏感數據加密存儲

### API安全
- 率限制(Rate Limiting)
- CORS設定
- 輸入驗證和過濾

### 支付安全
- HTTPS強制加密
- Webhook簽名驗證
- 支付狀態同步機制

## 🚀 部署配置

### 環境變數
```env
# JWT設定
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ECPay綠界科技
ECPAY_MERCHANT_ID=your-merchant-id
ECPAY_HASH_KEY=your-hash-key
ECPAY_HASH_IV=your-hash-iv

# NewebPay藍新金流
NEWEBPAY_MERCHANT_ID=your-merchant-id
NEWEBPAY_HASH_KEY=your-hash-key  
NEWEBPAY_HASH_IV=your-hash-iv
```