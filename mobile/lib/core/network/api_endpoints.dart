import 'dart:io';

class ApiEndpoints {
  // Configured for iOS simulator / macOS desktop (localhost) and Android emulator (10.0.2.2)
  static String get _host {
    try {
      if (Platform.isAndroid) return '10.0.2.2';
    } catch (_) {}
    return 'localhost';
  }

  static String get authBaseUrl => 'http://$_host:8001/api/v1/auth';
  static String get userBaseUrl => 'http://$_host:8003/api/v1/profile';
  static String get onboardingBaseUrl => 'http://$_host:8003/api/v1/profile';
  static String get recipeBaseUrl => 'http://$_host:8004/api/v1/recipes';
  static String get diaryBaseUrl => 'http://$_host:8005/api/v1/diary';
  static String get groceryBaseUrl => 'http://$_host:8006/api/v1/grocery';
  static String get subscriptionBaseUrl => 'http://$_host:8007/api/v1/subscriptions';
  static String get planBaseUrl => 'http://$_host:8009/api/v1/plan';
  static String get notificationsBaseUrl => 'http://$_host:8010/api/v1/notifications';
  static String get visionBaseUrl => 'http://$_host:8011/api/v1/food-recognition';
  static String get chatBaseUrl => 'http://$_host:8012/api/v1/chat';
  static String get appointmentBaseUrl => 'http://$_host:8013/api/v1/appointments';
  static String get aiChatBaseUrl => 'http://$_host:8015/api/v1/ai-chat';
  static String get deliveryBaseUrl => 'http://$_host:8017/api/v1/delivery';
  static String get wearableBaseUrl => 'http://$_host:8018/api/v1/wearables';
  static String get marketplaceBaseUrl => 'http://$_host:8025/api/v1/marketplace';
  static String get aiChatWsUrl => 'ws://$_host:8015/api/v1/ai-chat/ws';
}
