import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';

class MacroRing extends StatelessWidget {
  final double calories;
  final double maxCalories;
  final double size;
  final double strokeWidth;

  const MacroRing({
    super.key,
    required this.calories,
    required this.maxCalories,
    this.size = 120,
    this.strokeWidth = 12,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = (calories / maxCalories).clamp(0.0, 1.0);
    final remaining = 1.0 - percentage;

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          PieChart(
            PieChartData(
              sectionsSpace: 0,
              centerSpaceRadius: (size / 2) - strokeWidth,
              startDegreeOffset: -90,
              sections: [
                PieChartSectionData(
                  color: NutriColors.primary,
                  value: percentage * 100,
                  title: '',
                  radius: strokeWidth,
                ),
                PieChartSectionData(
                  color: NutriColors.border,
                  value: remaining * 100,
                  title: '',
                  radius: strokeWidth,
                ),
              ],
            ),
            swapAnimationDuration: const Duration(milliseconds: 800),
            swapAnimationCurve: Curves.easeInOut,
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                calories.toInt().toString(),
                style: NutriTypography.displayLg.copyWith(
                  height: 1.0,
                  letterSpacing: -1,
                ),
              ),
              Text(
                'kcal',
                style: NutriTypography.dataSm.copyWith(
                  color: NutriColors.inkMuted,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
