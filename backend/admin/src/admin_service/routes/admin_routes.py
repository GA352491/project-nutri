from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel
from ..schemas.admin_schemas import (
    AdminDashboardResponse,
    AuditLogEntry,
    CreateAuditLogRequest,
    FeatureFlag,
    UpdateFeatureFlagRequest,
    BroadcastNotificationRequest,
    BroadcastNotificationResponse
)
from ..services.admin_service import (
    get_dashboard_data,
    get_analytics_data,
    get_audit_logs,
    create_audit_log,
    get_feature_flags,
    update_feature_flag,
    dispatch_global_broadcast,
    get_broadcast_history,
    get_cost_center_overview,
    update_service_llm_config,
    set_user_ai_plan_override,
    trigger_user_ai_plan,
    check_ai_auto_plan_enabled,
    execute_devops_pipeline,
)
from ..schemas.admin_schemas import (
    CostCenterOverview,
    ServiceLLMConfig,
    UpdateServiceLLMConfigRequest
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

@router.post("/devops/trigger-pipeline")
async def trigger_pipeline():
    """Trigger the real automated 5-stage CI/CD and smoke gate pipeline."""
    return await execute_devops_pipeline()

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def dashboard():
    return await get_dashboard_data()

@router.get("/analytics")
async def analytics():
    return await get_analytics_data()

# ── LLM Dynamic Routing & Cost Center ──────────────────────────────────────
@router.get("/cost-center", response_model=CostCenterOverview)
async def get_cost_center():
    return await get_cost_center_overview()

@router.patch("/cost-center/service/{service_key}", response_model=ServiceLLMConfig)
async def update_service_llm(service_key: str, req: UpdateServiceLLMConfigRequest):
    return await update_service_llm_config(service_key, req)

# ── Audit Logs ─────────────────────────────────────────────────────────────
@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    resource_type: Optional[str] = None
):
    return await get_audit_logs(limit=limit, action=action, resource_type=resource_type)

@router.post("/audit-logs", response_model=AuditLogEntry)
async def log_audit_event(req: CreateAuditLogRequest):
    return await create_audit_log(req)

# ── Feature Flags & Remote Config ──────────────────────────────────────────
@router.get("/feature-flags", response_model=List[FeatureFlag])
async def list_feature_flags():
    return await get_feature_flags()

@router.patch("/feature-flags/{key}", response_model=FeatureFlag)
async def modify_feature_flag(key: str, req: UpdateFeatureFlagRequest):
    return await update_feature_flag(key, req)

# ── Broadcast Announcement ────────────────────────────────────────────────
@router.get("/broadcast")
async def get_broadcasts(limit: int = Query(50, ge=1, le=200)):
    return await get_broadcast_history(limit=limit)


@router.post("/broadcast", response_model=BroadcastNotificationResponse)
async def send_broadcast(req: BroadcastNotificationRequest):
    return await dispatch_global_broadcast(req)


# ── AI Meal Plan Auto-Assign Controls ────────────────────────────────────

class UserAIPlanOverrideRequest(BaseModel):
    enabled: bool

class TriggerAIPlanRequest(BaseModel):
    caloric_target: int = 1800
    region: str = "in_south_andhra"
    dietary_flag: str = "vegetarian"

@router.get("/ai-plan/status")
async def get_global_ai_plan_status():
    """Get current global AI auto-assign status."""
    return {
        "global_enabled": check_ai_auto_plan_enabled(),
        "feature_flag": "ff_ai_auto_plan_on_register",
        "description": "When enabled, AI generates and assigns a 7-day meal plan for every new user after onboarding."
    }

@router.patch("/users/{user_id}/ai-plan-override")
async def set_ai_plan_override(user_id: str, req: UserAIPlanOverrideRequest):
    """
    Set per-user AI meal plan auto-assign override.
    Overrides the global app-level flag for this specific user.
    """
    return await set_user_ai_plan_override(user_id, req.enabled)

@router.post("/users/{user_id}/generate-plan")
async def admin_generate_plan(user_id: str, req: TriggerAIPlanRequest):
    """
    Admin manually triggers AI meal plan generation for a specific user.
    Works regardless of the global auto-assign flag state.
    """
    return await trigger_user_ai_plan(
        user_id=user_id,
        caloric_target=req.caloric_target,
        region=req.region,
        dietary_flag=req.dietary_flag
    )
