-- ================================================
-- 用戶認證系統數據庫遷移計劃
-- ================================================

-- 第一階段: 創建用戶認證相關表

-- 1. 用戶主表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    
    -- 基本信息
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- bcrypt哈希，OAuth用戶可為空
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    phone_number VARCHAR(20),
    
    -- 帳號狀態
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP NULL,
    
    -- 註冊資訊
    registration_method VARCHAR(20) DEFAULT 'local', -- local, google, facebook
    registration_date TIMESTAMP DEFAULT NOW(),
    registration_ip VARCHAR(45),
    last_login TIMESTAMP,
    last_login_ip VARCHAR(45),
    login_count INTEGER DEFAULT 0,
    
    -- API 配置
    personal_openai_key TEXT, -- AES-256 加密存儲
    api_key_is_valid BOOLEAN DEFAULT NULL,
    api_key_last_validated TIMESTAMP,
    
    -- 用量統計 (當前週期)
    free_api_calls_remaining INTEGER DEFAULT 3,
    total_api_calls INTEGER DEFAULT 0,
    current_period_calls INTEGER DEFAULT 0,
    
    -- 偏好設置
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    theme VARCHAR(20) DEFAULT 'light', -- light, dark
    
    -- 時間戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL -- 軟刪除
);

-- 創建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_registration_date ON users(registration_date);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_is_premium ON users(is_premium);

-- 2. OAuth第三方登入表
CREATE TABLE user_oauth (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- OAuth資訊
    provider VARCHAR(20) NOT NULL, -- google, facebook, github
    provider_user_id VARCHAR(100) NOT NULL,
    provider_email VARCHAR(255),
    provider_name VARCHAR(100),
    provider_avatar VARCHAR(500),
    
    -- Token資訊
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    scope TEXT,
    
    -- 額外數據
    provider_data JSONB, -- 存儲完整的OAuth響應
    
    -- 狀態
    is_primary BOOLEAN DEFAULT FALSE, -- 是否為主要登入方式
    last_used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(provider, provider_user_id)
);

-- 創建索引
CREATE INDEX idx_user_oauth_user_id ON user_oauth(user_id);
CREATE INDEX idx_user_oauth_provider ON user_oauth(provider);
CREATE UNIQUE INDEX idx_user_oauth_provider_id ON user_oauth(provider, provider_user_id);

-- 3. API使用記錄表
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 請求資訊
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    
    -- AI相關使用
    ai_model_used VARCHAR(50),
    ai_task_type VARCHAR(50), -- chat, analysis, backtest, strategy, vision
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    
    -- 請求詳情
    request_time TIMESTAMP DEFAULT NOW(),
    response_time_ms INTEGER,
    user_ip VARCHAR(45),
    user_agent TEXT,
    
    -- 配額和計費
    quota_deducted BOOLEAN DEFAULT FALSE,
    quota_type VARCHAR(20), -- free, basic, premium, personal_key
    
    -- 錯誤信息
    error_message TEXT,
    
    -- 請求/響應詳情 (可選，調試用)
    request_payload JSONB,
    response_payload JSONB
);

-- 創建分區表按月分區（性能優化）
CREATE INDEX idx_api_usage_user_time ON api_usage(user_id, request_time);
CREATE INDEX idx_api_usage_endpoint_time ON api_usage(endpoint, request_time);
CREATE INDEX idx_api_usage_ai_model ON api_usage(ai_model_used) WHERE ai_model_used IS NOT NULL;
CREATE INDEX idx_api_usage_cost ON api_usage(cost_usd) WHERE cost_usd > 0;

-- 4. 用戶訂閱計劃表
CREATE TABLE user_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 計劃資訊
    plan_name VARCHAR(50) NOT NULL, -- free, basic, premium, enterprise
    plan_price DECIMAL(8,2) DEFAULT 0,
    billing_cycle VARCHAR(20) DEFAULT 'monthly', -- monthly, yearly
    
    -- 配額設定
    monthly_api_calls INTEGER DEFAULT 0,
    current_period_calls INTEGER DEFAULT 0,
    can_use_advanced_ai BOOLEAN DEFAULT FALSE,
    can_use_vision_ai BOOLEAN DEFAULT FALSE,
    max_concurrent_requests INTEGER DEFAULT 10,
    
    -- 功能權限
    features JSONB, -- 存儲功能權限JSON
    
    -- 訂閱狀態
    status VARCHAR(20) DEFAULT 'active', -- active, cancelled, expired, suspended
    
    -- 時間管理
    current_period_start TIMESTAMP DEFAULT NOW(),
    current_period_end TIMESTAMP,
    next_billing_date TIMESTAMP,
    trial_ends_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- 支付資訊
    stripe_customer_id VARCHAR(100),
    stripe_subscription_id VARCHAR(100),
    stripe_price_id VARCHAR(100),
    
    -- 折扣和優惠
    discount_percent INTEGER DEFAULT 0,
    coupon_code VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 創建索引
