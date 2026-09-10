"""
NutriPlan Service Registry
==========================
Single source of truth for ALL inter-service URLs in the backend.

How it works
------------
APP_DOMAIN and APP_SCHEME are read from the root .env file (or environment).
Each service's full URL is assembled as:

    {APP_SCHEME}://{APP_DOMAIN}:{APP_PORT_*}

To change from local development to staging or production, update ONLY
APP_DOMAIN and APP_SCHEME in .env — no source code changes required.

Usage
-----
    from nutriplan_shared.service_registry import AUTH_URL, MEAL_PLAN_URL, SERVICES_HEALTH_MAP

    # In an httpx call:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{AUTH_URL}/api/v1/auth/users")

    # Health probe loop:
    for name, health_url in SERVICES_HEALTH_MAP:
        resp = await client.get(health_url)
"""

import os
from typing import List, Tuple, Dict

# ── Read domain configuration from environment ─────────────────────────────────
_DOMAIN: str = os.getenv("APP_DOMAIN", "localhost")
_SCHEME: str = os.getenv("APP_SCHEME", "http")


def svc_url(port: int | str) -> str:
    """Assemble a service base URL from the environment-configured domain."""
    return f"{_SCHEME}://{_DOMAIN}:{port}"


# ── Service ports (read from env, fall back to canonical local dev ports) ──────
_PORT_AUTH             = int(os.getenv("APP_PORT_AUTH",             "8001"))
_PORT_COMPLIANCE       = int(os.getenv("APP_PORT_COMPLIANCE",       "8002"))
_PORT_PROFILE          = int(os.getenv("APP_PORT_PROFILE",          "8003"))
_PORT_RECIPE           = int(os.getenv("APP_PORT_RECIPE",           "8004"))
_PORT_DIARY            = int(os.getenv("APP_PORT_DIARY",            "8005"))
_PORT_GROCERY          = int(os.getenv("APP_PORT_GROCERY",          "8006"))
_PORT_SUBSCRIPTION     = int(os.getenv("APP_PORT_SUBSCRIPTION",     "8007"))
_PORT_MEAL_PLAN        = int(os.getenv("APP_PORT_MEAL_PLAN",        "8009"))
_PORT_NOTIFICATION     = int(os.getenv("APP_PORT_NOTIFICATION",     "8010"))
_PORT_FOOD_RECOGNITION = int(os.getenv("APP_PORT_FOOD_RECOGNITION", "8011"))
_PORT_CHAT             = int(os.getenv("APP_PORT_CHAT",             "8012"))
_PORT_APPOINTMENT      = int(os.getenv("APP_PORT_APPOINTMENT",      "8013"))
_PORT_VIDEO            = int(os.getenv("APP_PORT_VIDEO",            "8014"))
_PORT_AI_CHAT          = int(os.getenv("APP_PORT_AI_CHAT",          "8015"))
_PORT_PAYMENT          = int(os.getenv("APP_PORT_PAYMENT",          "8016"))
_PORT_DELIVERY         = int(os.getenv("APP_PORT_DELIVERY",         "8017"))
_PORT_WEARABLE         = int(os.getenv("APP_PORT_WEARABLE",         "8018"))
_PORT_ADMIN            = int(os.getenv("APP_PORT_ADMIN",            "8019"))
_PORT_FOOD_VISION      = int(os.getenv("APP_PORT_FOOD_VISION",      "8020"))
_PORT_MARKETPLACE      = int(os.getenv("APP_PORT_MARKETPLACE",      "8025"))
_PORT_GATEWAY          = int(os.getenv("APP_PORT_GATEWAY",          "8000"))
_PORT_TEMPORAL_UI      = int(os.getenv("APP_PORT_TEMPORAL_UI",      "8233"))
_PORT_OLLAMA           = int(os.getenv("APP_PORT_OLLAMA",           "11434"))

