from fastapi import FastAPI
import sys
import os

# Add shared module to path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints

from .routes import rooms

app = FastAPI(title="NutriPlan — Video Service", docs_url="/api/docs")

add_standard_middleware(app)
add_health_endpoints(app)

app.include_router(rooms.router, prefix="/api/v1/video", tags=["Video"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("video_service.main:app", host="0.0.0.0", port=8014, reload=True)
