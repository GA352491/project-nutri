#!/usr/bin/env bash
# ========================================================
# NutriPlan — Unified Ecosystem Startup Script
# Usage: ./start_all.sh [--stop] [--status]
# ========================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
LOG_DIR="$ROOT/.logs"
PID_FILE="$ROOT/.nutriplan.pids"

# Ensure common system and runtime paths are available
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Applications/Postgres.app/Contents/Versions/18/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

mkdir -p "$LOG_DIR"

GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
ok()   { echo -e "${GREEN}✅  $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $*${NC}"; }
err()  { echo -e "${RED}❌  $*${NC}"; }
hdr()  { echo -e "\n${YELLOW}━━━ $* ━━━${NC}"; }

# ── STOP ──────────────────────────────────────────────────
if [[ "${1:-}" == "--stop" ]]; then
  hdr "Stopping all NutriPlan services"
  if [[ -f "$PID_FILE" ]]; then
    while IFS='=' read -r name pid; do
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" && ok "Stopped $name (PID $pid)"
      fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
  fi
  for port in 7233 8233 8001 8002 8003 8004 8005 8006 8007 8009 8010 8011 8012 8013 8014 8015 8016 8017 8018 8019 8020 8025 5173; do
    pid=$(lsof -ti:"$port" 2>/dev/null || true)
    [[ -n "$pid" ]] && kill $pid 2>/dev/null && ok "Released port $port" || true
  done
  ok "All services stopped."
  exit 0
fi

# ── STATUS ─────────────────────────────────────────────────
if [[ "${1:-}" == "--status" ]]; then
  hdr "NutriPlan Service Status"
  check_port() {
    local name="$1" port="$2"
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 1 "http://localhost:$port/health" 2>/dev/null || echo "DOWN")
    if [[ "$code" == "200" ]]; then ok "$name — :$port"; else err "$name — :$port (HTTP $code)"; fi
  }
  check_port "Frontend (Vite)"       5173
  check_port "Auth Service"          8001
  check_port "Compliance Service"    8002
  check_port "Profile Service"       8003
  check_port "Recipe Service"        8004
  check_port "Diary Service"         8005
  check_port "Grocery Service"       8006
  check_port "Subscription Service"  8007
  check_port "Meal Plan Service"     8009
  check_port "Notification Service"  8010
  check_port "Food Recognition"      8011
  check_port "Chat Service"          8012
  check_port "Appointment Service"   8013
  check_port "Video Service"         8014
  check_port "AI Chatbot Service"    8015
  check_port "Payment Service"       8016
  check_port "Delivery Service"      8017
  check_port "Wearable Service"      8018
  check_port "Analytics Service"     8019
  check_port "Admin Service"         8020
  check_port "Marketplace Service"   8025
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 1 "http://localhost:8233" 2>/dev/null || echo "DOWN")
  if [[ "$code" == "200" ]]; then ok "Temporal Web UI      — :8233"; else err "Temporal Web UI      — :8233"; fi
  exit 0
fi

# ── START ──────────────────────────────────────────────────
> "$PID_FILE"

echo ""
echo -e "${GREEN}   ╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}   ║       NutriPlan Ecosystem Startup         ║${NC}"
echo -e "${GREEN}   ║  Powered by Temporal Durable Workflows     ║${NC}"
echo -e "${GREEN}   ╚═══════════════════════════════════════════╝${NC}"
echo ""

SHARED_PATH="$BACKEND/shared/src"

PYTHON="$ROOT/.venv/bin/python"

start_uvicorn() {
  local name="$1" port="$2" dir="$3" module="$4"
  existing=$(lsof -ti:"$port" 2>/dev/null || true)
  [[ -n "$existing" ]] && kill $existing 2>/dev/null && sleep 0.3 || true
  echo -e "  ${YELLOW}→ $name :$port${NC}"
  (
    cd "$dir"
    PYTHONPATH="$SHARED_PATH" \
    "$PYTHON" -m uvicorn "$module" --host 0.0.0.0 --port "$port" --log-level warning
  ) > "$LOG_DIR/${name// /_}.log" 2>&1 &
  echo "$name=$!" >> "$PID_FILE"
  sleep 0.2
}

# 1. Temporal Server
hdr "1/4 — Temporal Dev Server (localhost:7233, UI: 8233)"
existing_temporal=$(lsof -ti:7233 2>/dev/null || true)
if [[ -n "$existing_temporal" ]]; then
  warn "Temporal already running on :7233 — skipping"
else
  temporal server start-dev --ui-port 8233 --port 7233 \
    > "$LOG_DIR/temporal.log" 2>&1 &
  echo "temporal=$!" >> "$PID_FILE"
  sleep 2
  ok "Temporal started → http://localhost:8233/namespaces/default/workflows"
