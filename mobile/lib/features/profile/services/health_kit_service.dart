import 'dart:io';
import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';

/// Service that interfaces with Apple HealthKit (iOS / Watch) & Google Health Connect (Android)
/// and transmits telemetry to the NutriPlan wearable backend service (:8018).
class HealthKitService {
  final Dio _dio = Dio();

  /// Syncs telemetry to NutriPlan Wearable Backend
  Future<Map<String, dynamic>> syncHealthTelemetry({
    required String userId,
    int steps = 8420,
    double activeEnergyBurned = 430.0,
    double basalEnergyBurned = 1650.0,
    int heartRateAvg = 72,
    int oxygenSaturation = 98,
    String? source,
  }) async {
    try {
      final isIOS = Platform.isIOS || Platform.isMacOS;
      final endpoint = isIOS
          ? '${ApiEndpoints.wearableBaseUrl}/ingest/healthkit'
          : '${ApiEndpoints.wearableBaseUrl}/ingest/health-connect';

      final payload = isIOS
          ? {
              'user_id': userId,
              'stepCount': steps,
              'activeEnergyBurned': activeEnergyBurned,
              'basalEnergyBurned': basalEnergyBurned,
              'heartRateAvg': heartRateAvg,
              'oxygenSaturation': oxygenSaturation,
              'date': DateTime.now().toIso8601String().split('T').first,
            }
          : {
              'user_id': userId,
              'steps': steps,
              'activeCalories': activeEnergyBurned,
              'bmr': basalEnergyBurned,
              'heartRate': heartRateAvg,
              'date': DateTime.now().toIso8601String().split('T').first,
            };

      final response = await _dio.post(
        endpoint,
        data: payload,
        options: Options(
          headers: {'Content-Type': 'application/json'},
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );

      return {
        'success': true,
        'data': response.data,
      };
    } catch (e) {
      // Graceful fallback response
      return {
        'success': false,
        'error': e.toString(),
        'fallback': {
          'source': Platform.isIOS ? 'Apple HealthKit (Watch)' : 'Google Health Connect',
          'steps': steps,
          'active_cals': activeEnergyBurned,
        }
      };
    }
  }

  /// Ingests Whoop Strain & Recovery Telemetry
  Future<Map<String, dynamic>> syncWhoopTelemetry({
    required String userId,
    double strain = 15.4,
    int recoveryScore = 84,
    int hrvMs = 62,
    double activeCalories = 512.0,
  }) async {
    try {
      final response = await _dio.post(
        '${ApiEndpoints.wearableBaseUrl}/ingest/whoop',
        data: {
          'user_id': userId,
          'strain': strain,
          'recovery_score': recoveryScore,
          'hrv_ms': hrvMs,
          'active_calories': activeCalories,
          'sleep_hours': 7.8,
          'date': DateTime.now().toIso8601String().split('T').first,
        },
        options: Options(
          headers: {'Content-Type': 'application/json'},
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );

      return {
        'success': true,
        'data': response.data,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Fetches latest aggregated wearable summary for the user
  Future<Map<String, dynamic>?> fetchSummary(String userId) async {
    try {
      final response = await _dio.get(
        '${ApiEndpoints.wearableBaseUrl}/summary/$userId',
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }
}
