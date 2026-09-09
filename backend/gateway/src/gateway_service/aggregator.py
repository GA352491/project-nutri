import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

from nutriplan_shared.service_registry import SERVICES_CATALOGUE

# Build services dynamically from centralized service_registry
SERVICES = [
    {
        "name": s["name"],
        "key": s["key"],
        "url": s["url"],
        "docs": f"{s['url']}/docs",
        "prefix": s["prefix"],
    }
    for s in SERVICES_CATALOGUE
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
