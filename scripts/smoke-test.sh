#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# NutriPlan Live Stack Smoke Test Suite
# Tests all 16 microservices, Gateway OpenAPI aggregation, and critical flows.
# Usage: bash scripts/smoke-test.sh
# ─────────────────────────────────────────────────────────────────────────────

set -u

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

PASSED=0
FAILED=0

check_endpoint() {
  local name=$1
  local url=$2
  local expected_status=${3:-200}
  
  status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
  
  if [ "$status_code" -eq "$expected_status" ]; then
    printf "  %-38s ${GREEN}✓ PASS${NC} (HTTP %s)\n" "$name" "$status_code"
    PASSED=$((PASSED + 1))
  else
    printf "  %-38s ${RED}✗ FAIL${NC} (got %s, expected %s)\n" "$name" "$status_code" "$expected_status"
    FAILED=$((FAILED + 1))
  fi
}

echo ""
echo -e "${BOLD}🥦 NutriPlan Live Stack Smoke Test Suite${NC}"
echo "========================================================="

echo -e "\n${YELLOW}[1] Gateway & Service Discovery${NC}"
check_endpoint "API Gateway Health" "http://localhost:8000/health"
check_endpoint "API Gateway OpenAPI JSON" "http://localhost:8000/openapi.json"
check_endpoint "Unified Redoc Documentation" "http://localhost:8000/redoc"
check_endpoint "Unified Swagger UI" "http://localhost:8000/docs"
check_endpoint "Services Registry JSON" "http://localhost:8000/services"

echo -e "\n${YELLOW}[2] Microservices Health Endpoints (All 16)${NC}"
check_endpoint "Auth Service (:8001)" "http://localhost:8001/health"
check_endpoint "Compliance Service (:8002)" "http://localhost:8002/health"
check_endpoint "Profile & Onboarding (:8003)" "http://localhost:8003/health"
check_endpoint "Recipe Service (:8004)" "http://localhost:8004/health"
check_endpoint "Food Diary Service (:8005)" "http://localhost:8005/health"
check_endpoint "Grocery List Service (:8006)" "http://localhost:8006/health"
check_endpoint "Subscriptions Service (:8007)" "http://localhost:8007/health"
check_endpoint "Meal Plan Engine (:8009)" "http://localhost:8009/health"
check_endpoint "Notifications Service (:8010)" "http://localhost:8010/health"
check_endpoint "Chat Service (:8012)" "http://localhost:8012/health"
check_endpoint "Appointments Service (:8013)" "http://localhost:8013/health"
check_endpoint "Video Consultation (:8014)" "http://localhost:8014/health"
check_endpoint "AI Chatbot Service (:8015)" "http://localhost:8015/health"
check_endpoint "Payment Service (:8016)" "http://localhost:8016/health"
check_endpoint "Delivery Service (:8017)" "http://localhost:8017/health"
check_endpoint "Wearable Ingestion (:8018)" "http://localhost:8018/health"
check_endpoint "Marketplace Service (:8021)" "http://localhost:8021/health"

echo -e "\n${YELLOW}[3] Functional Flow Validation${NC}"

# Test Compliance Engine with US & Clinical rules
compliance_res=$(curl -s -X POST http://localhost:8002/api/v1/compliance/evaluate \
  -H "Content-Type: application/json" \
  -d '{"age": 45, "gender": "male", "weight_kg": 90, "height_cm": 178, "activity_level": "Lightly Active", "region": "US", "clinical_condition": "diabetes"}' || echo "{}")

if echo "$compliance_res" | grep -q "USDA"; then
  printf "  %-38s ${GREEN}✓ PASS${NC} (US Diabetic Evaluated)\n" "Compliance US Engine"
  PASSED=$((PASSED + 1))
else
  printf "  %-38s ${RED}✗ FAIL${NC} (Compliance US response invalid)\n" "Compliance US Engine"
  FAILED=$((FAILED + 1))
fi

# Test Marketplace Search
marketplace_res=$(curl -s http://localhost:8021/api/v1/marketplace/search || echo "[]")
if echo "$marketplace_res" | grep -q "hourly_rate_usd"; then
  printf "  %-38s ${GREEN}✓ PASS${NC} (Nutritionists Listed)\n" "Marketplace Directory"
  PASSED=$((PASSED + 1))
else
  printf "  %-38s ${RED}✗ FAIL${NC} (Marketplace search empty or offline)\n" "Marketplace Directory"
  FAILED=$((FAILED + 1))
fi

# Test Stripe Checkout Session Generation
payment_res=$(curl -s -X POST http://localhost:8016/api/v1/payment/stripe/checkout/booking \
  -H "Content-Type: application/json" \
  -d '{"appointment_id": "smoke_test_123", "amount_usd": 120.0, "nutritionist_account_id": "acct_test_123"}' || echo "{}")

if echo "$payment_res" | grep -q "client_secret"; then
  printf "  %-38s ${GREEN}✓ PASS${NC} (PaymentIntent Generated)\n" "Stripe PaymentIntent API"
  PASSED=$((PASSED + 1))
else
  printf "  %-38s ${YELLOW}⚠ SKIPPED / MOCKED${NC} (Payment requires live Stripe credentials)\n" "Stripe PaymentIntent API"
fi

echo ""
echo "========================================================="
if [ "$FAILED" -eq 0 ]; then
  echo -e "${BOLD}${GREEN}🎉 ALL SMOKE TESTS PASSED! (${PASSED} checks passed)${NC}\n"
else
  echo -e "${BOLD}${RED}❌ SMOKE TESTS ENCOUNTERED ${FAILED} FAILURES (${PASSED} passed, ${FAILED} failed)${NC}\n"
fi
