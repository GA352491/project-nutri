from fastapi import FastAPI
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    service: str

def add_health_endpoints(app: FastAPI, service_name: str = "nutriplan_service"):
    """
    Adds /health and /ready endpoints to the FastAPI application.
    """
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        return HealthResponse(status="ok", service=service_name)
    
    @app.get("/ready", response_model=HealthResponse, tags=["Health"])
    async def readiness_check():
        return HealthResponse(status="ready", service=service_name)
