"""
Food Recognition Service — Main Entry Point
Uses a local Ollama vision model (llava) to recognize food items from images
and returns full nutritional data by matching against our recipe/food database.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import recognize

app = FastAPI(
    title="NutriPlan Food Recognition Service",
    description="AI-powered food image recognition → nutritional data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recognize.router, prefix="/api/v1/food-recognition", tags=["Food Recognition"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "food-recognition"}
