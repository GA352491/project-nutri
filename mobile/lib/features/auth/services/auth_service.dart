import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();

  Future<UserModel> login({required String email, required String password}) async {
    try {
      final response = await _apiClient.dio.post(
        '${ApiEndpoints.authBaseUrl}/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      final token = response.data['access_token'];
      if (token != null) {
        await _apiClient.saveToken(token);
      }

      // Fetch user profile info
      return await getCurrentUser();
    } on DioException catch (e) {
      final message = e.response?.data['detail'] ?? 'Login failed. Please check your credentials.';
      throw Exception(message);
    }
  }

  Future<UserModel> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '${ApiEndpoints.authBaseUrl}/register',
        data: {
          'email': email,
          'password': password,
          'full_name': fullName,
        },
      );

      final token = response.data['access_token'];
      if (token != null) {
        await _apiClient.saveToken(token);
      }

      return UserModel.fromJson(response.data['user'] ?? {
        'email': email,
        'name': fullName,
        'role': 'patient',
      });
    } on DioException catch (e) {
      final message = e.response?.data['detail'] ?? 'Registration failed.';
      throw Exception(message);
    }
  }

  Future<UserModel> getCurrentUser() async {
    try {
      final response = await _apiClient.dio.get('${ApiEndpoints.authBaseUrl}/me');
      return UserModel.fromJson(response.data);
    } catch (_) {
      // Fallback demo user if running in offline mode
      return const UserModel(
        id: 'usr_local_1',
        email: 'user@nutriplan.local',
        name: 'Demo Patient',
        role: 'patient',
        hasCompletedOnboarding: true,
      );
    }
  }

  Future<void> logout() async {
    await _apiClient.clearToken();
  }
}
