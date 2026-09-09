import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../widgets/macro_ring.dart';
import '../widgets/meal_card.dart';
import '../widgets/meal_detail_bottom_sheet.dart';
import '../providers/plan_provider.dart';
import '../../auth/providers/auth_provider.dart';

class TodayScreen extends ConsumerStatefulWidget {
  const TodayScreen({super.key});

  @override
  ConsumerState<TodayScreen> createState() => _TodayScreenState();
}

class _TodayScreenState extends ConsumerState<TodayScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final todayAsync = ref.watch(todayPlanProvider);
    final dateStr = DateFormat('EEE, MMM d').format(DateTime.now());

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvas,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Today', style: NutriTypography.displayMd),
            Text(dateStr, style: NutriTypography.dataMd),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.watch_rounded, color: NutriColors.primary),
            tooltip: 'Wearables Hub',
            onPressed: () => context.push('/wearables'),
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('All meals on track. Stay hydrated with 2.5L water today!')),
              );
            },
          ),
          const SizedBox(width: 4),
          Consumer(
            builder: (context, ref, _) {
              final user = ref.watch(authProvider).user;
              final initials = (user?.name != null && user!.name!.isNotEmpty)
                  ? user.name!.trim().split(' ').map((e) => e.isNotEmpty ? e[0].toUpperCase() : '').take(2).join()
                  : 'U';
              return GestureDetector(
                onTap: () => context.push('/profile'),
                child: CircleAvatar(
                  radius: 16,
                  backgroundColor: NutriColors.primarySoft,
                  child: Text(
                    initials,
                    style: const TextStyle(
                      color: NutriColors.primaryStrong,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              );
            },
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: todayAsync.when(
        loading: () => const Center(child: CircularProgressIndicator(color: NutriColors.primary)),
        error: (err, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off_rounded, size: 48, color: NutriColors.inkMuted),
              const SizedBox(height: 16),
              const Text('Could not load your daily plan', style: NutriTypography.bodyMd),
              const SizedBox(height: 6),
              Text('Make sure the backend services are running.', style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted)),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => ref.invalidate(todayPlanProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Try Again'),
              )
            ],
          ),
        ),
        data: (summary) => RefreshIndicator(
          onRefresh: () async => ref.refresh(todayPlanProvider),
          color: NutriColors.primary,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ── Macro Ring Dashboard ───────────────────────────────────
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: NutriColors.canvasRaised,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: NutriColors.border),
                    boxShadow: [
                      BoxShadow(color: Colors.black.withValues(alpha: 0.02), blurRadius: 10, offset: const Offset(0, 4))
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      MacroRing(
                        calories: summary.caloriesEaten.toDouble(),
                        maxCalories: summary.targetCalories.toDouble(),
                        size: 140,
                        strokeWidth: 14,
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildMacroBar('Protein', summary.proteinG, summary.targetProteinG, MacroColors.protein),
                          const SizedBox(height: 16),
                          _buildMacroBar('Carbs', summary.carbsG, summary.targetCarbsG, MacroColors.carbs),
                          const SizedBox(height: 16),
                          _buildMacroBar('Fat', summary.fatG, summary.targetFatG, MacroColors.fat),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // ── ICMR-NIN Micronutrient Deficit & Auto-Fix Banner ───────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade50,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.amber.shade300),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.amber.shade200.withValues(alpha: 0.6),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.water_drop_rounded, color: Colors.amber, size: 20),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  'Iron Deficit Alert (35%)',
                                  style: NutriTypography.dataMd.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.amber.shade900,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.amber.shade200,
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    'Auto-Fixed',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.amber.shade900,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Intake is below ICMR-NIN target (13.5mg vs 21mg). Auto-added high-iron regional meals in your lunch & dinner slots.',
                              style: NutriTypography.bodySm.copyWith(
                                color: Colors.brown.shade800,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // ── Quick Actions Hub ──────────────────────────────────────
                // Named & prominent — so users can always find AI Food Scanner
                // and Smart Grocery without hunting through the nav bar.
                const Text('Quick Actions', style: NutriTypography.displaySm),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _QuickActionCard(
                        icon: Icons.camera_alt_rounded,
                        emoji: '📸',
                        title: 'AI Food Scanner',
                        subtitle: 'Snap & auto-log\nyour meal calories',
                        gradientColors: const [Color(0xFF6C47FF), Color(0xFF9B78FF)],
                        onTap: () => context.push('/camera'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _QuickActionCard(
                        icon: Icons.shopping_cart_rounded,
                        emoji: '🛒',
                        title: 'Smart Grocery',
                        subtitle: 'Auto-generate weekly\nshopping list',
                        gradientColors: const [Color(0xFF22C55E), Color(0xFF16A34A)],
                        onTap: () => context.push('/grocery'),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // ── Meals List Header with Regional Grounding Badge ─────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Your Daily Plan', style: NutriTypography.displaySm),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: NutriColors.primary.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: NutriColors.primary.withValues(alpha: 0.3)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.eco_rounded, color: NutriColors.primary, size: 13),
                          SizedBox(width: 4),
                          Text('ICMR-NIN REGIONAL', style: TextStyle(color: NutriColors.primary, fontSize: 10, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    )
                  ],
                ),
                const SizedBox(height: 16),

                if (summary.meals.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: NutriColors.canvasRaised,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: NutriColors.border),
                    ),
                    child: const Center(
                      child: Text('No meals scheduled for today yet.', style: NutriTypography.bodyMd),
                    ),
                  )
                else
                  ...summary.meals.map(
                    (meal) => Padding(
                      padding: const EdgeInsets.only(bottom: 16.0),
                      child: NutriMealCard(
                        id: meal.id,
                        title: meal.title,
                        imageUrl: meal.imageUrl ??
                            'https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&q=80',
                        calories: meal.calories,
                        protein: meal.protein,
                        carbs: meal.carbs,
                        fat: meal.fat,
                        isLogged: meal.isLogged,
                        statusLabel: meal.mealType,
                        onLog: () async {
                          final entryId = await ref
                              .read(mealPlanServiceProvider)
                              .logMeal(
                                meal.id,
                                mealName: meal.title,
                                calories: meal.calories,
                                protein: meal.protein,
                                carbs: meal.carbs,
                                fat: meal.fat,
                                mealType: meal.mealType,
                              );
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                backgroundColor: entryId != null ? NutriColors.success : NutriColors.danger,
                                behavior: SnackBarBehavior.floating,
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12)),
                                content: Text(
                                  entryId != null
                                    ? '✅ Logged ${meal.title} to your Diary!'
                                    : '⚠️ Could not log meal — please sign in.',
                                ),
                              ),
                            );
                            // Always invalidate so macros reflect new state
                            ref.invalidate(todayPlanProvider);
                          }
                        },
                        onUnlog: () async {
                          if (meal.loggedEntryId != null) {
                            await ref
                                .read(mealPlanServiceProvider)
                                .unlogMeal(meal.loggedEntryId!);
                          }
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                backgroundColor: NutriColors.danger,
                                behavior: SnackBarBehavior.floating,
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12)),
                                content: Text(
                                    '🗑️ Removed ${meal.title} from Diary'),
                              ),
                            );
                            // Invalidate so macros drop accordingly
                            ref.invalidate(todayPlanProvider);
                          }
                        },
                        onSwap: () async {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                                content: Text(
                                    'Finding ICMR-NIN alternative with matching macros...')),
                          );
                          final swapped = await ref
                              .read(mealPlanServiceProvider)
                              .swapMeal(
                                currentMealName: meal.title,
                                mealType: meal.mealType,
                                targetCalories: meal.calories.toDouble(),
                              );
                          if (context.mounted) {
                            if (swapped != null) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  backgroundColor: NutriColors.primary,
                                  behavior: SnackBarBehavior.floating,
                                  shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12)),
                                  content: Text(
                                      'Swapped to: ${swapped.title} (${swapped.calories} kcal)'),
                                ),
                              );
                              ref.invalidate(todayPlanProvider);
                            } else {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                    content: Text(
                                        'No alternative found in this macro slot')),
                              );
                            }
                          }
                        },
                        onTap: () {
                          showModalBottomSheet(
                            context: context,
                            isScrollControlled: true,
                            backgroundColor: Colors.transparent,
                            builder: (ctx) => MealDetailBottomSheet(
                              meal: meal,
                              mealPlanService:
                                  ref.read(mealPlanServiceProvider),
                              onLogToggled: (newEntryId) {
                                ref.invalidate(todayPlanProvider);
                              },
                            ),
                          );
                        },
                      ),
                    ),
                  ),

                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
      // ── Bottom Navigation Bar (5 items, no ambiguous center FAB) ────────
      // AI Food Scanner is now a Quick Action card on the dashboard — labelled
      // and prominent. The bottom nav keeps standard navigation destinations.
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) {
          setState(() => _currentIndex = i);
          if (i == 1) {
            context.push('/diary');
          } else if (i == 2) {
            context.push('/grocery');
          } else if (i == 3) {
            context.push('/chat');
          } else if (i == 4) {
            context.push('/profile');
          }
        },
        selectedItemColor: NutriColors.primary,
        unselectedItemColor: NutriColors.inkMuted,
        showSelectedLabels: true,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
        backgroundColor: NutriColors.canvasRaised,
        elevation: 8,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 11),
        unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w400, fontSize: 11),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home_rounded),
            label: 'Today',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.menu_book_outlined),
            activeIcon: Icon(Icons.menu_book_rounded),
            label: 'Diary',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart_outlined),
            activeIcon: Icon(Icons.shopping_cart_rounded),
            label: 'Grocery',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_bubble_outline_rounded),
            activeIcon: Icon(Icons.chat_bubble_rounded),
            label: 'Care Chat',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline_rounded),
            activeIcon: Icon(Icons.person_rounded),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  Widget _buildMacroBar(String label, int current, int max, Color color) {
    final double pct = max > 0 ? (current / max).clamp(0.0, 1.0) : 0.0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: NutriTypography.dataMd.copyWith(color: NutriColors.ink, fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Text('${current}g / ${max}g', style: NutriTypography.dataSm),
          ],
        ),
        const SizedBox(height: 6),
        Container(
          width: 120,
          height: 6,
          decoration: BoxDecoration(
            color: NutriColors.border,
            borderRadius: BorderRadius.circular(3),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: pct,
            child: Container(
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Quick Action Card Widget
// Shown on the Today dashboard to give clear, named shortcuts to
// AI Food Scanner and Smart Grocery — fixing the navigation confusion
// where a bare camera FAB was mistaken for the grocery destination.
// ─────────────────────────────────────────────────────────────────────────────

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String emoji;
  final String title;
  final String subtitle;
  final List<Color> gradientColors;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.emoji,
    required this.title,
    required this.subtitle,
    required this.gradientColors,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradientColors,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: gradientColors.first.withValues(alpha: 0.35),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: Colors.white, size: 22),
            ),
            const SizedBox(height: 10),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 13,
                height: 1.2,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.82),
                fontSize: 10.5,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
