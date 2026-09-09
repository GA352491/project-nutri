# NutriPlan Mobile — Build & Deployment Guide (Android & iOS)

This guide documents the exact prerequisites, commands, and steps to run, test, and generate **`.apk`** (Android) and **`.ipa`** (iOS) installation packages for NutriPlan on mobile devices.

---

## 1. Quick Reference: Built Artifacts

| Platform | Output Artifact | Location |
|---|---|---|
| **Android** | `NutriPlan.apk` | `/Users/anishganga/Project-nutri/build_artifacts/NutriPlan.apk` |
| **macOS** | `NutriPlan.dmg` | `/Users/anishganga/Project-nutri/build_artifacts/NutriPlan.dmg` |
| **iOS** | `NutriPlan.ipa` | Generated via Xcode Organizer archive export |

---

## 2. Environment Variables & Ports

When compiling release builds for mobile, Flutter injects microservice ports via `--dart-define`.

### Backend Host Settings
- **Android Emulator**: Uses `API_HOST=10.0.2.2` (the Android virtual router pointing to Mac host).
- **Physical Device (USB / Same Wi-Fi)**: Use your Mac's LAN IP (e.g. `192.168.1.X`) or run reverse proxy via ADB:
  ```bash
  adb reverse tcp:8001 tcp:8001
  adb reverse tcp:8003 tcp:8003
  # ... for all microservice ports 8001 through 8025
  ```
- **macOS Desktop / Simulator**: Uses `API_HOST=localhost`.

---

## 3. Android: Running & Generating `.apk`

### Prerequisites
1. **Java Development Kit (JDK 17 or 21)**: Bundled inside Android Studio:
   ```bash
   export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
   ```
2. **Android SDK & cmdline-tools**:
   ```bash
   export ANDROID_HOME="$HOME/Library/Android/sdk"
   export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
   ```

### Run on Connected Android Device or Emulator
```bash
cd /Users/anishganga/Project-nutri/mobile
flutter run -d android
```

### Generate Release `.apk`
Run the build script directly:
```bash
./mobile/build_apk.sh
```

Or execute manually:
```bash
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

cd /Users/anishganga/Project-nutri/mobile

flutter build apk --release \
  --dart-define=API_SCHEME=http \
  --dart-define=API_HOST=10.0.2.2 \
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
```

The compiled file will be at:
```
mobile/build/app/outputs/flutter-apk/app-release.apk
```

Copy it to the central artifact repository:
```bash
cp mobile/build/app/outputs/flutter-apk/app-release.apk /Users/anishganga/Project-nutri/build_artifacts/NutriPlan.apk
```

### Install APK onto Android Phone
```bash
# Option A: Directly via USB cable
adb install -r /Users/anishganga/Project-nutri/build_artifacts/NutriPlan.apk

# Option B: Wirelessly
# Transfer NutriPlan.apk to your phone (via Google Drive, AirDrop equivalent, or Slack/Email)
# Open the file on your device and allow "Install from Unknown Sources"
```

---

## 4. iOS: Running & Generating `.ipa`

iOS apps require code signing by Apple before they can be installed on a physical device.

### Step 1: Open the Project in Xcode
```bash
open /Users/anishganga/Project-nutri/mobile/ios/Runner.xcworkspace
```

### Step 2: Install Platform Component (One-Time)
If Xcode shows `Ineligible destinations: iOS is not installed`:
1. In Xcode, press `Cmd + ,` (or go to **Xcode** → **Settings**).
2. Click the **Components** tab.
3. Click the download icon next to the available **iOS Platform** to install the device runtime.

### Step 3: Configure Free Apple Developer Signing
1. Click the top-level **Runner** project in the left navigation sidebar.
2. Select the **Runner** target (under Targets).
3. Switch to the **Signing & Capabilities** tab.
4. Check **Automatically manage signing**.
5. In **Team**, choose your Personal Team (log in with your personal Apple ID if none is listed — no paid account required for personal device testing).
6. Set a unique **Bundle Identifier** (e.g. `com.anishganga.nutriplan`).

### Step 4: Archive and Export `.ipa`
1. Connect your iPhone to your Mac with a lightning/USB-C cable.
2. Select **Any iOS Device (arm64)** or your connected device as the build target in Xcode's top bar.
3. From the menu bar, select: **Product** → **Archive**.
4. When the **Organizer** window opens with your finished archive:
   - Click **Distribute App** in the right inspector.
   - Select **Custom** → **Development** (or **Ad-Hoc**).
   - Keep default signing options and click **Export**.
   - Select `/Users/anishganga/Project-nutri/build_artifacts/` as the destination.
   - The result will be **`NutriPlan.ipa`**.

### Step 5: Install `.ipa` on your iPhone
```bash
# Option A: Apple Configurator (Free from Mac App Store)
# Drag and drop NutriPlan.ipa onto your connected iPhone in Apple Configurator

# Option B: Sideloadly / AltStore
# Open Sideloadly, drag NutriPlan.ipa, select your iPhone, and click Start

# Option C: Direct Xcode Installation
# In Xcode, go to Window > Devices and Simulators (Cmd + Shift + 2)
# Under Installed Apps, click '+' and select NutriPlan.ipa (or Runner.app)
```

---

## 5. Automated Build Scripts

Helper scripts are available in the project to streamline these commands:

| Script | Action |
|---|---|
| `./mobile/build_apk.sh` | Builds release APK with all microservice ports and outputs to `build_artifacts/NutriPlan.apk` |
| `./mobile/build_dmg.sh` | Compiles macOS app and packages into `build_artifacts/NutriPlan.dmg` |
| `./mobile/build_ipa.sh` | Validates iOS workspace and launches Xcode Archive workflow |

---

## 6. Key Configuration Files Reference

- **Android Cleartext & Dev Network Policy**: `mobile/android/app/src/main/res/xml/network_security_config.xml`
- **Android Manifest & Permissions**: `mobile/android/app/src/main/AndroidManifest.xml`
- **iOS Permissions & HealthKit**: `mobile/ios/Runner/Info.plist`
- **Microservice Domain Registry**: `mobile/lib/core/network/api_endpoints.dart`
