import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../models/meal_plan_model.dart';
import '../services/meal_plan_service.dart';

class MealDetailBottomSheet extends StatefulWidget {
  final MealItem meal;
  final MealPlanService mealPlanService;
  final Function(String? loggedEntryId) onLogToggled;

  const MealDetailBottomSheet({
    super.key,
    required this.meal,
    required this.mealPlanService,
    required this.onLogToggled,
  });

  @override
  State<MealDetailBottomSheet> createState() => _MealDetailBottomSheetState();
}

class _MealDetailBottomSheetState extends State<MealDetailBottomSheet> {
  late bool _isLogged;
  String? _entryId;
  bool _isLoading = false;
  bool _isFetchingRecipe = true;
  List<String> _ingredients = [];
  List<String> _instructions = [];

  @override
  void initState() {
    super.initState();
    _isLogged = widget.meal.isLogged;
    _entryId = widget.meal.loggedEntryId;
    _ingredients = List.from(widget.meal.ingredients);
    _instructions = List.from(widget.meal.instructions);
    _loadRecipeDetails();
  }

  Future<void> _loadRecipeDetails() async {
    try {
      final recipeData = await widget.mealPlanService.getRecipeDetail(widget.meal.id);
      if (recipeData != null && mounted) {
        final List<String> fetchedIngredients = [];
        if (recipeData['ingredients'] is List) {
          for (var ing in recipeData['ingredients']) {
            if (ing is String) {
              fetchedIngredients.add(ing);
            } else if (ing is Map) {
              final name = ing['name'] ?? '';
              final qty = ing['quantity'] ?? ing['amount'] ?? '';
              final unit = ing['unit'] ?? '';
              fetchedIngredients.add('$qty $unit $name'.trim());
            }
          }
        }

        final List<String> fetchedInstructions = [];
        if (recipeData['instructions'] is List) {
          for (var ins in recipeData['instructions']) {
            fetchedInstructions.add(ins.toString());
          }
        }

        setState(() {
          if (fetchedIngredients.isNotEmpty) _ingredients = fetchedIngredients;
          if (fetchedInstructions.isNotEmpty) _instructions = fetchedInstructions;
        });
      }
    } catch (_) {
      // Fallback already assigned
    } finally {
      if (mounted) {
        setState(() => _isFetchingRecipe = false);
      }
    }
  }

