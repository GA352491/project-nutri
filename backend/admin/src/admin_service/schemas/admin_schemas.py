from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class DashboardStats(BaseModel):
    total_users: int
    active_subscriptions: int
    recipes_curated: int
    daily_active_users: int

class SystemHealth(BaseModel):
    service_name: str
    status: str
    latency_ms: int

class AdminDashboardResponse(BaseModel):
    stats: DashboardStats
    system_health: List[SystemHealth]

# ── Audit Logs ─────────────────────────────────────────────────────────────
class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    actor_id: str
    actor_email: str
    actor_role: str
    action: str  # READ, WRITE, DELETE, EXPORT, VERIFY, BROADCAST
    resource_type: str  # USER, RECIPE, NUTRITIONIST, MEAL_PLAN, SYSTEM
    resource_id: Optional[str] = None
    status: str  # SUCCESS, FAILED, DENIED
    ip_address: Optional[str] = "127.0.0.1"
    details: Optional[str] = None

class CreateAuditLogRequest(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    actor_email: Optional[str] = "admin@nutriplan.local"
    actor_role: Optional[str] = "admin"
    status: str = "SUCCESS"
    details: Optional[str] = None

# ── Feature Flags & Remote Config ──────────────────────────────────────────
class FeatureFlag(BaseModel):
    key: str
    name: str
    description: str
    enabled: bool
    category: str  # ai, checkout, regional, media
    rollout_pct: int = 100
    updated_at: str

class UpdateFeatureFlagRequest(BaseModel):
    enabled: Optional[bool] = None
    rollout_pct: Optional[int] = None

# ── Broadcast Announcement ────────────────────────────────────────────────
class BroadcastNotificationRequest(BaseModel):
    title: str
    message: str
    audience: str  # all, patients, nutritionists, premium
    channel: str  # in_app, email, all
    severity: str = "info"  # info, warning, success, urgent
    action_url: Optional[str] = None

class BroadcastNotificationResponse(BaseModel):
    broadcast_id: str
    timestamp: str
    target_count: int
    status: str
    summary: str

# ── LLM Dynamic Routing & Cost Center ──────────────────────────────────────
class LLMModelOption(BaseModel):
    id: str
    name: str
    provider: str  # local_ollama, openai, anthropic, google, deepseek
    cost_per_1k_input_usd: float
    cost_per_1k_output_usd: float
    is_local: bool = False
    context_window: int
    supports_vision: bool = False

class ServiceLLMConfig(BaseModel):
    service_key: str  # meal_planner, food_vision, clinical_soap, patient_chatbot, compliance_guard
    service_name: str
    description: str
    selected_model_id: str
    fallback_model_id: str
    temperature: float = 0.2
    max_tokens: int = 1024
    user_rate_limit_per_hour: int = 20  # requests per user / hr
    monthly_budget_usd: float = 150.0
    current_burn_usd: float = 0.0
    total_tokens_consumed: int = 0
    total_requests: int = 0

class UpdateServiceLLMConfigRequest(BaseModel):
    selected_model_id: Optional[str] = None
    fallback_model_id: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    user_rate_limit_per_hour: Optional[int] = None
    monthly_budget_usd: Optional[float] = None

class UserBurnMetric(BaseModel):
    user_id: str
    user_email: str
    user_role: str
    plan: str
    requests_today: int
    rate_limit_hourly: int
    tokens_consumed: int
    total_cost_burned_usd: float
    last_active: str
    status: str  # OK, THROTTLED, EXCEEDED

class CostCenterOverview(BaseModel):
    total_burned_usd: float
    monthly_budget_total_usd: float
    local_inference_savings_usd: float
    total_tokens_processed: int
    cloud_vs_local_ratio: str
    services: List[ServiceLLMConfig]
    available_models: List[LLMModelOption]
    top_user_burners: List[UserBurnMetric]
