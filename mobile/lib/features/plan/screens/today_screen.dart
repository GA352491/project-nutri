import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../widgets/macro_ring.dart';
import '../widgets/meal_card.dart';
import '../providers/plan_provider.dart';

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
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Today', style: NutriTypography.displayMd),
            Text(dateStr, style: NutriTypography.dataMd),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          const SizedBox(width: 8),
          const CircleAvatar(
            radius: 16,
            backgroundImage: NetworkImage('https://i.pravatar.cc/150?u=patient'),
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
              const Text('Could not load daily plan', style: NutriTypography.bodyMd),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () => ref.refresh(todayPlanProvider),
                child: const Text('Retry'),
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
                // Macro Ring Dashboard
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

                // ICMR-NIN Micronutrient Deficit & Auto-Fix Banner
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

                const SizedBox(height: 24),
                
                // Meals List Header with Regional Grounding Badge
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
                        imageUrl: meal.imageUrl ?? 'https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&q=80',
                        calories: meal.calories,
                        protein: meal.protein,
                        carbs: meal.carbs,
                        fat: meal.fat,
                        isLogged: meal.isLogged,
                        statusLabel: meal.mealType,
                        onLog: () {
                          ref.read(mealPlanServiceProvider).logMeal(meal.id);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Logged ${meal.title}!')),
                          );
                        },
                        onSwap: () {},
                        onTap: () {},
                      ),
                    ),
                  ),
                
                const SizedBox(height: 80), // Padding for FAB
              ],
            ),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/camera'),
        backgroundColor: NutriColors.primary,
        child: const Icon(Icons.camera_alt, color: Colors.white),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        selectedItemColor: NutriColors.primary,
        unselectedItemColor: NutriColors.inkMuted,
        showSelectedLabels: false,
        showUnselectedLabels: false,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), activeIcon: Icon(Icons.dashboard), label: 'Today'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_month_outlined), activeIcon: Icon(Icons.calendar_month), label: 'Plan'),
          BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline), activeIcon: Icon(Icons.chat_bubble), label: 'Chat'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), activeIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }

  Widget _buildMacroBar(String label, int current, int max, Color color) {
    final double pct = (current / max).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: NutriTypography.dataMd.copyWith(color: NutriColors.ink, fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Text('$current / ${max}g', style: NutriTypography.dataSm),
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
