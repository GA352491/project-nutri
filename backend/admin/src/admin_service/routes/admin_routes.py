from fastapi import APIRouter, Query
from typing import Optional, List
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
    update_service_llm_config
)
from ..schemas.admin_schemas import (
    CostCenterOverview,
    ServiceLLMConfig,
    UpdateServiceLLMConfigRequest
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

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
