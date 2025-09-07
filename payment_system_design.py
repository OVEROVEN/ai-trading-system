"""
支付系統設計與Stripe整合
========================

完整的訂閱管理、支付處理、發票生成系統

作者: Claude Code AI Assistant
日期: 2024
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass

import stripe
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

# ================================
# 支付相關枚舉和模型
# ================================

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled" 
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIALING = "trialing"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class PlanConfig:
    """訂閱方案配置"""
    name: str
    display_name: str
    description: str
    monthly_price_usd: Decimal
    yearly_price_usd: Decimal
    monthly_api_calls: int
    features: List[str]
    stripe_monthly_price_id: str
    stripe_yearly_price_id: str
    is_popular: bool = False

# 訂閱方案配置
SUBSCRIPTION_PLANS = {
    "free": PlanConfig(
        name="free",
        display_name="免費方案", 
        description="適合初次體驗用戶",
        monthly_price_usd=Decimal("0"),
        yearly_price_usd=Decimal("0"),
        monthly_api_calls=3,
        features=[
            "3次AI分析",
            "基礎技術指標", 
            "基礎圖表功能",
            "社區支持"
        ],
        stripe_monthly_price_id="",
        stripe_yearly_price_id="",
    ),
    "basic": PlanConfig(
        name="basic",
        display_name="基礎方案",
        description="適合個人投資者",
        monthly_price_usd=Decimal("9.99"),
        yearly_price_usd=Decimal("99.99"),  # 8.5折
        monthly_api_calls=100,
        features=[
            "100次AI分析/月",
            "所有技術指標",
            "高級圖表功能", 
            "數據導出",
            "50次回測/月",
            "郵件支持"
        ],
        stripe_monthly_price_id="price_basic_monthly",
        stripe_yearly_price_id="price_basic_yearly",
        is_popular=True
    ),
    "premium": PlanConfig(
        name="premium", 
        display_name="高級方案",
        description="適合專業交易者",
        monthly_price_usd=Decimal("29.99"),
        yearly_price_usd=Decimal("299.99"),
        monthly_api_calls=500,
        features=[
            "500次AI分析/月",
            "高級AI模型(GPT-4)",
            "實時數據推送",
            "自定義策略",
            "200次回測/月", 
            "優先客服",
            "API接入"
        ],
        stripe_monthly_price_id="price_premium_monthly", 
        stripe_yearly_price_id="price_premium_yearly"
    ),
    "enterprise": PlanConfig(
        name="enterprise",
        display_name="企業方案", 
        description="適合機構用戶",
        monthly_price_usd=Decimal("99.99"),
        yearly_price_usd=Decimal("999.99"),
        monthly_api_calls=2000,
        features=[
            "2000次AI分析/月",
            "所有AI模型", 
            "無限回測",
            "自定義API key",
            "白標部署",
            "專屬客服",
            "SLA保障"
        ],
        stripe_monthly_price_id="price_enterprise_monthly",
        stripe_yearly_price_id="price_enterprise_yearly"
    )
}

# ================================
# 支付請求模型
# ================================

class CreateSubscriptionRequest(BaseModel):
    """創建訂閱請求"""
    plan_name: str
    billing_cycle: BillingCycle
    payment_method_id: Optional[str] = None
    coupon_code: Optional[str] = None

class UpdateSubscriptionRequest(BaseModel):
    """更新訂閱請求"""
    new_plan_name: str
    billing_cycle: BillingCycle

class CreatePaymentIntentRequest(BaseModel):
    """創建支付意圖請求"""
    plan_name: str
    billing_cycle: BillingCycle
    currency: str = "usd"

class ApplyCouponRequest(BaseModel):
    """應用優惠券請求"""
    coupon_code: str

# ================================
# Stripe支付管理器
# ================================

class StripePaymentManager:
    """Stripe支付管理器"""
    
    def __init__(self, stripe_secret_key: str, db: Session):
        stripe.api_key = stripe_secret_key
        self.db = db
        
    async def create_customer(
        self,
        user_id: int,
        email: str,
        name: Optional[str] = None
    ) -> str:
        """創建Stripe客戶"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": str(user_id)}
            )
            
            # 更新用戶記錄
            from src.database.models import UserPlan
            user_plan = self.db.query(UserPlan).filter(
                UserPlan.user_id == user_id
            ).first()
            
            if user_plan:
                user_plan.stripe_customer_id = customer.id
                self.db.commit()
            
            return customer.id
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_subscription(
        self,
        user_id: int,
        request: CreateSubscriptionRequest
    ) -> Dict[str, Any]:
        """創建訂閱"""
        try:
            # 獲取用戶和計劃配置
            user = await self._get_user(user_id)
            plan_config = SUBSCRIPTION_PLANS.get(request.plan_name)
            
            if not plan_config:
                raise HTTPException(status_code=400, detail="無效的訂閱方案")
            
            # 獲取或創建Stripe客戶
            customer_id = await self._get_or_create_customer(user)
            
            # 選擇價格ID
            price_id = (
                plan_config.stripe_monthly_price_id 
                if request.billing_cycle == BillingCycle.MONTHLY
                else plan_config.stripe_yearly_price_id
            )
            
            # 創建訂閱參數
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
                "metadata": {
                    "user_id": str(user_id),
                    "plan_name": request.plan_name
                }
            }
            
            # 應用優惠券
            if request.coupon_code:
                coupon = await self._validate_coupon(request.coupon_code)
                if coupon:
                    subscription_params["coupon"] = request.coupon_code
            
            # 創建訂閱
            subscription = stripe.Subscription.create(**subscription_params)
            
            # 更新數據庫
            await self._update_user_plan(
                user_id, 
                plan_config,
                request.billing_cycle,
                subscription
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def cancel_subscription(
        self, 
        user_id: int,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """取消訂閱"""
        try:
            # 獲取用戶訂閱
            user_plan = await self._get_user_plan(user_id)
            if not user_plan or not user_plan.stripe_subscription_id:
                raise HTTPException(status_code=404, detail="未找到活躍訂閱")
            
            if immediate:
                # 立即取消
                subscription = stripe.Subscription.cancel(
                    user_plan.stripe_subscription_id
                )
                user_plan.status = SubscriptionStatus.CANCELLED
                user_plan.cancelled_at = datetime.now()
                
            else:
                # 週期結束時取消
                subscription = stripe.Subscription.modify(
                    user_plan.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                user_plan.status = SubscriptionStatus.ACTIVE  # 仍然活躍直到週期結束
            
            self.db.commit()
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "current_period_end": subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def change_plan(
        self,
        user_id: int, 
        request: UpdateSubscriptionRequest
    ) -> Dict[str, Any]:
        """更改訂閱方案"""
        try:
            # 獲取當前訂閱
            user_plan = await self._get_user_plan(user_id)
            if not user_plan or not user_plan.stripe_subscription_id:
                raise HTTPException(status_code=404, detail="未找到活躍訂閱")
            
            new_plan_config = SUBSCRIPTION_PLANS.get(request.new_plan_name)
            if not new_plan_config:
                raise HTTPException(status_code=400, detail="無效的訂閱方案")
            
            # 獲取當前訂閱
            subscription = stripe.Subscription.retrieve(
                user_plan.stripe_subscription_id
            )
            
            # 選擇新價格ID
            new_price_id = (
                new_plan_config.stripe_monthly_price_id
                if request.billing_cycle == BillingCycle.MONTHLY
                else new_plan_config.stripe_yearly_price_id
            )
            
            # 更新訂閱
            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id
                }],
                proration_behavior="create_prorations"  # 按比例計費
            )
            
            # 更新數據庫
            await self._update_user_plan(
                user_id,
                new_plan_config, 
                request.billing_cycle,
                updated_subscription
            )
            
            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status,
                "new_plan": request.new_plan_name
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_billing_history(
        self, 
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """獲取帳單歷史"""
        try:
            user_plan = await self._get_user_plan(user_id)
            if not user_plan or not user_plan.stripe_customer_id:
                return []
            
            # 獲取發票
            invoices = stripe.Invoice.list(
                customer=user_plan.stripe_customer_id,
                limit=limit
            )
            
            billing_history = []
            for invoice in invoices.data:
                billing_history.append({
                    "id": invoice.id,
                    "amount": invoice.amount_paid / 100,  # 轉換為美元
                    "currency": invoice.currency.upper(),
                    "status": invoice.status,
                    "date": datetime.fromtimestamp(invoice.created),
                    "invoice_url": invoice.hosted_invoice_url,
                    "pdf_url": invoice.invoice_pdf,
                    "description": invoice.lines.data[0].description if invoice.lines.data else ""
                })
            
            return billing_history
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_customer_portal_session(
        self,
        user_id: int,
        return_url: str
    ) -> str:
        """創建客戶門戶會話"""
        try:
            user_plan = await self._get_user_plan(user_id)
            if not user_plan or not user_plan.stripe_customer_id:
                raise HTTPException(status_code=404, detail="未找到客戶記錄")
            
            session = stripe.billing_portal.Session.create(
                customer=user_plan.stripe_customer_id,
                return_url=return_url
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # ================================
    # 內部輔助方法
    # ================================
    
    async def _get_user(self, user_id: int):
        """獲取用戶"""
        from src.database.models import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        return user
    
    async def _get_user_plan(self, user_id: int):
        """獲取用戶方案"""
        from src.database.models import UserPlan
        return self.db.query(UserPlan).filter(
            UserPlan.user_id == user_id
        ).first()
    
    async def _get_or_create_customer(self, user) -> str:
        """獲取或創建Stripe客戶"""
        user_plan = await self._get_user_plan(user.id)
        
        if user_plan and user_plan.stripe_customer_id:
            return user_plan.stripe_customer_id
        else:
            return await self.create_customer(
                user.id,
                user.email,
                user.full_name
            )
    
    async def _validate_coupon(self, coupon_code: str) -> Optional[Any]:
        """驗證優惠券"""
        try:
            coupon = stripe.Coupon.retrieve(coupon_code)
            return coupon if coupon.valid else None
        except stripe.error.StripeError:
            return None
    
    async def _update_user_plan(
        self,
        user_id: int,
        plan_config: PlanConfig,
        billing_cycle: BillingCycle,
        subscription
    ):
        """更新用戶方案"""
        from src.database.models import UserPlan
        
        user_plan = self.db.query(UserPlan).filter(
            UserPlan.user_id == user_id
        ).first()
        
        if not user_plan:
            user_plan = UserPlan(user_id=user_id)
            self.db.add(user_plan)
        
        # 更新方案信息
        user_plan.plan_name = plan_config.name
        user_plan.billing_cycle = billing_cycle.value
        user_plan.monthly_api_calls = plan_config.monthly_api_calls
        user_plan.current_period_calls = 0
        user_plan.status = SubscriptionStatus.ACTIVE.value
        user_plan.stripe_subscription_id = subscription.id
        
        # 設置週期時間
        user_plan.current_period_start = datetime.fromtimestamp(
            subscription.current_period_start
        )
        user_plan.current_period_end = datetime.fromtimestamp(
            subscription.current_period_end
        )
        
        # 設置價格
        price = (
            plan_config.monthly_price_usd
            if billing_cycle == BillingCycle.MONTHLY
            else plan_config.yearly_price_usd
        )
        user_plan.plan_price = float(price)
        
        self.db.commit()

# ================================
# Webhook處理器
# ================================

class StripeWebhookHandler:
    """Stripe Webhook處理器"""
    
    def __init__(self, webhook_secret: str, db: Session):
        self.webhook_secret = webhook_secret
        self.db = db
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """處理Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 處理不同類型的事件
        if event["type"] == "invoice.payment_succeeded":
            await self._handle_payment_succeeded(event["data"]["object"])
        elif event["type"] == "invoice.payment_failed": 
            await self._handle_payment_failed(event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            await self._handle_subscription_deleted(event["data"]["object"])
        elif event["type"] == "customer.subscription.updated":
            await self._handle_subscription_updated(event["data"]["object"])
        
        return {"status": "success"}
    
    async def _handle_payment_succeeded(self, invoice):
        """處理支付成功"""
        subscription_id = invoice.get("subscription")
        if not subscription_id:
            return
        
        # 更新用戶方案狀態
        from src.database.models import UserPlan, PaymentHistory
        
        user_plan = self.db.query(UserPlan).filter(
            UserPlan.stripe_subscription_id == subscription_id
        ).first()
        
        if user_plan:
            user_plan.status = SubscriptionStatus.ACTIVE.value
            user_plan.current_period_calls = 0  # 重置使用量
            
            # 記錄支付歷史
            payment_record = PaymentHistory(
                user_id=user_plan.user_id,
                payment_intent_id=invoice.get("payment_intent"),
                invoice_id=invoice.get("id"),
                amount_cents=invoice.get("amount_paid"),
                currency=invoice.get("currency", "usd"),
                status=PaymentStatus.SUCCEEDED.value,
                plan_name=user_plan.plan_name,
                billing_period_start=datetime.fromtimestamp(
                    invoice.get("period_start", 0)
                ),
                billing_period_end=datetime.fromtimestamp(
                    invoice.get("period_end", 0)
                ),
                receipt_url=invoice.get("hosted_invoice_url"),
                invoice_url=invoice.get("invoice_pdf")
            )
            
            self.db.add(payment_record)
            self.db.commit()
    
    async def _handle_payment_failed(self, invoice):
        """處理支付失敗"""
        # 實現支付失敗邏輯
        pass
    
    async def _handle_subscription_deleted(self, subscription):
        """處理訂閱刪除"""
        from src.database.models import UserPlan
        
        user_plan = self.db.query(UserPlan).filter(
            UserPlan.stripe_subscription_id == subscription["id"]
        ).first()
        
        if user_plan:
            user_plan.status = SubscriptionStatus.CANCELLED.value
            user_plan.cancelled_at = datetime.now()
            self.db.commit()
    
    async def _handle_subscription_updated(self, subscription):
        """處理訂閱更新"""
        # 實現訂閱更新邏輯
        pass

# ================================
# FastAPI端點
# ================================

app = FastAPI()

@app.get("/api/billing/plans")
async def get_subscription_plans():
    """獲取所有訂閱方案"""
    plans = []
    for plan_name, config in SUBSCRIPTION_PLANS.items():
        if plan_name == "free":
            continue
            
        plans.append({
            "name": config.name,
            "display_name": config.display_name,
            "description": config.description,
            "monthly_price": float(config.monthly_price_usd),
            "yearly_price": float(config.yearly_price_usd),
            "monthly_api_calls": config.monthly_api_calls,
            "features": config.features,
            "is_popular": config.is_popular,
            "yearly_discount": round(
                (1 - (config.yearly_price_usd / (config.monthly_price_usd * 12))) * 100
            )
        })
    
    return {"plans": plans}

@app.post("/api/billing/subscribe")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user = Depends(),  # 從JWT獲取
    payment_manager: StripePaymentManager = Depends()
):
    """創建訂閱"""
    result = await payment_manager.create_subscription(
        current_user["id"],
        request
    )
    return result

@app.post("/api/billing/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user = Depends(),
    payment_manager: StripePaymentManager = Depends()
):
    """取消訂閱"""
    result = await payment_manager.cancel_subscription(
        current_user["id"],
        immediate
    )
    return result

@app.get("/api/billing/history")
async def get_billing_history(
    limit: int = 20,
    current_user = Depends(),
    payment_manager: StripePaymentManager = Depends()
):
    """獲取帳單歷史"""
    history = await payment_manager.get_billing_history(
        current_user["id"],
        limit
    )
    return {"history": history}

@app.post("/api/billing/portal")
async def create_billing_portal(
    return_url: str,
    current_user = Depends(),
    payment_manager: StripePaymentManager = Depends()
):
    """創建計費門戶"""
    portal_url = await payment_manager.create_customer_portal_session(
        current_user["id"],
        return_url
    )
    return {"url": portal_url}

@app.post("/api/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    webhook_handler: StripeWebhookHandler = Depends()
):
    """Stripe webhook端點"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    result = await webhook_handler.handle_webhook(payload, signature)
    return result

# ================================
# 部署配置和監控
# ================================

"""
Stripe配置檢查清單：

□ 創建Stripe帳戶並完成KYC
□ 獲取API密鑰（測試和生產環境）
□ 創建產品和價格
□ 配置webhook端點
□ 設置客戶門戶
□ 配置稅率（如需要）
□ 設置優惠券
□ 測試支付流程
□ 監控支付失敗
□ 設置退款流程

安全注意事項：
- 始終在服務器端驗證支付
- 使用webhook確保支付狀態同步
- 保護API密鑰安全
- 實施重複支付保護
- 監控異常交易
"""