#!/usr/bin/env bash
set -e

echo "=== Building NutriPlan macOS DMG Installer ==="

export PATH="/usr/local/opt/ruby/bin:/usr/local/lib/ruby/gems/3.4.0/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

flutter build macos --release \
  --dart-define=API_SCHEME=http \
  --dart-define=API_HOST=localhost \
  --dart-define=AUTH_PORT=8001 \
  --dart-define=PROFILE_PORT=8003 \
  --dart-define=RECIPE_PORT=8004 \
  --dart-define=DIARY_PORT=8005 \
  --dart-define=GROCERY_PORT=8006 \
  --dart-define=SUBSCRIPTION_PORT=8007 \
  --dart-define=MEAL_PLAN_PORT=8009 \
  --dart-define=FOOD_RECOGNITION_PORT=8011 \
  --dart-define=CHAT_PORT=8012 \
  --dart-define=APPOINTMENT_PORT=8013 \
  --dart-define=VIDEO_PORT=8014 \
  --dart-define=AI_CHATBOT_PORT=8015 \
  --dart-define=PAYMENT_PORT=8016 \
  --dart-define=WEARABLE_PORT=8018

mkdir -p "$SCRIPT_DIR/../build_artifacts"
hdiutil create -volname "NutriPlan" -srcfolder "$SCRIPT_DIR/build/macos/Build/Products/Release/nutriplan.app" -ov -format UDZO "$SCRIPT_DIR/../build_artifacts/NutriPlan.dmg"

echo "✅ DMG successfully generated at: $SCRIPT_DIR/../build_artifacts/NutriPlan.dmg"
