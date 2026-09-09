import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../theme/colors.dart';

class ExpertBottomNav extends StatelessWidget {
  final int currentIndex;

  const ExpertBottomNav({
    super.key,
    required this.currentIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        border: Border(
          top: BorderSide(
            color: NutriColors.border.withValues(alpha: 0.6),
            width: 1,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, -3),
          ),
        ],
      ),
      child: BottomNavigationBar(
        currentIndex: currentIndex,
        onTap: (index) {
          if (index == currentIndex) return;
          switch (index) {
            case 0:
              context.go('/expert/dashboard');
              break;
            case 1:
              context.go('/expert/patients');
              break;
            case 2:
              context.go('/expert/messages');
              break;
            case 3:
              context.go('/expert/settings');
              break;
          }
        },
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.transparent,
        elevation: 0,
        selectedItemColor: NutriColors.primary,
        unselectedItemColor: NutriColors.inkMuted,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11),
        unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w500, fontSize: 11),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard_rounded),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people_outline_rounded),
            activeIcon: Icon(Icons.people_rounded),
            label: 'Patients',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.forum_outlined),
            activeIcon: Icon(Icons.forum_rounded),
            label: 'Messages',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.badge_outlined),
            activeIcon: Icon(Icons.badge_rounded),
            label: 'Practice',
          ),
        ],
      ),
    );
  }
}
