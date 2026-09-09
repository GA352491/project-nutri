import 'dart:io' show Platform;

class ApiEndpoints {
  // ─────────────────────────────────────────────────────────────────────────
  // Configure via compile-time dart-define (preferred for CI/staging/prod):
  //   flutter run --dart-define=APP_DOMAIN=api.nutriplan.app --dart-define=APP_SCHEME=https
  //
  // For local dev on a physical device via Wi-Fi, pass your machine's LAN IP:
  //   flutter run --dart-define=APP_DOMAIN=192.168.1.42
  // ─────────────────────────────────────────────────────────────────────────
  static const String _envDomain = String.fromEnvironment('APP_DOMAIN', defaultValue: '');
  static const String _envHost = String.fromEnvironment('API_HOST', defaultValue: '');
  static const String _envScheme = String.fromEnvironment('APP_SCHEME', defaultValue: '');
  static const String _envApiScheme = String.fromEnvironment('API_SCHEME', defaultValue: 'http');

  /// Resolves the API host in order of priority:
  /// 1. `--dart-define=APP_DOMAIN=...` or `--dart-define=API_HOST=...`
  /// 2. Android emulator → 10.0.2.2 (routes to host machine localhost)
  /// 3. iOS simulator / macOS → 127.0.0.1 (host loopback)
  static String get domain {
    if (_envDomain.isNotEmpty) return _envDomain;
    if (_envHost.isNotEmpty) return _envHost;
    try {
      if (Platform.isAndroid) return '10.0.2.2';
    } catch (_) {}
    return '127.0.0.1';
  }

  static String get scheme => _envScheme.isNotEmpty ? _envScheme : _envApiScheme;
  static String get wsScheme => scheme == 'https' ? 'wss' : 'ws';

  static String serviceUrl(int port, String path) => '$scheme://$domain:$port$path';

  // ── Microservice base URLs ──────────────────────────────────────────────
  static String get authBaseUrl          => serviceUrl(8001, '/api/v1/auth');
  static String get userBaseUrl          => serviceUrl(8003, '/api/v1/profile');
  static String get onboardingBaseUrl    => serviceUrl(8003, '/api/v1/profile');
  static String get recipeBaseUrl        => serviceUrl(8004, '/api/v1/recipes');
  static String get diaryBaseUrl         => serviceUrl(8005, '/api/v1/diary');
  static String get groceryBaseUrl       => serviceUrl(8006, '/api/v1/grocery');
  static String get subscriptionBaseUrl  => serviceUrl(8007, '/api/v1/subscriptions');
  static String get planBaseUrl          => serviceUrl(8009, '/api/v1/plan');
  static String get notificationsBaseUrl => serviceUrl(8010, '/api/v1/notifications');
  static String get visionBaseUrl        => serviceUrl(8011, '/api/v1/food-recognition');
  static String get chatBaseUrl          => serviceUrl(8012, '/api/v1/chat');
  static String get appointmentBaseUrl   => serviceUrl(8013, '/api/v1/appointments');
  static String get aiChatBaseUrl        => serviceUrl(8015, '/api/v1/ai-chat');
  static String get paymentBaseUrl       => serviceUrl(8016, '/api/v1/payment');
  static String get deliveryBaseUrl      => serviceUrl(8017, '/api/v1/delivery');
  static String get wearableBaseUrl      => serviceUrl(8018, '/api/v1/wearables');
  static String get marketplaceBaseUrl   => serviceUrl(8025, '/api/v1/marketplace');
  static String get aiChatWsUrl          => '$wsScheme://$domain:8015/api/v1/ai-chat/ws';
}
