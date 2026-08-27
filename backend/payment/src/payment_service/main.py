from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import os

# Add shared module to path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints

from .routes import stripe
from .routes import payments
from .services.payment_store import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("✅ Payment Service started — ledger tables ready. Swagger: http://localhost:8016/api/docs")
    except Exception as e:
        print(f"Payment Service database note (Postgres offline: {e})")
    yield


app = FastAPI(title="NutriPlan — Payment Service", docs_url="/api/docs", lifespan=lifespan)

add_standard_middleware(app)
add_health_endpoints(app)

app.include_router(stripe.router, prefix="/api/v1/payment/stripe", tags=["Stripe Payments"])
app.include_router(payments.router, prefix="/api/v1/payment", tags=["Payment Ledger"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("payment_service.main:app", host="0.0.0.0", port=8016, reload=True)
