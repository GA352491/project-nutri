import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Register all 11 NutriPlan microservices
SERVICES = [
    {"name": "Auth Service", "key": "auth", "url": "http://localhost:8001", "docs": "http://localhost:8001/docs", "prefix": "/api/v1/auth"},
    {"name": "Profile & Onboarding Service", "key": "profile", "url": "http://localhost:8003", "docs": "http://localhost:8003/docs", "prefix": "/api/v1/profile"},
    {"name": "Recipe & Food DB Service", "key": "recipe", "url": "http://localhost:8004", "docs": "http://localhost:8004/docs", "prefix": "/api/v1/recipes"},
    {"name": "Food Diary Service", "key": "diary", "url": "http://localhost:8005", "docs": "http://localhost:8005/docs", "prefix": "/api/v1/diary"},
    {"name": "Grocery List Service", "key": "grocery", "url": "http://localhost:8006", "docs": "http://localhost:8006/docs", "prefix": "/api/v1/grocery"},
    {"name": "Meal Plan Engine Service", "key": "meal_plan", "url": "http://localhost:8009", "docs": "http://localhost:8009/docs", "prefix": "/api/v1/plan"},
    {"name": "Notifications Service", "key": "notifications", "url": "http://localhost:8010", "docs": "http://localhost:8010/docs", "prefix": "/api/v1/notifications"},
    {"name": "AI Chatbot Service", "key": "chat", "url": "http://localhost:8012", "docs": "http://localhost:8012/docs", "prefix": "/api/v1/chat"},
    {"name": "Appointments Service", "key": "appointment", "url": "http://localhost:8013", "docs": "http://localhost:8013/docs", "prefix": "/api/v1/appointments"},
    {"name": "Video Consultation Service", "key": "video", "url": "http://localhost:8014", "docs": "http://localhost:8014/docs", "prefix": "/api/v1/video"},
    {"name": "Payment Service", "key": "payment", "url": "http://localhost:8016", "docs": "http://localhost:8016/docs", "prefix": "/api/v1/payment"},
    {"name": "Delivery Service", "key": "delivery", "url": "http://localhost:8017", "docs": "http://localhost:8017/docs", "prefix": "/api/v1/delivery"},
    {"name": "Wearable Service", "key": "wearable", "url": "http://localhost:8018", "docs": "http://localhost:8018/docs", "prefix": "/api/v1/wearable"},
    {"name": "Marketplace Service", "key": "marketplace", "url": "http://localhost:8025", "docs": "http://localhost:8025/docs", "prefix": "/api/v1/marketplace"},
    {"name": "Compliance Service", "key": "compliance", "url": "http://localhost:8002", "docs": "http://localhost:8002/docs", "prefix": "/api/v1/compliance"},
    {"name": "Subscriptions Service", "key": "subscriptions", "url": "http://localhost:8007", "docs": "http://localhost:8007/docs", "prefix": "/api/v1/subscriptions"},
]

async def fetch_service_health() -> List[Dict[str, Any]]:
    """Poll health endpoints of all microservices."""
    results = []
    async with httpx.AsyncClient(timeout=0.6) as client:
        for svc in SERVICES:
            status = "offline"
            try:
                resp = await client.get(f"{svc['url']}/health")
                if resp.status_code == 200:
                    status = "online"
            except Exception:
                status = "offline"
            results.append({
                "name": svc["name"],
                "key": svc["key"],
                "url": svc["url"],
                "docs": svc["docs"],
                "status": status,
                "prefix": svc["prefix"]
            })
    return results

async def aggregate_openapi_specs() -> Dict[str, Any]:
    """Fetch and merge openapi.json from all operational microservices."""
    merged_spec: Dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {
            "title": "NutriPlan Unified Microservices API Gateway",
            "version": "1.0.0",
            "description": "Unified interactive OpenAPI gateway portal consolidating all backend microservices for NutriPlan.",
            "contact": {"name": "NutriPlan Engineering", "email": "dev@nutriplan.local"}
        },
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "tags": []
    }

    async with httpx.AsyncClient(timeout=0.8) as client:
        for svc in SERVICES:
            try:
                resp = await client.get(f"{svc['url']}/openapi.json")
                if resp.status_code == 200:
                    spec = resp.json()
                    svc_tag = svc["name"]
                    merged_spec["tags"].append({
                        "name": svc_tag,
                        "description": f"Endpoints served by {svc['name']} ({svc['url']})"
                    })

                    # Merge paths
                    for path, methods in spec.get("paths", {}).items():
                        for method, details in methods.items():
                            if isinstance(details, dict):
                                details["tags"] = [svc_tag]
                        merged_spec["paths"][path] = methods

                    # Merge schemas
                    schemas = spec.get("components", {}).get("schemas", {})
                    for schema_name, schema_def in schemas.items():
                        merged_spec["components"]["schemas"][f"{svc['key']}_{schema_name}"] = schema_def
            except Exception as e:
                logger.warning(f"Could not load openapi spec from {svc['name']}: {e}")

    return merged_spec