fi

# 2. Backend Microservices
hdr "2/4 — Backend Microservices (20 services)"
start_uvicorn "Auth Service"            8001  "$BACKEND/auth"            "src.auth_service.main:app"
start_uvicorn "Compliance Service"      8002  "$BACKEND/compliance"      "src.compliance_service.main:app"
start_uvicorn "Profile Service"         8003  "$BACKEND/profile"         "src.profile_service.main:app"
start_uvicorn "Recipe Service"          8004  "$BACKEND/recipe"          "src.recipe_service.main:app"
start_uvicorn "Diary Service"           8005  "$BACKEND/diary"           "src.diary_service.main:app"
start_uvicorn "Grocery Service"         8006  "$BACKEND/grocery"         "src.grocery_service.main:app"
start_uvicorn "Subscription Service"    8007  "$BACKEND/subscriptions"   "src.subscription_service.main:app"
start_uvicorn "Meal Plan Service"       8009  "$BACKEND/meal_plan"       "src.meal_plan_service.main:app"
start_uvicorn "Notification Service"    8010  "$BACKEND/notifications"   "src.notification_service.main:app"
start_uvicorn "Food Recognition"        8011  "$BACKEND/food_recognition" "src.food_recognition_service.main:app"
start_uvicorn "Chat Service"            8012  "$BACKEND/chat"            "src.chat_service.main:app"
start_uvicorn "Appointment Service"     8013  "$BACKEND/appointment"     "src.appointment_service.main:app"
start_uvicorn "Video Service"           8014  "$BACKEND/video"           "src.video_service.main:app"
start_uvicorn "AI Chatbot"              8015  "$BACKEND/ai_chatbot"      "src.chatbot_service.main:app"
start_uvicorn "Payment Service"         8016  "$BACKEND/payment"         "src.payment_service.main:app"
start_uvicorn "Delivery Service"        8017  "$BACKEND/delivery"        "src.delivery_service.main:app"
start_uvicorn "Wearable Service"        8018  "$BACKEND/wearable"        "src.wearable_service.main:app"
start_uvicorn "Analytics Service"       8019  "$BACKEND/analytics"       "src.analytics_service.main:app"
start_uvicorn "Admin Service"           8020  "$BACKEND/admin"           "src.admin_service.main:app"
start_uvicorn "Marketplace Service"     8025  "$BACKEND/marketplace"     "src.marketplace_service.main:app"
ok "All 20 microservices starting..."

# 3. Temporal Hub
hdr "3/4 — Temporal Master Worker Hub"
sleep 2
(
  PYTHONPATH="$SHARED_PATH:$BACKEND/appointment/src:$BACKEND/meal_plan/src:$BACKEND/subscriptions/src:$BACKEND/notifications/src:$BACKEND/delivery/src:$BACKEND/payment/src" \
  "$PYTHON" "$BACKEND/shared/src/nutriplan_shared/temporal_hub.py"
) > "$LOG_DIR/temporal_hub.log" 2>&1 &
echo "temporal_hub=$!" >> "$PID_FILE"
ok "Temporal Hub started — 5 workflow queues active"

# 4. Frontend
hdr "4/4 — Frontend Dev Server (localhost:5173)"
existing_fe=$(lsof -ti:5173 2>/dev/null || true)
if [[ -n "$existing_fe" ]]; then
  warn "Frontend already running on :5173 — skipping"
else
  (cd "$FRONTEND" && npm run dev) > "$LOG_DIR/frontend.log" 2>&1 &
  echo "frontend=$!" >> "$PID_FILE"
fi

# Summary
hdr "Waiting 5s for services to initialize..."
sleep 5

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   NutriPlan Ecosystem READY 🚀                     ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   🌐  Frontend App       →  ${GREEN}http://localhost:5173${NC}"
echo -e "   ⚡  Temporal Web UI    →  ${GREEN}http://localhost:8233/namespaces/default/workflows${NC}"
echo -e "   📋  Meal Plan API Docs →  ${GREEN}http://localhost:8009/docs${NC}"
echo -e "   📋  Auth API Docs      →  ${GREEN}http://localhost:8001/docs${NC}"
echo -e "   📋  Payment API Docs   →  ${GREEN}http://localhost:8016/docs${NC}"
echo ""
echo -e "   Logs:   ${YELLOW}$LOG_DIR/${NC}"
echo -e "   Stop:   ${YELLOW}./start_all.sh --stop${NC}"
echo -e "   Status: ${YELLOW}./start_all.sh --status${NC}"
echo ""

wait
