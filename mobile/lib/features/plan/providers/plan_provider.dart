import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/meal_plan_model.dart';
import '../services/meal_plan_service.dart';

final mealPlanServiceProvider = Provider<MealPlanService>((ref) => MealPlanService());

final todayPlanProvider = FutureProvider<DailyMacroSummary>((ref) async {
  final service = ref.watch(mealPlanServiceProvider);
  return await service.getTodayPlanAndMacros();
});
