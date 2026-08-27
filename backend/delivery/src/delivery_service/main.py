from fastapi import FastAPI
import sys
import os

# Add shared module to path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints

from .routes import partners

app = FastAPI(title="NutriPlan — Delivery Service", docs_url="/api/docs")

add_standard_middleware(app)
add_health_endpoints(app)

app.include_router(partners.router, prefix="/api/v1/delivery", tags=["Delivery Partners"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("delivery_service.main:app", host="0.0.0.0", port=8017, reload=True)
