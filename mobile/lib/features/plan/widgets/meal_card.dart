import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../shared/widgets/chip.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';

class NutriMealCard extends StatelessWidget {
  final String id;
  final String title;
  final String imageUrl;
  final int calories;
  final int protein;
  final int carbs;
  final int fat;
  final bool isLogged;
  final String statusLabel; // e.g., 'Breakfast', 'Lunch'
  final VoidCallback onLog;
  final VoidCallback? onUnlog;
  final VoidCallback onSwap;
  final VoidCallback onTap;
  final bool highGlycemic; // CGM Spike Radar flag

  const NutriMealCard({
    super.key,
    required this.id,
    required this.title,
    required this.imageUrl,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.isLogged,
    required this.statusLabel,
    required this.onLog,
    this.onUnlog,
    required this.onSwap,
    required this.onTap,
    this.highGlycemic = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: NutriColors.canvasRaised,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: NutriColors.border),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.02),
              blurRadius: 10,
              offset: const Offset(0, 4),
            )
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image header
            SizedBox(
              height: 140,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  CachedNetworkImage(
                    imageUrl: imageUrl,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Container(color: NutriColors.border),
                    errorWidget: (context, url, error) => Container(color: NutriColors.border, child: const Icon(Icons.broken_image, color: NutriColors.inkMuted)),
                  ),
                  Positioned(
                    top: 12,
                    left: 12,
                    child: NutriChip(
                      label: statusLabel,
                      variant: isLogged ? NutriChipVariant.info : NutriChipVariant.secondary,
                    ),
                  ),
                  if (isLogged)
                    Positioned(
                      top: 12,
                      right: 12,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: NutriColors.success,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.check, color: Colors.white, size: 16),
                      ),
                    ),
                ],
              ),
            ),
            
            // Content
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: NutriTypography.displaySm,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  
                  // Macros
                  Row(
                    children: [
                      _buildMacro(calories.toString(), 'kcal'),
                      _buildDivider(),
                      _buildMacro(protein.toString(), 'P', color: MacroColors.protein),
                      _buildDivider(),
                      _buildMacro(carbs.toString(), 'C', color: MacroColors.carbs),
                      _buildDivider(),
                      _buildMacro(fat.toString(), 'F', color: MacroColors.fat),
                    ],
                  ),
                  const SizedBox(height: 6),

                  // CGM Spike Radar chip
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: highGlycemic
                          ? const Color(0xFFFFF3E0)
                          : const Color(0xFFE8F5E9),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: highGlycemic
                            ? const Color(0xFFFFA726)
                            : const Color(0xFF66BB6A),
                        width: 1,
                      ),
                    ),
                    child: Text(
                      highGlycemic
                          ? '\uD83E\uDE78 CGM GI 55+ · Eat Salad 1st'
                          : '\uD83E\uDE78 CGM Stable',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: highGlycemic
                            ? const Color(0xFFE65100)
                            : const Color(0xFF2E7D32),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Actions
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: isLogged ? null : onSwap,
                          child: const Text('Swap'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: isLogged
                            ? OutlinedButton.icon(
                                onPressed: onUnlog,
                                icon: const Icon(Icons.check_circle_rounded,
                                    color: NutriColors.success, size: 16),
                                label: const Text('Logged',
                                    style: TextStyle(
                                        color: NutriColors.success,
                                        fontWeight: FontWeight.bold)),
                                style: OutlinedButton.styleFrom(
                                  side: const BorderSide(
                                      color: NutriColors.success),
                                ),
                              )
                            : ElevatedButton(
                                onPressed: onLog,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: NutriColors.primary,
                                ),
                                child: const Text('Log Meal'),
                              ),
                      ),
                    ],
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildMacro(String value, String label, {Color? color}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          value,
          style: NutriTypography.dataMd.copyWith(color: NutriColors.ink, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: NutriTypography.dataMd.copyWith(color: color ?? NutriColors.inkMuted),
        ),
      ],
    );
  }

  Widget _buildDivider() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 6),
      child: Text('·', style: TextStyle(color: NutriColors.border, fontSize: 16)),
    );
  }
}
