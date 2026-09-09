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

  final List<String> ingredients;
  final List<String> instructions;
  final String? loggedEntryId;

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
    this.ingredients = const [],
    this.instructions = const [],
    this.loggedEntryId,
  });

  MealItem copyWith({
    String? id,
    String? title,
    String? mealType,
    String? imageUrl,
    int? calories,
    int? protein,
    int? carbs,
    int? fat,
    bool? isLogged,
    List<String>? ingredients,
    List<String>? instructions,
    String? loggedEntryId,
  }) {
    return MealItem(
      id: id ?? this.id,
      title: title ?? this.title,
      mealType: mealType ?? this.mealType,
      imageUrl: imageUrl ?? this.imageUrl,
      calories: calories ?? this.calories,
      protein: protein ?? this.protein,
      carbs: carbs ?? this.carbs,
      fat: fat ?? this.fat,
      isLogged: isLogged ?? this.isLogged,
      ingredients: ingredients ?? this.ingredients,
      instructions: instructions ?? this.instructions,
      loggedEntryId: loggedEntryId ?? this.loggedEntryId,
    );
  }

  factory MealItem.fromJson(Map<String, dynamic> json) {
    List<String> parsedIngredients = [];
    if (json['ingredients'] is List) {
      for (var ing in json['ingredients']) {
        if (ing is String) {
          parsedIngredients.add(ing);
        } else if (ing is Map) {
          final name = ing['name'] ?? '';
          final qty = ing['quantity'] ?? ing['amount'] ?? '';
          final unit = ing['unit'] ?? '';
          parsedIngredients.add('$qty $unit $name'.trim());
        }
      }
    }

    List<String> parsedInstructions = [];
    if (json['instructions'] is List) {
      parsedInstructions = (json['instructions'] as List)
          .map((i) => i.toString())
          .toList();
    }

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
      ingredients: parsedIngredients,
      instructions: parsedInstructions,
      loggedEntryId: json['logged_entry_id']?.toString(),
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
