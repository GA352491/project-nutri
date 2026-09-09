import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/register_screen.dart';
import '../features/onboarding/screens/onboarding_wizard.dart';
import '../features/plan/screens/today_screen.dart';
import '../features/photo_log/screens/camera_capture_screen.dart';
import '../features/profile/screens/profile_screen.dart';
import '../features/profile/wearables_hub_screen.dart';
import '../features/chat/screens/chat_screen.dart';
import '../features/diary/screens/daily_diary_screen.dart';
import '../features/grocery/screens/grocery_screen.dart';
import '../features/expert/screens/expert_dashboard_screen.dart';
import '../features/expert/screens/expert_patients_screen.dart';
import '../features/expert/screens/expert_messages_screen.dart';
import '../features/expert/screens/expert_settings_screen.dart';

final GlobalKey<NavigatorState> rootNavigatorKey = GlobalKey<NavigatorState>();

final GoRouter appRouter = GoRouter(
  navigatorKey: rootNavigatorKey,
  initialLocation: '/today',
  routes: [
    // ── Auth & Onboarding ──────────────────────────────────────────────────
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/onboarding',
      builder: (context, state) => const OnboardingWizard(),
    ),

    // ── Patient / Consumer Journey ─────────────────────────────────────────
    GoRoute(
      path: '/today',
      builder: (context, state) => const TodayScreen(),
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/camera',
      builder: (context, state) => const CameraCaptureScreen(),
    ),
    GoRoute(
      path: '/wearables',
      builder: (context, state) => const WearablesHubScreen(),
    ),
    GoRoute(
      path: '/chat',
      builder: (context, state) => const ChatScreen(),
    ),
    GoRoute(
      path: '/diary',
      builder: (context, state) => const DailyDiaryScreen(),
    ),
    GoRoute(
      path: '/grocery',
      builder: (context, state) => const GroceryScreen(),
    ),

    // ── Clinical Expert / Nutritionist Portal ─────────────────────────────
    GoRoute(
      path: '/expert',
      redirect: (context, state) => '/expert/dashboard',
    ),
    GoRoute(
      path: '/expert/dashboard',
      builder: (context, state) => const ExpertDashboardScreen(),
    ),
    GoRoute(
      path: '/expert/patients',
      builder: (context, state) => const ExpertPatientsScreen(),
    ),
    GoRoute(
      path: '/expert/messages',
      builder: (context, state) => const ExpertMessagesScreen(),
    ),
    GoRoute(
      path: '/expert/settings',
      builder: (context, state) => const ExpertSettingsScreen(),
    ),
  ],
);
