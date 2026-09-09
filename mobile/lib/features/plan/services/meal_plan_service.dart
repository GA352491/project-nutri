import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../models/meal_plan_model.dart';

class MealPlanService {
  final ApiClient _apiClient = ApiClient();

  Future<DailyMacroSummary> getTodayPlanAndMacros() async {
    try {
      final todayStr = DateTime.now().toIso8601String().split('T').first;

      // Fetch plan and diary independently — either can fail without breaking the other
      dynamic planResp;
      dynamic diaryResp;
      try {
        planResp = await _apiClient.dio.get('${ApiEndpoints.planBaseUrl}/today');
      } catch (_) {
        planResp = null;
      }
      try {
        diaryResp = await _apiClient.dio.get('${ApiEndpoints.diaryBaseUrl}/day/$todayStr');
      } catch (_) {
        diaryResp = null;
      }

      final planData = (planResp?.data ?? {}) as Map<String, dynamic>;
      final diaryData = (diaryResp?.data ?? {}) as Map<String, dynamic>;

      final mealsJson = (planData['meals'] as List?) ?? [];
      final diaryEntries = (diaryData['entries'] as List?) ?? [];

      // Check which meals are currently logged in today's diary
      final meals = mealsJson.map((m) {
        final mealItem = MealItem.fromJson(m);
        // Find matching entry in diary
        final match = diaryEntries.firstWhere(
          (e) =>
              (e['food_name'] != null &&
                  e['food_name'].toString().toLowerCase().trim() ==
                      mealItem.title.toLowerCase().trim()) ||
              (e['recipe_id'] != null &&
                  e['recipe_id'].toString() == mealItem.id),
          orElse: () => null,
        );

        if (match != null) {
          return mealItem.copyWith(
            isLogged: true,
            loggedEntryId: match['id']?.toString(),
          );
        }
        return mealItem;
      }).toList();

      // ── Compute eaten macros by summing ONLY logged meal items ──────────
      // We intentionally do NOT use planData['calories_eaten'] because the backend
      // hardcodes it to 40% of target as a dummy estimate. We also prefer
      // diary totals if available, but fall back to summing logged meals so that
      // the chart always reflects the user's actual logged state.
      final loggedMeals = meals.where((m) => m.isLogged).toList();

      int actualCaloriesEaten;
      int actualProtein;
      int actualCarbs;
      int actualFat;

      final diaryTotalCal = diaryData['total_calories'];
      if (diaryTotalCal != null) {
        // Diary service returned valid totals — use them directly
        actualCaloriesEaten = (diaryTotalCal as num).toInt();
        actualProtein = (diaryData['total_protein_g'] as num? ?? 0).toInt();
        actualCarbs = (diaryData['total_carbs_g'] as num? ?? 0).toInt();
        actualFat = (diaryData['total_fat_g'] as num? ?? 0).toInt();
      } else {
        // Diary unavailable (auth error or no entries) — sum from logged meal items
        actualCaloriesEaten = loggedMeals.fold(0, (sum, m) => sum + m.calories);
        actualProtein = loggedMeals.fold(0, (sum, m) => sum + m.protein);
        actualCarbs = loggedMeals.fold(0, (sum, m) => sum + m.carbs);
        actualFat = loggedMeals.fold(0, (sum, m) => sum + m.fat);
      }

      final targetCalories = (planData['target_calories'] as num?)?.toInt() ?? 2000;
      final targetProtein = (planData['target_protein_g'] as num?)?.toInt() ?? 120;
      final targetCarbs = (planData['target_carbs_g'] as num?)?.toInt() ?? 220;
      final targetFat = (planData['target_fat_g'] as num?)?.toInt() ?? 65;

      return DailyMacroSummary(
        caloriesEaten: actualCaloriesEaten,
        targetCalories: targetCalories,
        proteinG: actualProtein,
        targetProteinG: targetProtein,
        carbsG: actualCarbs,
        targetCarbsG: targetCarbs,
        fatG: actualFat,
        targetFatG: targetFat,
        meals: meals,
      );
    } catch (e) {
      // Plan backend unavailable — return zero-eaten state so chart shows 0.
      // Do NOT return hardcoded macro values as they mislead users.
      rethrow;
    }
  }

  Future<MealItem?> swapMeal({
    required String currentMealName,
    required String mealType,
    String regionId = 'in_south_andhra',
    double targetCalories = 450.0,
    String dietaryFlag = 'vegetarian',
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '${ApiEndpoints.planBaseUrl}/swap-meal',
        data: {
          'current_meal_name': currentMealName,
          'meal_type': mealType.toLowerCase(),
          'region_id': regionId,
          'caloric_target_kcal': targetCalories,
          'dietary_flag': dietaryFlag,
        },
      );
      final repl = response.data['replacement'];
      if (repl != null) {
        return MealItem.fromJson(repl);
      }
    } catch (_) {}
    return null;
  }

  Future<String?> logMeal(
    String mealId, {
    String? mealName,
    int calories = 400,
    int protein = 20,
    int carbs = 50,
    int fat = 12,
    String mealType = 'lunch',
  }) async {
    try {
      final todayStr = DateTime.now().toIso8601String().split('T').first;
      final response = await _apiClient.dio.post(
        '${ApiEndpoints.diaryBaseUrl}/entries',
        data: {
          'log_date': todayStr,
          'meal_type': mealType.toLowerCase(),
          'food_name': mealName ?? mealId,
          'quantity_g': 200.0,
          'calories': calories.toDouble(),
          'protein_g': protein.toDouble(),
          'carbs_g': carbs.toDouble(),
          'fat_g': fat.toDouble(),
          'fiber_g': 5.0,
          'recipe_id': mealId,
          'source': 'meal_plan',
          'notes': 'Logged from daily meal plan',
        },
      );
      if (response.data != null && response.data['id'] != null) {
        return response.data['id'].toString();
      }
    } catch (_) {}
    return null;
  }

  Future<bool> unlogMeal(String entryId) async {
    try {
      final response = await _apiClient.dio.delete(
        '${ApiEndpoints.diaryBaseUrl}/entries/$entryId',
      );
      return response.statusCode == 200 || response.statusCode == 204;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> getRecipeDetail(String recipeId) async {
    try {
      final response = await _apiClient.dio.get(
        '${ApiEndpoints.recipeBaseUrl}/$recipeId',
      );
      if (response.data is Map<String, dynamic>) {
        return response.data;
      }
    } catch (_) {}
    return null;
  }
}
