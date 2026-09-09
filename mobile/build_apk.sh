#!/usr/bin/env bash
set -e

echo "=== Building NutriPlan Android Release APK ==="

export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

flutter build apk --release \
  --dart-define=APP_DOMAIN=192.168.0.101 \
  --dart-define=APP_SCHEME=http \
  --dart-define=API_HOST=192.168.0.101 \
  --dart-define=API_SCHEME=http

mkdir -p "$SCRIPT_DIR/../build_artifacts"
cp "$SCRIPT_DIR/build/app/outputs/flutter-apk/app-release.apk" "$SCRIPT_DIR/../build_artifacts/NutriPlan.apk"

echo "✅ APK successfully generated at: $SCRIPT_DIR/../build_artifacts/NutriPlan.apk"
