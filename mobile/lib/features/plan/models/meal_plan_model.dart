class MealItem {
  final String id;
  final String title;
  final String mealType;
  final String? imageUrl;
  final int calories;
  final int protein;
  final int carbs;
  final int fat;
  final bool isLogged;

  const MealItem({
    required this.id,
    required this.title,
    required this.mealType,
    this.imageUrl,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
    this.isLogged = false,
  });

  factory MealItem.fromJson(Map<String, dynamic> json) {
    return MealItem(
      id: json['id']?.toString() ?? json['recipe_id']?.toString() ?? '1',
      title: json['name'] ?? json['title'] ?? 'Meal',
      mealType: json['meal_type'] ?? json['type'] ?? 'Lunch',
      imageUrl: json['image_url'] ?? json['image'],
      calories: (json['calories_kcal'] ?? json['calories'] ?? 350).toInt(),
      protein: (json['protein_g'] ?? json['protein'] ?? 15).toInt(),
      carbs: (json['carbs_g'] ?? json['carbs'] ?? 40).toInt(),
      fat: (json['fat_g'] ?? json['fat'] ?? 10).toInt(),
      isLogged: json['is_logged'] ?? false,
    );
  }
}

class DailyMacroSummary {
  final int caloriesEaten;
  final int targetCalories;
  final int proteinG;
  final int targetProteinG;
  final int carbsG;
  final int targetCarbsG;
  final int fatG;
  final int targetFatG;
  final List<MealItem> meals;

  const DailyMacroSummary({
    required this.caloriesEaten,
    required this.targetCalories,
    required this.proteinG,
    required this.targetProteinG,
    required this.carbsG,
    required this.targetCarbsG,
    required this.fatG,
    required this.targetFatG,
    required this.meals,
  });

  factory DailyMacroSummary.initial() {
    return const DailyMacroSummary(
      caloriesEaten: 1250,
      targetCalories: 2000,
      proteinG: 75,
      targetProteinG: 120,
      carbsG: 140,
      targetCarbsG: 220,
      fatG: 45,
      targetFatG: 65,
      meals: [],
    );
  }
}
