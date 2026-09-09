#!/usr/bin/env bash
set -e

echo "=== NutriPlan iOS .ipa Builder ==="
echo "Note: Building an installable .ipa requires Apple Developer Code Signing or an active Simulator/Device runtime."
echo ""
echo "Step 1: In Xcode, open: /Users/anishganga/Project-nutri/mobile/ios/Runner.xcworkspace"
echo "Step 2: Go to Xcode > Settings > Components and install the 'iOS 26.5' platform runtime."
echo "Step 3: Under 'Signing & Capabilities', select your Personal or Organization Team."
echo "Step 4: Run Product > Archive to export the signed .ipa for your iPhone."
