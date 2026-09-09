import 'package:dio/dio.dart';
import 'package:intl/intl.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../../photo_log/services/food_recognition_service.dart';

class DiaryService {
  final ApiClient _apiClient = ApiClient();

  /// Logs a food item recognized by the AI Vision Engine to the diary.
  Future<bool> logRecognizedFood(
    FoodRecognitionResult result, {
    String? mealType,
  }) async {
    final resolvedMealType = mealType ?? result.mealTypeGuess;
    final todayStr = DateFormat('yyyy-MM-dd').format(DateTime.now());

    try {
      final payload = {
        'log_date': todayStr,
        'meal_type': resolvedMealType.toLowerCase(),
        'food_name': result.displayFoodName,
        'quantity_g': result.items.fold<double>(0, (s, i) => s + i.portionG),
        'calories': result.totalCalories,
        'protein_g': result.totalProteinG,
        'carbs_g': result.totalCarbsG,
        'fat_g': result.totalFatG,
        'fiber_g': result.items.fold<double>(0, (s, i) => s + i.fiberG),
        'source': 'ai_vision',
        'notes':
            'Logged via NutriPlan AI Vision (${(result.averageConfidence * 100).toInt()}% confidence)',
      };

      final response = await _apiClient.dio.post(
        '${ApiEndpoints.diaryBaseUrl}/entries',
        data: payload,
      );

      return response.statusCode == 200 || response.statusCode == 201;
    } on DioException {
      // Network error — diary logging failure is non-critical (vision result already shown)
      return false;
    }
  }
}
