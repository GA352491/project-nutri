import 'dart:io';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/button.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../diary/services/diary_service.dart';
import '../services/food_recognition_service.dart';

class CameraCaptureScreen extends StatefulWidget {
  const CameraCaptureScreen({super.key});

  @override
  State<CameraCaptureScreen> createState() => _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends State<CameraCaptureScreen> {
  bool _isProcessing = false;
  final FoodRecognitionService _visionService = FoodRecognitionService();

  void _simulateCapture() async {
    setState(() => _isProcessing = true);
    // On a real device, use image_picker to get a real File.
    // In simulator mode the service returns its offline-fallback result.
    final result = await _visionService.analyzePhoto(
      // Pass a dummy non-existent File — service falls back to curated result gracefully
      File('/tmp/nutriplan_capture.jpg'),
    );
    setState(() => _isProcessing = false);
    if (mounted) {
      _showBottomSheet(result);
    }
  }

  void _showBottomSheet(FoodRecognitionResult result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _NutritionResultSheet(result: result),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Simulated Camera Preview
          Container(
            color: Colors.black,
            child: Center(
              child: Image.network(
                'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=800',
                fit: BoxFit.cover,
                height: double.infinity,
                width: double.infinity,
              ),
            ),
          ),
          
          // UI Overlay
          SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Top Bar
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white),
                        onPressed: () => context.pop(),
                      ),
                      const Icon(Icons.flash_off, color: Colors.white),
                    ],
                  ),
                ),
                
                // Bottom Bar
                Padding(
                  padding: const EdgeInsets.all(32.0),
                  child: Column(
                    children: [
                      if (_isProcessing)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.7),
                            borderRadius: BorderRadius.circular(30),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const SizedBox(
                                height: 16,
                                width: 16,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              ),
                              const SizedBox(width: 12),
                              Text('AI Vision analyzing food...', style: NutriTypography.bodyMd.copyWith(color: Colors.white)),
                            ],
                          ),
                        ),
                      const SizedBox(height: 24),
                      GestureDetector(
                        onTap: _isProcessing ? null : _simulateCapture,
                        child: Container(
                          height: 80,
                          width: 80,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 4),
                          ),
                          child: Center(
                            child: Container(
                              height: 64,
                              width: 64,
                              decoration: const BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NutritionResultSheet extends StatelessWidget {
  final FoodRecognitionResult result;
  const _NutritionResultSheet({required this.result});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(24),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 24),
                decoration: BoxDecoration(
                  color: NutriColors.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('AI Vision Detected', style: NutriTypography.dataSm),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: NutriColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${(result.confidence * 100).toInt()}% Match',
                    style: NutriTypography.dataSm.copyWith(color: NutriColors.primary, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(result.foodName, style: NutriTypography.displayMd),
            Text(result.portionEstimate, style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted)),
            const SizedBox(height: 24),
            
            // Macros
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildMacroStat('${result.estimatedCalories}', 'kcal', NutriColors.ink),
                _buildMacroStat('${result.proteinG}g', 'Protein', MacroColors.protein),
                _buildMacroStat('${result.carbsG}g', 'Carbs', MacroColors.carbs),
                _buildMacroStat('${result.fatG}g', 'Fat', MacroColors.fat),
              ],
            ),
            const SizedBox(height: 32),
            
            Row(
              children: [
                Expanded(
                  child: NutriButton(
                    text: 'Retake',
                    variant: ButtonVariant.outline,
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: NutriButton(
                    text: '⚡ Add to Diary',
                    onPressed: () async {
                      Navigator.pop(context); // Close sheet
                      context.pop(); // Close camera back to Today

                      final diaryService = DiaryService();
                      await diaryService.logRecognizedFood(result);

                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            backgroundColor: NutriColors.primary,
                            content: Row(
                              children: [
                                const Icon(Icons.check_circle_rounded, color: Colors.white, size: 20),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    'Logged ${result.foodName} (+${result.estimatedCalories} kcal, ${result.proteinG}g P)!',
                                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                                  ),
                                ),
                              ],
                            ),
                            duration: const Duration(seconds: 3),
                          ),
                        );
                      }
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMacroStat(String value, String label, Color color) {
    return Column(
      children: [
        Text(value, style: NutriTypography.displaySm.copyWith(color: color)),
        const SizedBox(height: 4),
        Text(label, style: NutriTypography.dataMd.copyWith(color: NutriColors.inkMuted)),
      ],
    );
  }
}
