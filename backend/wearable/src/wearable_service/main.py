from fastapi import FastAPI
import sys
import os

# Add shared module to path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints

from .routes import ingest

app = FastAPI(title="NutriPlan — Wearable Service", docs_url="/api/docs")

add_standard_middleware(app)
add_health_endpoints(app)

app.include_router(ingest.router, prefix="/api/v1/wearable", tags=["Wearable Ingestion"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("wearable_service.main:app", host="0.0.0.0", port=8018, reload=True)
