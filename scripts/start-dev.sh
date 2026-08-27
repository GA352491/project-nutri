#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# NutriPlan Local Development Startup Script
# ─────────────────────────────────────────────────────────────────────────────

set -e
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BOLD}🥦 NutriPlan — Local Dev Stack${NC}"
echo "============================================"

# ── 1. Infrastructure ─────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[1/4] Starting Infrastructure...${NC}"

# Redis (FastStream message broker)
if ! pgrep -x "redis-server" > /dev/null; then
  redis-server --daemonize yes --loglevel warning
  echo -e "${GREEN}  ✓ Redis started (localhost:6379)${NC}"
else
  echo -e "${GREEN}  ✓ Redis already running${NC}"
fi

# Ollama (local LLM for PydanticAI)
if ! pgrep -x "ollama" > /dev/null; then
  ollama serve > /dev/null 2>&1 &
  sleep 2
  echo -e "${GREEN}  ✓ Ollama started (localhost:11434)${NC}"
else
  echo -e "${GREEN}  ✓ Ollama already running${NC}"
fi

# ── 2. FastStream Broker ──────────────────────────────────────────────────────
echo -e "\n${YELLOW}[2/4] Starting FastStream Event Broker...${NC}"
PYTHONPATH="$ROOT_DIR/backend/shared/src:$PYTHONPATH" python3 -m nutriplan_shared.faststream_broker.broker > /dev/null 2>&1 &
FASTSTREAM_PID=$!
echo -e "${GREEN}  ✓ FastStream broker started (PID: $FASTSTREAM_PID)${NC}"

# ── 3. Temporal Workers ───────────────────────────────────────────────────────
echo -e "\n${YELLOW}[3/4] Starting Temporal Workers...${NC}"
if [ -d "$ROOT_DIR/backend/appointment/src" ]; then
  PYTHONPATH="$ROOT_DIR/backend/appointment/src:$ROOT_DIR/backend/shared/src:$PYTHONPATH" python3 -m appointment_service.temporal_workers.booking_worker > /dev/null 2>&1 &
  echo -e "${GREEN}  ✓ BookingWorkflow worker started${NC}"
fi

# ── 4. Microservices ──────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[4/4] Starting Microservices & Gateway...${NC}"

services=(
  "backend/gateway/src:gateway_service.main:8000:API Gateway & Unified Docs"
  "backend/auth/src:auth_service.main:8001:Auth"
  "backend/profile/src:profile_service.main:8003:Profile & Onboarding"
  "backend/recipe/src:recipe_service.main:8004:Recipe"
  "backend/diary/src:diary_service.main:8005:Food Diary"
  "backend/grocery/src:grocery_service.main:8006:Grocery"
  "backend/meal_plan/src:meal_plan_service.main:8009:Meal Plan (PydanticAI+Guardrails)"
  "backend/notifications/src:notification_service.main:8010:Notifications"
  "backend/chat/src:chat_service.main:8012:Chat"
  "backend/ai_chatbot/src:chatbot_service.main:8015:AI Chatbot (LangGraph)"
  "backend/appointment/src:appointment_service.main:8013:Appointments (Temporal)"
  "backend/video/src:video_service.main:8014:Video (Jitsi)"
  "backend/payment/src:payment_service.main:8016:Payment (Stripe)"
  "backend/delivery/src:delivery_service.main:8017:Delivery"
  "backend/wearable/src:wearable_service.main:8018:Wearable (FastStream)"
  "backend/marketplace/src:marketplace_service.main:8021:Marketplace"
  "backend/compliance/src:compliance_service.main:8002:Compliance (ICMR/USDA)"
  "backend/subscriptions/src:subscription_service.main:8007:Subscriptions & Growth"
)

for entry in "${services[@]}"; do
  IFS=: read -r rel_dir module port name <<< "$entry"
  full_dir="$ROOT_DIR/$rel_dir"
  if [ -d "$full_dir" ]; then
    (cd "$full_dir" && PYTHONPATH="$ROOT_DIR/backend/shared/src:$full_dir:$PYTHONPATH" uvicorn "$module:app" --port "$port" --reload --log-level error > /dev/null 2>&1) &
    echo -e "${GREEN}  ✓ $name Service → http://localhost:$port/docs${NC}"
  fi
done

echo ""
echo "============================================"
echo -e "${BOLD}${GREEN}🚀 All services running!${NC}"
echo ""
echo -e "  Unified Gateway & Docs: http://localhost:8000"
echo -e "  Frontend:               http://localhost:5173"
echo -e "  Temporal UI:            http://localhost:8233"
echo -e "  Ollama:                 http://localhost:11434"
echo ""
echo "  Press Ctrl+C to stop all services."

wait