# ── Named service URL constants ────────────────────────────────────────────────
# Use these throughout the entire backend — never write http://localhost:XXXX
AUTH_URL             = svc_url(_PORT_AUTH)
COMPLIANCE_URL       = svc_url(_PORT_COMPLIANCE)
PROFILE_URL          = svc_url(_PORT_PROFILE)
RECIPE_URL           = svc_url(_PORT_RECIPE)
DIARY_URL            = svc_url(_PORT_DIARY)
GROCERY_URL          = svc_url(_PORT_GROCERY)
SUBSCRIPTION_URL     = svc_url(_PORT_SUBSCRIPTION)
MEAL_PLAN_URL        = svc_url(_PORT_MEAL_PLAN)
NOTIFICATION_URL     = svc_url(_PORT_NOTIFICATION)
FOOD_RECOGNITION_URL = svc_url(_PORT_FOOD_RECOGNITION)
CHAT_URL             = svc_url(_PORT_CHAT)
APPOINTMENT_URL      = svc_url(_PORT_APPOINTMENT)
VIDEO_URL            = svc_url(_PORT_VIDEO)
AI_CHAT_URL          = svc_url(_PORT_AI_CHAT)
PAYMENT_URL          = svc_url(_PORT_PAYMENT)
DELIVERY_URL         = svc_url(_PORT_DELIVERY)
WEARABLE_URL         = svc_url(_PORT_WEARABLE)
ADMIN_URL            = svc_url(_PORT_ADMIN)
FOOD_VISION_URL      = svc_url(_PORT_FOOD_VISION)
MARKETPLACE_URL      = svc_url(_PORT_MARKETPLACE)
GATEWAY_URL          = svc_url(_PORT_GATEWAY)
OLLAMA_URL           = os.getenv("OLLAMA_URL", svc_url(_PORT_OLLAMA))
DEFAULT_LLM_MODEL    = os.getenv("DEFAULT_LLM_MODEL", "ollama/llama3.2:latest")
TEMPORAL_UI_URL      = svc_url(_PORT_TEMPORAL_UI)

# Frontend origin (used in Stripe redirects, CORS fallbacks)
FRONTEND_URL         = os.getenv("FRONTEND_URL", f"{_SCHEME}://{_DOMAIN}:5173")

# ── Structured service catalogue ──────────────────────────────────────────────
# Used by the API Gateway aggregator and the admin health-probe loop.

SERVICES_CATALOGUE: List[Dict] = [
    {"name": "Auth Service",              "key": "auth",             "url": AUTH_URL,             "prefix": "/api/v1/auth"},
    {"name": "Compliance Service",        "key": "compliance",       "url": COMPLIANCE_URL,       "prefix": "/api/v1/compliance"},
    {"name": "Profile & Onboarding",      "key": "profile",          "url": PROFILE_URL,          "prefix": "/api/v1/profile"},
    {"name": "Recipe & Food DB",          "key": "recipe",           "url": RECIPE_URL,           "prefix": "/api/v1/recipes"},
    {"name": "Food Diary",                "key": "diary",            "url": DIARY_URL,            "prefix": "/api/v1/diary"},
    {"name": "Grocery List",              "key": "grocery",          "url": GROCERY_URL,          "prefix": "/api/v1/grocery"},
    {"name": "Subscriptions",             "key": "subscriptions",    "url": SUBSCRIPTION_URL,     "prefix": "/api/v1/subscriptions"},
    {"name": "Meal Plan Engine",          "key": "meal_plan",        "url": MEAL_PLAN_URL,        "prefix": "/api/v1/plan"},
    {"name": "Notifications",             "key": "notifications",    "url": NOTIFICATION_URL,     "prefix": "/api/v1/notifications"},
    {"name": "Food Recognition",          "key": "food_recognition", "url": FOOD_RECOGNITION_URL, "prefix": "/api/v1/food-recognition"},
    {"name": "AI Chat (WebSocket)",        "key": "chat",             "url": CHAT_URL,             "prefix": "/api/v1/chat"},
    {"name": "Appointments",              "key": "appointment",      "url": APPOINTMENT_URL,      "prefix": "/api/v1/appointments"},
    {"name": "Video Consultation",        "key": "video",            "url": VIDEO_URL,            "prefix": "/api/v1/video"},
    {"name": "AI Chatbot",                "key": "ai_chat",          "url": AI_CHAT_URL,          "prefix": "/api/v1/ai-chat"},
    {"name": "Payment",                   "key": "payment",          "url": PAYMENT_URL,          "prefix": "/api/v1/payment"},
    {"name": "Delivery",                  "key": "delivery",         "url": DELIVERY_URL,         "prefix": "/api/v1/delivery"},
    {"name": "Wearable",                  "key": "wearable",         "url": WEARABLE_URL,         "prefix": "/api/v1/wearable"},
    {"name": "Admin",                     "key": "admin",            "url": ADMIN_URL,            "prefix": "/api/v1/admin"},
    {"name": "Marketplace",               "key": "marketplace",      "url": MARKETPLACE_URL,      "prefix": "/api/v1/marketplace"},
    {"name": "Ollama LLM Engine",         "key": "ollama",           "url": OLLAMA_URL,           "prefix": "/api"},
    {"name": "Temporal Server & UI",      "key": "temporal",         "url": TEMPORAL_UI_URL,      "prefix": ""},
]

# Simple (name, health_url) tuples for health-probe loops
SERVICES_HEALTH_MAP: List[Tuple[str, str]] = [
    (
        svc["name"],
        f"{svc['url']}/" if svc["key"] in ("ollama", "temporal") else f"{svc['url']}/health"
    )
    for svc in SERVICES_CATALOGUE
]
