from fastapi import FastAPI
import sys
import os

# Add shared module to path for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared/src")))
from nutriplan_shared.fastapi import add_standard_middleware, add_health_endpoints

from .routes import chat

app = FastAPI(title="NutriPlan — AI Chatbot Service", docs_url="/api/docs")

add_standard_middleware(app)
add_health_endpoints(app)

app.include_router(chat.router, prefix="/api/v1/ai-chat", tags=["AI Chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chatbot_service.main:app", host="0.0.0.0", port=8012, reload=True)