  Future<void> _toggleLog() async {
    setState(() => _isLoading = true);
    if (!_isLogged) {
      final newId = await widget.mealPlanService.logMeal(
        widget.meal.id,
        mealName: widget.meal.title,
        calories: widget.meal.calories,
        protein: widget.meal.protein,
        carbs: widget.meal.carbs,
        fat: widget.meal.fat,
        mealType: widget.meal.mealType,
      );
      if (mounted) {
        setState(() {
          _isLogged = true;
          _entryId = newId;
          _isLoading = false;
        });
        widget.onLogToggled(newId);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: NutriColors.success,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            content: Text('Logged "${widget.meal.title}" to your Food Diary!'),
          ),
        );
      }
    } else {
      if (_entryId != null && _entryId!.isNotEmpty) {
        await widget.mealPlanService.unlogMeal(_entryId!);
      }
      if (mounted) {
        setState(() {
          _isLogged = false;
          _entryId = null;
          _isLoading = false;
        });
        widget.onLogToggled(null);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: NutriColors.danger,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            content: Text('Removed "${widget.meal.title}" from your Food Diary.'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final meal = widget.meal;

    return DraggableScrollableSheet(
      initialChildSize: 0.88,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      builder: (_, scrollController) => Container(
        decoration: const BoxDecoration(
          color: NutriColors.canvasRaised,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: NutriColors.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),

            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                children: [
                  // Hero Image
                  ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Stack(
                      children: [
                        SizedBox(
                          height: 200,
                          width: double.infinity,
                          child: CachedNetworkImage(
                            imageUrl: meal.imageUrl ??
                                'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80',
                            fit: BoxFit.cover,
                            placeholder: (_, __) => Container(color: NutriColors.border),
                            errorWidget: (_, __, ___) => Container(
                              color: NutriColors.border,
                              child: const Icon(Icons.broken_image, color: NutriColors.inkMuted),
                            ),
                          ),
                        ),
                        Positioned(
                          top: 12,
                          left: 12,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: NutriColors.primary,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              meal.mealType.toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                        if (_isLogged)
                          Positioned(
                            top: 12,
                            right: 12,
                            child: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: const BoxDecoration(
                                color: NutriColors.success,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.check, color: Colors.white, size: 16),
                            ),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Title
                  Text(
                    meal.title,
                    style: NutriTypography.displayMd.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),

                  // Tags / Regional indicator
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: NutriColors.primary.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'ICMR-NIN Regional Gold Standard',
                          style: TextStyle(
                            color: NutriColors.primary,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.green.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'Vegetarian',
                          style: TextStyle(
                            color: Colors.green,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Nutrition Facts Card
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: NutriColors.canvas,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: NutriColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'NUTRITION FACTS (Per Serving)',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                            color: NutriColors.inkMuted,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            _MacroItem(
                              label: 'Calories',
                              value: '${meal.calories}',
                              unit: 'kcal',
                              color: NutriColors.ink,
                            ),
                            _MacroItem(
                              label: 'Protein',
                              value: '${meal.protein}',
                              unit: 'g',
                              color: MacroColors.protein,
                            ),
                            _MacroItem(
                              label: 'Carbs',
                              value: '${meal.carbs}',
                              unit: 'g',
                              color: MacroColors.carbs,
                            ),
                            _MacroItem(
                              label: 'Fat',
                              value: '${meal.fat}',
                              unit: 'g',
                              color: MacroColors.fat,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Ingredients Section
                  Text(
                    'Ingredients',
                    style: NutriTypography.displaySm.copyWith(fontWeight: FontWeight.bold),
                  ),
                  if (_isFetchingRecipe)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8),
                      child: SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: NutriColors.primary,
                        ),
                      ),
                    )
                  else if (_ingredients.isEmpty)
                    const Text(
                      '• Whole grains, legumes, cold-pressed oil, regional herbs & spices',
                      style: TextStyle(color: NutriColors.inkMuted, fontSize: 13),
                    )
                  else
                    ..._ingredients.map(
                      (item) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('🥗 ', style: TextStyle(fontSize: 14)),
                            Expanded(
                              child: Text(
                                item,
                                style: NutriTypography.bodyMd.copyWith(color: NutriColors.ink),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  const SizedBox(height: 20),

                  // Step-by-Step Instructions
                  Text(
                    'Preparation Instructions',
                    style: NutriTypography.displaySm.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  if (_instructions.isEmpty)
                    const Text(
                      '1. Rinse ingredients thoroughly.\n2. Cook grains and lentils with fresh tempering.\n3. Serve hot with traditional accompaniments.',
                      style: TextStyle(color: NutriColors.inkMuted, fontSize: 13, height: 1.5),
                    )
                  else
                    ..._instructions.asMap().entries.map(
                      (entry) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 24,
                              height: 24,
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: NutriColors.primary.withValues(alpha: 0.12),
                                shape: BoxShape.circle,
                              ),
                              child: Text(
                                '${entry.key + 1}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: NutriColors.primary,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                entry.value,
                                style: NutriTypography.bodyMd.copyWith(color: NutriColors.ink, height: 1.4),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  const SizedBox(height: 32),
                ],
              ),
            ),

            // Bottom Action Bar
            Container(
              padding: const EdgeInsets.all(16),
              decoration: const BoxDecoration(
                color: NutriColors.canvasRaised,
                border: Border(top: BorderSide(color: NutriColors.border)),
              ),
              child: SafeArea(
                child: SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: _isLogged
                      ? OutlinedButton.icon(
                          onPressed: _isLoading ? null : _toggleLog,
                          icon: _isLoading
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.remove_circle_outline_rounded,
                                  color: NutriColors.danger),
                          label: Text(
                            _isLoading ? 'Updating...' : 'Un-log this Meal from Diary',
                            style: const TextStyle(
                              color: NutriColors.danger,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: NutriColors.danger, width: 1.5),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                        )
                      : ElevatedButton.icon(
                          onPressed: _isLoading ? null : _toggleLog,
                          icon: _isLoading
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(Icons.check_circle_outline_rounded,
                                  color: Colors.white),
                          label: Text(
                            _isLoading ? 'Logging...' : 'Log this Meal to Food Diary',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: NutriColors.primary,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MacroItem extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final Color color;

  const _MacroItem({
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.baseline,
          textBaseline: TextBaseline.alphabetic,
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(width: 2),
            Text(
              unit,
              style: const TextStyle(
                fontSize: 11,
                color: NutriColors.inkMuted,
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: NutriColors.inkMuted,
          ),
        ),
      ],
    );
  }
}
