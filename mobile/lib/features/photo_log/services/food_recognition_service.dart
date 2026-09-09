import 'dart:io';
import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';

/// Represents a single recognized food item from the AI Vision Engine.
class RecognizedFoodItem {
  final String name;
  final double confidence;
  final double portionG;
  final double calories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;
  final String? region;

  const RecognizedFoodItem({
    required this.name,
    required this.confidence,
    required this.portionG,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    this.region,
  });

  factory RecognizedFoodItem.fromJson(Map<String, dynamic> json) {
    return RecognizedFoodItem(
      name: (json['name'] as String? ?? 'Unknown item').trim(),
      confidence: (json['confidence'] as num? ?? 0.0).toDouble(),
      portionG: (json['portion_g'] as num? ?? 0.0).toDouble(),
      calories: (json['calories'] as num? ?? 0.0).toDouble(),
      proteinG: (json['protein_g'] as num? ?? 0.0).toDouble(),
      carbsG: (json['carbs_g'] as num? ?? 0.0).toDouble(),
      fatG: (json['fat_g'] as num? ?? 0.0).toDouble(),
      fiberG: (json['fiber_g'] as num? ?? 0.0).toDouble(),
      region: json['region'] as String?,
    );
  }
}

/// Full meal analysis result returned by the Vision Engine.
class FoodRecognitionResult {
  final String imageId;
  final List<RecognizedFoodItem> items;
  final double totalCalories;
  final double totalProteinG;
  final double totalCarbsG;
  final double totalFatG;
  final String mealTypeGuess;
  final List<String> complianceWarnings;

  const FoodRecognitionResult({
    required this.imageId,
    required this.items,
    required this.totalCalories,
    required this.totalProteinG,
    required this.totalCarbsG,
    required this.totalFatG,
    required this.mealTypeGuess,
    required this.complianceWarnings,
  });

  /// Combined display name of all identified food items.
  String get displayFoodName {
    if (items.isEmpty) return 'Unidentified Meal';
    return items.map((i) => i.name).join(' + ');
  }

  /// Portion display string (total weight across items).
  String get portionDisplay {
    final totalG = items.fold<double>(0, (sum, i) => sum + i.portionG);
    return totalG > 0 ? '~${totalG.toStringAsFixed(0)}g serving' : 'Estimated portion';
  }

  /// Average confidence across all items (0.0 – 1.0).
  double get averageConfidence {
    if (items.isEmpty) return 0.0;
    return items.fold<double>(0, (sum, i) => sum + i.confidence) / items.length;
  }

  factory FoodRecognitionResult.fromJson(Map<String, dynamic> json) {
    final rawItems = (json['items'] as List<dynamic>? ?? []);
    final items = rawItems
        .whereType<Map<String, dynamic>>()
        .map((i) => RecognizedFoodItem.fromJson(i))
        .toList();

    return FoodRecognitionResult(
      imageId: json['image_id'] as String? ?? '',
      items: items,
      totalCalories: (json['total_calories'] as num? ?? 0.0).toDouble(),
      totalProteinG: (json['total_protein_g'] as num? ?? 0.0).toDouble(),
      totalCarbsG: (json['total_carbs_g'] as num? ?? 0.0).toDouble(),
      totalFatG: (json['total_fat_g'] as num? ?? 0.0).toDouble(),
      mealTypeGuess: json['meal_type_guess'] as String? ?? 'meal',
      complianceWarnings: (json['compliance_warnings'] as List<dynamic>? ?? [])
          .whereType<String>()
          .toList(),
    );
  }
}

/// Exceptions thrown by [FoodRecognitionService].
class FoodRecognitionException implements Exception {
  final String message;
  final int? statusCode;
  const FoodRecognitionException(this.message, {this.statusCode});

  @override
  String toString() => 'FoodRecognitionException: $message';
}

/// Communicates with the NutriPlan Vision Engine backend.
/// Endpoint: POST /api/v1/food-recognition/analyze (multipart form data)
class FoodRecognitionService {
  final ApiClient _apiClient = ApiClient();

  /// Analyzes a food image file via the live Vision Engine.
  ///
  /// Throws [FoodRecognitionException] on error — no silent fallbacks.
  Future<FoodRecognitionResult> analyzePhoto(
    File imageFile, {
    String userRegion = 'india',
    bool autoLog = false,
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        imageFile.path,
        filename: 'meal_photo.jpg',
        contentType: DioMediaType('image', 'jpeg'),
      ),
      'user_region': userRegion,
      'auto_log': autoLog.toString(),
    });

    try {
      final response = await _apiClient.dio.post(
        '${ApiEndpoints.visionBaseUrl}/analyze',
        data: formData,
        options: Options(
          headers: {'Content-Type': 'multipart/form-data'},
          receiveTimeout: const Duration(seconds: 60), // LLaVA can be slow
          sendTimeout: const Duration(seconds: 30),
        ),
      );

      if (response.statusCode == null ||
          response.statusCode! < 200 ||
          response.statusCode! >= 300) {
        throw FoodRecognitionException(
          'Server returned status ${response.statusCode}',
          statusCode: response.statusCode,
        );
      }

      final data = response.data;
      if (data is! Map<String, dynamic>) {
        throw const FoodRecognitionException('Unexpected response format from Vision Engine');
      }

      final result = FoodRecognitionResult.fromJson(data);
      if (result.items.isEmpty) {
        throw const FoodRecognitionException(
          'No food items were detected in the image. Please try a clearer photo.',
        );
      }

      return result;
    } on DioException catch (e) {
      final code = e.response?.statusCode;
      if (code == 415) {
        throw const FoodRecognitionException(
          'Unsupported image format. Please use JPEG or PNG.',
          statusCode: 415,
        );
      }
      if (code == 413) {
        throw const FoodRecognitionException(
          'Image is too large (max 10MB). Please choose a smaller photo.',
          statusCode: 413,
        );
      }
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw const FoodRecognitionException(
          'Vision Engine timed out. The AI model may be loading — please try again in a moment.',
        );
      }
      if (e.type == DioExceptionType.connectionError) {
        throw const FoodRecognitionException(
          'Cannot reach the Vision Engine. Please check your network connection.',
        );
      }
      throw FoodRecognitionException(
        e.message ?? 'Network error while contacting Vision Engine',
      );
    }
  }
}
