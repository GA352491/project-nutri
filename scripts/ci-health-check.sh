#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# NutriPlan CI Health Check
# Waits for all backend microservices to become healthy before running E2E tests.
# Usage: bash scripts/ci-health-check.sh [--timeout=60]
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

TIMEOUT=${1:-60}
INTERVAL=2

declare -A SERVICES=(
  ["auth"]="http://localhost:8001/health"
  ["profile"]="http://localhost:8003/health"
  ["meal_plan"]="http://localhost:8009/health"
  ["diary"]="http://localhost:8005/health"
  ["grocery"]="http://localhost:8006/health"
  ["chat"]="http://localhost:8012/health"
  ["marketplace"]="http://localhost:8021/health"
  ["notifications"]="http://localhost:8010/health"
  ["recipe"]="http://localhost:8004/health"
)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

wait_for_service() {
  local name=$1
  local url=$2
  local elapsed=0

  printf "  Waiting for %-16s %s" "$name" "$url"

  while [ $elapsed -lt $TIMEOUT ]; do
    if curl -sf "$url" > /dev/null 2>&1; then
      printf " ${GREEN}✓${NC}\n"
      return 0
    fi
    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
    printf "."
  done

  printf " ${RED}✗ TIMEOUT${NC}\n"
  return 1
}

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║       NutriPlan CI — Service Health Check            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

FAILED=0
for name in "${!SERVICES[@]}"; do
  url="${SERVICES[$name]}"
  if ! wait_for_service "$name" "$url"; then
    FAILED=$((FAILED + 1))
  fi
done

echo ""
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✅  All services healthy — E2E tests can proceed.${NC}"
  exit 0
else
  echo -e "${RED}❌  $FAILED service(s) failed to start within ${TIMEOUT}s.${NC}"
  echo -e "${YELLOW}   Check logs with: bash scripts/start-dev.sh${NC}"
  exit 1
fi