CREATE INDEX idx_user_plans_user_id ON user_plans(user_id);
CREATE INDEX idx_user_plans_status ON user_plans(status);
CREATE INDEX idx_user_plans_stripe_sub ON user_plans(stripe_subscription_id);
CREATE INDEX idx_user_plans_period_end ON user_plans(current_period_end);

-- 5. 支付歷史表
CREATE TABLE payment_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 支付基本資訊
    payment_intent_id VARCHAR(100), -- Stripe payment intent ID
    invoice_id VARCHAR(100), -- Stripe invoice ID
    
    -- 金額資訊
    amount_cents INTEGER NOT NULL, -- 以分為單位，避免浮點數問題
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- 支付狀態
    status VARCHAR(20) NOT NULL, -- pending, succeeded, failed, cancelled, refunded
    failure_reason TEXT,
    
    -- 支付方式
    payment_method VARCHAR(50), -- card, paypal, bank_transfer
    last_4_digits VARCHAR(4), -- 信用卡後四位
    
    -- 訂單資訊
    plan_name VARCHAR(50),
    billing_period_start TIMESTAMP,
    billing_period_end TIMESTAMP,
    
    -- 收據和發票
    receipt_url VARCHAR(500),
    invoice_url VARCHAR(500),
    
    -- 退款資訊
    refund_amount_cents INTEGER DEFAULT 0,
    refunded_at TIMESTAMP,
    
    -- 時間戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 創建索引
CREATE INDEX idx_payment_history_user_id ON payment_history(user_id);
CREATE INDEX idx_payment_history_status ON payment_history(status);
CREATE INDEX idx_payment_history_created ON payment_history(created_at);
CREATE INDEX idx_payment_history_payment_intent ON payment_history(payment_intent_id);

-- 6. 用戶會話表 (可選，用於追蹤活躍會話)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 會話資訊
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    device_fingerprint VARCHAR(255),
    
    -- 設備資訊
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(20), -- desktop, mobile, tablet
    browser VARCHAR(50),
    os VARCHAR(50),
    country VARCHAR(2),
    
    -- 會話狀態
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 創建索引
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active, expires_at);

-- 7. 系統設定表 (存儲全局配置)
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'string', -- string, integer, float, boolean, json
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- 是否可以通過API獲取
    category VARCHAR(50) DEFAULT 'general',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 插入初始系統設定
INSERT INTO system_settings (key, value, value_type, description, category) VALUES
('free_trial_api_calls', '3', 'integer', '免費用戶初始API調用次數', 'billing'),
('max_api_calls_per_minute', '60', 'integer', '每分鐘最大API調用次數', 'rate_limiting'),
('session_timeout_hours', '24', 'integer', '會話超時時間（小時）', 'security'),
('require_email_verification', 'true', 'boolean', '是否要求郵箱驗證', 'security'),
('maintenance_mode', 'false', 'boolean', '系統維護模式', 'system'),
('default_ai_model', 'gpt-3.5-turbo', 'string', '默認AI模型', 'ai'),
('max_file_upload_size', '10485760', 'integer', '最大文件上傳大小（字節）', 'system');

-- ================================================
-- 第二階段: 修改現有表以支持用戶關聯
-- ================================================

