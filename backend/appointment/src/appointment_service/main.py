from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints

from .config import settings
from .routes import booking
from .services.appointment_store import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("✅ Appointment Service started — Swagger: http://localhost:8013/api/docs")
    except Exception as e:
        print(f"Appointment Service database note: {e}")
    yield


app = FastAPI(title="NutriPlan — Appointment Service", docs_url="/api/docs", lifespan=lifespan)

add_standard_middleware(app, settings)
add_health_endpoints(app)

app.include_router(booking.router, prefix="/api/v1/appointments", tags=["Appointments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("appointment_service.main:app", host="0.0.0.0", port=8013, reload=True)
