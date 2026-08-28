import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../models/meal_plan_model.dart';

class MealPlanService {
  final ApiClient _apiClient = ApiClient();

  Future<DailyMacroSummary> getTodayPlanAndMacros() async {
    try {
      final response = await _apiClient.dio.get('${ApiEndpoints.planBaseUrl}/today');
      final data = response.data;
      final mealsJson = (data['meals'] as List?) ?? [];
      final meals = mealsJson.map((m) => MealItem.fromJson(m)).toList();

      return DailyMacroSummary(
        caloriesEaten: (data['calories_eaten'] ?? 1150).toInt(),
        targetCalories: (data['target_calories'] ?? 2000).toInt(),
        proteinG: (data['protein_g'] ?? 68).toInt(),
        targetProteinG: (data['target_protein_g'] ?? 120).toInt(),
        carbsG: (data['carbs_g'] ?? 135).toInt(),
        targetCarbsG: (data['target_carbs_g'] ?? 220).toInt(),
        fatG: (data['fat_g'] ?? 42).toInt(),
        targetFatG: (data['target_fat_g'] ?? 65).toInt(),
        meals: meals,
      );
    } catch (_) {
      // Fallback data if backend is still starting
      return const DailyMacroSummary(
        caloriesEaten: 1350,
        targetCalories: 2000,
        proteinG: 82,
        targetProteinG: 120,
        carbsG: 145,
        targetCarbsG: 220,
        fatG: 48,
        targetFatG: 65,
        meals: [
          MealItem(
            id: '1',
            title: 'Moong Dal Chilla with Mint Chutney',
            mealType: 'Breakfast',
            imageUrl: 'https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&q=80',
            calories: 320,
            protein: 14,
            carbs: 45,
            fat: 8,
            isLogged: true,
          ),
          MealItem(
            id: '2',
            title: 'Palak Paneer with Brown Rice',
            mealType: 'Lunch',
            imageUrl: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80',
            calories: 450,
            protein: 22,
            carbs: 42,
            fat: 16,
            isLogged: false,
          ),
          MealItem(
            id: '3',
            title: 'Spiced Chickpea & Cucumber Bowl',
            mealType: 'Dinner',
            imageUrl: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80',
            calories: 380,
            protein: 18,
            carbs: 48,
            fat: 12,
            isLogged: false,
          ),
        ],
      );
    }
  }

  Future<void> logMeal(String mealId) async {
    try {
      await _apiClient.dio.post('${ApiEndpoints.diaryBaseUrl}/log', data: {'meal_id': mealId});
    } catch (_) {}
  }
}