-- 為現有表添加用戶關聯
ALTER TABLE stock_prices ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE technical_indicators ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE technical_patterns ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE trading_signals ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE ai_analysis ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE backtest_results ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- 添加索引
CREATE INDEX idx_stock_prices_user_id ON stock_prices(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_technical_indicators_user_id ON technical_indicators(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_technical_patterns_user_id ON technical_patterns(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_trading_signals_user_id ON trading_signals(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_ai_analysis_user_id ON ai_analysis(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_backtest_results_user_id ON backtest_results(user_id) WHERE user_id IS NOT NULL;

-- ================================================
-- 第三階段: 創建視圖和函數
-- ================================================

-- 用戶統計視圖
CREATE VIEW user_statistics AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.registration_date,
    u.is_premium,
    up.plan_name,
    up.current_period_calls,
    up.monthly_api_calls,
    COUNT(au.id) as total_api_calls_made,
    SUM(au.cost_usd) as total_spent_usd,
    u.last_login,
    u.login_count
FROM users u
LEFT JOIN user_plans up ON u.id = up.user_id AND up.status = 'active'
LEFT JOIN api_usage au ON u.id = au.user_id
GROUP BY u.id, up.plan_name, up.current_period_calls, up.monthly_api_calls;

-- 每日用量統計視圖
CREATE VIEW daily_usage_stats AS
SELECT 
    DATE(request_time) as usage_date,
    COUNT(*) as total_requests,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(CASE WHEN ai_model_used IS NOT NULL THEN 1 ELSE 0 END) as ai_requests,
    SUM(cost_usd) as total_cost_usd,
    AVG(response_time_ms) as avg_response_time
FROM api_usage
WHERE request_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(request_time)
ORDER BY usage_date DESC;

-- 檢查用戶配額的函數
CREATE OR REPLACE FUNCTION check_user_quota(p_user_id INTEGER, p_endpoint VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    user_plan RECORD;
    current_calls INTEGER;
    is_ai_endpoint BOOLEAN;
BEGIN
    -- 檢查是否為AI端點
    is_ai_endpoint := p_endpoint LIKE '%/ai/%' OR p_endpoint LIKE '%/analyze%';
    
    -- 如果不是AI端點，直接允許
    IF NOT is_ai_endpoint THEN
        RETURN TRUE;
    END IF;
    
    -- 獲取用戶計劃
    SELECT up.*, u.personal_openai_key, u.api_key_is_valid
    INTO user_plan
    FROM user_plans up
    JOIN users u ON up.user_id = u.id
    WHERE up.user_id = p_user_id 
    AND up.status = 'active'
    ORDER BY up.created_at DESC
    LIMIT 1;
    
    -- 如果用戶有有效的個人API密鑰，不限制
    IF user_plan.personal_openai_key IS NOT NULL AND user_plan.api_key_is_valid = TRUE THEN
        RETURN TRUE;
    END IF;
    
    -- 檢查當前週期使用量
    IF user_plan.current_period_calls >= user_plan.monthly_api_calls THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 更新用戶配額使用量的函數
CREATE OR REPLACE FUNCTION update_user_quota(p_user_id INTEGER, p_endpoint VARCHAR)
RETURNS VOID AS $$
DECLARE
    is_ai_endpoint BOOLEAN;
BEGIN
    -- 檢查是否為AI端點
    is_ai_endpoint := p_endpoint LIKE '%/ai/%' OR p_endpoint LIKE '%/analyze%';
    
    -- 只有AI端點才扣除配額
    IF is_ai_endpoint THEN
        UPDATE user_plans 
        SET current_period_calls = current_period_calls + 1,
            updated_at = NOW()
        WHERE user_id = p_user_id 
        AND status = 'active';
        
        -- 更新用戶總調用次數
        UPDATE users 
        SET total_api_calls = total_api_calls + 1,
            updated_at = NOW()
        WHERE id = p_user_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 重置用戶週期配額的函數
CREATE OR REPLACE FUNCTION reset_user_quotas()
RETURNS VOID AS $$
BEGIN
    UPDATE user_plans 
    SET current_period_calls = 0,
        current_period_start = NOW(),
        current_period_end = NOW() + INTERVAL '1 month',
        updated_at = NOW()
    WHERE current_period_end <= NOW()
    AND status = 'active';
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- 第四階段: 創建管理員相關表
-- ================================================

-- 管理員表
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- admin, moderator, support
    permissions JSONB, -- 存儲權限列表
    
    created_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP,
    revoked_by INTEGER REFERENCES admin_users(id)
);

-- 管理員操作日誌
CREATE TABLE admin_logs (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50), -- user, plan, payment, system
    target_id INTEGER,
    description TEXT,
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================
-- 資料遷移腳本
-- ================================================

-- 創建默認免費計劃
INSERT INTO user_plans (user_id, plan_name, monthly_api_calls, current_period_calls, current_period_start, current_period_end, status)
SELECT id, 'free', 3, 0, NOW(), NOW() + INTERVAL '1 month', 'active'
FROM users 
WHERE id NOT IN (SELECT user_id FROM user_plans WHERE status = 'active');

-- 清理過期會話
DELETE FROM user_sessions WHERE expires_at < NOW();

-- 創建必要的觸發器
-- 更新 updated_at 字段的觸發器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為需要的表創建觸發器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_plans_updated_at BEFORE UPDATE ON user_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- 性能優化建議
-- ================================================

-- 1. 定期清理舊數據的計劃任務
-- 建議使用 pg_cron 或外部調度器定期執行：
-- DELETE FROM api_usage WHERE request_time < NOW() - INTERVAL '6 months';

-- 2. 分析查詢性能
-- ANALYZE users;
-- ANALYZE api_usage;
-- ANALYZE user_plans;

-- 3. 創建部分索引以節省空間
-- CREATE INDEX CONCURRENTLY idx_api_usage_errors ON api_usage(user_id, request_time) WHERE status_code >= 400;

-- ================================================
-- 安全措施
-- ================================================

-- 1. 創建只讀用戶用於報表
-- CREATE USER readonly_user WITH PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE trading_db TO readonly_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- 2. 設置行級安全策略（RLS）
-- ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY api_usage_user_policy ON api_usage FOR ALL TO application_user USING (user_id = current_setting('app.user_id')::INTEGER);