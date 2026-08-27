#!/usr/bin/env bash
# ========================================================
# NutriPlan — Stop All Services Script
# Gracefully terminates all backend microservices, Temporal,
# workers, frontend dev servers, and releases all reserved ports.
# ========================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT/.nutriplan.pids"
LOG_DIR="$ROOT/.logs"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

ok()   { echo -e "${GREEN}✅  $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $*${NC}"; }
hdr()  { echo -e "\n${YELLOW}━━━ $* ━━━${NC}"; }

hdr "Stopping NutriPlan Ecosystem"

# 1. Terminate tracked processes via PID file if present
if [[ -f "$PID_FILE" ]]; then
  while IFS='=' read -r name pid; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && ok "Stopped $name (PID $pid)"
    fi
  done < "$PID_FILE"
  rm -f "$PID_FILE"
fi

# 2. Terminate all uvicorn, vite, temporal, faststream, and temporal_hub processes
pkill -f "uvicorn src\." 2>/dev/null && ok "Terminated uvicorn backend workers" || true
pkill -f "temporal_hub.py" 2>/dev/null && ok "Terminated Temporal Hub worker" || true
pkill -f "temporal server" 2>/dev/null && ok "Terminated Temporal Dev Server" || true
pkill -f "vite" 2>/dev/null && ok "Terminated Vite dev server" || true

# 3. Release all known ecosystem ports
PORTS=(
  5173  # Frontend (Vite)
  7233  # Temporal gRPC Server
  8233  # Temporal Web UI
  8000  # API Gateway
  8001  # Auth Service
  8002  # Compliance Service
  8003  # Profile Service
  8004  # Recipe Service
  8005  # Diary Service
  8006  # Grocery Service
  8007  # Subscription Service
  8009  # Meal Plan Service
  8010  # Notification Service
  8011  # Food Recognition Service
  8012  # Chat Service
  8013  # Appointment Service
  8014  # Video Service
  8015  # AI Chatbot Service
  8016  # Payment Service
  8017  # Delivery Service
  8018  # Wearable Service
  8019  # Analytics Service
  8020  # Admin Service
  8025  # Marketplace Service
)

for port in "${PORTS[@]}"; do
  pids=$(lsof -ti:"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    for pid in $pids; do
      kill -9 "$pid" 2>/dev/null && ok "Released port $port (killed PID $pid)" || true
    done
  fi
done

echo ""
ok "All NutriPlan microservices and background processes have been completely stopped."
echo ""
