import 'dart:io';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../../shared/widgets/button.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../diary/services/diary_service.dart';
import '../services/food_recognition_service.dart';

// ──────────────────────────────────────────────────────────────────────────────
// Main screen
// ──────────────────────────────────────────────────────────────────────────────

class CameraCaptureScreen extends StatefulWidget {
  const CameraCaptureScreen({super.key});

  @override
  State<CameraCaptureScreen> createState() => _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends State<CameraCaptureScreen>
    with TickerProviderStateMixin {
  final _picker = ImagePicker();
  final _visionService = FoodRecognitionService();

  File? _capturedImage;
  bool _isProcessing = false;
  String? _errorMessage;

  late final AnimationController _pulseController;
  late final Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _pulseAnim =
        Tween<double>(begin: 0.95, end: 1.05).animate(_pulseController);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  // ── Capture / pick ──────────────────────────────────────────────────────────

  Future<void> _captureFromCamera() async {
    try {
      final picked = await _picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
        maxWidth: 1280,
        maxHeight: 1280,
      );
      if (picked == null) return;
      await _analyzeFile(File(picked.path));
    } catch (e) {
      _showError('Could not open camera. Please grant camera permission.');
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      final picked = await _picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 1280,
        maxHeight: 1280,
      );
      if (picked == null) return;
      await _analyzeFile(File(picked.path));
    } catch (e) {
      _showError('Could not open gallery. Please grant photo library permission.');
    }
  }

  // ── Analysis ────────────────────────────────────────────────────────────────

  Future<void> _analyzeFile(File imageFile) async {
    setState(() {
      _capturedImage = imageFile;
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final result = await _visionService.analyzePhoto(imageFile);
      if (!mounted) return;
      setState(() => _isProcessing = false);
      _showResultSheet(result);
    } on FoodRecognitionException catch (e) {
      if (!mounted) return;
      setState(() {
        _isProcessing = false;
        _errorMessage = e.message;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isProcessing = false;
        _errorMessage = 'An unexpected error occurred. Please try again.';
      });
    }
  }

  void _retake() {
    setState(() {
      _capturedImage = null;
      _errorMessage = null;
      _isProcessing = false;
    });
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: NutriColors.danger,
        content: Text(message, style: const TextStyle(color: Colors.white)),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  void _showResultSheet(FoodRecognitionResult result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _NutritionResultSheet(
        result: result,
        capturedImage: _capturedImage,
      ),
    ).then((_) {
      // Allow user to retake after dismissing result
      if (mounted) _retake();
    });
  }

  // ── Build ───────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Preview / viewport
            _capturedImage != null
                ? Image.file(_capturedImage!, fit: BoxFit.contain)
                : _buildIdleViewport(),

            // Top nav
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: _buildTopBar(),
            ),

            // Bottom controls
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: _capturedImage != null
                  ? _buildAnalysisControls()
                  : _buildCaptureControls(),
            ),
          ],
        ),
      ),
    );
  }

  // ── Widgets ─────────────────────────────────────────────────────────────────

  Widget _buildIdleViewport() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF0D1117), Color(0xFF161B22)],
        ),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ScaleTransition(
              scale: _pulseAnim,
              child: Container(
                width: 140,
                height: 140,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: NutriColors.primary.withValues(alpha: 0.6),
                    width: 2,
                  ),
                  gradient: RadialGradient(
                    colors: [
                      NutriColors.primary.withValues(alpha: 0.15),
                      Colors.transparent,
                    ],
                  ),
                ),
                child: Icon(
                  Icons.camera_enhance_rounded,
                  size: 64,
                  color: NutriColors.primary.withValues(alpha: 0.8),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'AI Food Vision',
              style: NutriTypography.displayMd.copyWith(color: Colors.white),
            ),
            const SizedBox(height: 8),
            Text(
              'Take a photo or pick from gallery\nto get instant nutritional insights',
              textAlign: TextAlign.center,
              style: NutriTypography.bodySm.copyWith(
                color: Colors.white.withValues(alpha: 0.55),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Row(
        children: [
          IconButton(
            icon: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.5),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 18),
            ),
            onPressed: () => context.pop(),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.black.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.auto_awesome, size: 14, color: NutriColors.primary),
                const SizedBox(width: 6),
                Text(
                  'AI Vision Engine',
                  style: NutriTypography.dataSm.copyWith(color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCaptureControls() {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Colors.transparent, Colors.black.withValues(alpha: 0.9)],
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Shutter row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Gallery pick
              _CircleIconButton(
                icon: Icons.photo_library_rounded,
                label: 'Gallery',
                onTap: _pickFromGallery,
              ),
              // Main shutter
              GestureDetector(
                onTap: _captureFromCamera,
                child: Container(
                  height: 76,
                  width: 76,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 3),
                    boxShadow: [
                      BoxShadow(
                        color: NutriColors.primary.withValues(alpha: 0.4),
                        blurRadius: 20,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: Center(
                    child: Container(
                      height: 62,
                      width: 62,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                ),
              ),
              // Spacer placeholder for symmetry
              const SizedBox(width: 56),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Tap to capture your meal',
            style: NutriTypography.dataSm.copyWith(
              color: Colors.white.withValues(alpha: 0.6),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisControls() {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Colors.transparent, Colors.black.withValues(alpha: 0.95)],
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_isProcessing) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.75),
                borderRadius: BorderRadius.circular(30),
                border: Border.all(
                  color: NutriColors.primary.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(
                      color: NutriColors.primary,
                      strokeWidth: 2,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'AI Vision analyzing your meal…',
                    style: NutriTypography.bodySm.copyWith(color: Colors.white),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
          if (_errorMessage != null) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: NutriColors.danger.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: NutriColors.danger.withValues(alpha: 0.4)),
              ),
              child: Column(
                children: [
                  const Icon(Icons.error_outline_rounded, color: NutriColors.danger, size: 28),
                  const SizedBox(height: 8),
                  Text(
                    _errorMessage!,
                    textAlign: TextAlign.center,
                    style: NutriTypography.bodySm.copyWith(color: Colors.white),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
          if (!_isProcessing)
            Row(
              children: [
                Expanded(
                  child: _OutlineButton(
                    label: 'Retake',
                    icon: Icons.replay_rounded,
                    onTap: _retake,
                  ),
                ),
                if (_errorMessage == null) ...[
                  const SizedBox(width: 12),
                  const Expanded(
                    child: _OutlineButton(
                      label: 'Analyzing…',
                      icon: Icons.auto_awesome,
                      onTap: null,
                      disabled: true,
                    ),
                  ),
                ],
              ],
            ),
        ],
      ),
    );
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Nutrition Result Bottom Sheet
// ──────────────────────────────────────────────────────────────────────────────

class _NutritionResultSheet extends StatefulWidget {
  final FoodRecognitionResult result;
  final File? capturedImage;

  const _NutritionResultSheet({
    required this.result,
    this.capturedImage,
  });

  @override
  State<_NutritionResultSheet> createState() => _NutritionResultSheetState();
}

class _NutritionResultSheetState extends State<_NutritionResultSheet> {
  final _diaryService = DiaryService();
  bool _isLogging = false;
  bool _logged = false;
  String? _logError;

  String _selectedMealType = '';

  @override
  void initState() {
    super.initState();
    _selectedMealType = widget.result.mealTypeGuess;
  }

  Future<void> _addToDiary() async {
    setState(() {
      _isLogging = true;
      _logError = null;
    });

    final success = await _diaryService.logRecognizedFood(
      widget.result,
      mealType: _selectedMealType,
    );

    if (!mounted) return;

    if (success) {
      setState(() {
        _isLogging = false;
        _logged = true;
      });
      await Future.delayed(const Duration(milliseconds: 600));
      if (!mounted) return;
      Navigator.pop(context);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: NutriColors.primary,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            content: Row(
              children: [
                const Icon(Icons.check_circle_rounded, color: Colors.white, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Logged to diary: ${widget.result.displayFoodName} '
                    '(${widget.result.totalCalories.toStringAsFixed(0)} kcal)',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } else {
      setState(() {
        _isLogging = false;
        _logError = 'Could not save to diary. Check your connection and try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final r = widget.result;
    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (_, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: NutriColors.canvasRaised,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.fromLTRB(24, 0, 24, 32),
            children: [
              // Drag handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.symmetric(vertical: 12),
                  decoration: BoxDecoration(
                    color: NutriColors.border,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),

              // Header — confidence badge + label
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'AI Vision Detected',
                    style: NutriTypography.dataSm.copyWith(
                      color: NutriColors.inkMuted,
                    ),
                  ),
                  _ConfidenceBadge(confidence: r.averageConfidence),
                ],
              ),
              const SizedBox(height: 4),
              Text(r.displayFoodName, style: NutriTypography.displayMd),
              Text(
                r.portionDisplay,
                style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted),
              ),
              const SizedBox(height: 20),

              // Macro grid
              _MacroGrid(result: r),
              const SizedBox(height: 20),

              // Items breakdown (if multiple items)
              if (r.items.length > 1) ...[
                Text(
                  'Detected Items',
                  style: NutriTypography.bodySm.copyWith(
                    fontWeight: FontWeight.w600,
                    color: NutriColors.inkMuted,
                  ),
                ),
                const SizedBox(height: 8),
                ...r.items.map((item) => _FoodItemRow(item: item)),
                const SizedBox(height: 16),
              ],

              // Compliance warnings
              if (r.complianceWarnings.isNotEmpty) ...[
                ...r.complianceWarnings.map(
                  (w) => _WarningChip(message: w),
                ),
                const SizedBox(height: 16),
              ],

              // Meal type picker
              _MealTypePicker(
                selected: _selectedMealType,
                onChanged: (v) => setState(() => _selectedMealType = v),
              ),
              const SizedBox(height: 20),

              // Error
              if (_logError != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: NutriColors.danger.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: NutriColors.danger.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Text(
                    _logError!,
                    style: NutriTypography.bodySm.copyWith(
                      color: NutriColors.danger,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
              ],

              // Actions
              Row(
                children: [
                  Expanded(
                    child: NutriButton(
                      text: 'Retake',
                      variant: ButtonVariant.outline,
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: NutriButton(
                      text: _logged
                          ? '✓ Logged!'
                          : _isLogging
                              ? 'Saving…'
                              : '⚡ Add to Diary',
                      onPressed: (_isLogging || _logged) ? null : _addToDiary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Sub-widgets
// ──────────────────────────────────────────────────────────────────────────────

class _ConfidenceBadge extends StatelessWidget {
  final double confidence;
  const _ConfidenceBadge({required this.confidence});

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).toInt();
    final color = pct >= 80
        ? const Color(0xFF22C55E)
        : pct >= 60
            ? const Color(0xFFF59E0B)
            : NutriColors.danger;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Text(
        '$pct% match',
        style: NutriTypography.dataSm.copyWith(
          color: color,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _MacroGrid extends StatelessWidget {
  final FoodRecognitionResult result;
  const _MacroGrid({required this.result});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
      decoration: BoxDecoration(
        color: NutriColors.canvas,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: NutriColors.border),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _Macro(
            value: result.totalCalories.toStringAsFixed(0),
            label: 'kcal',
            color: NutriColors.ink,
          ),
          _divider(),
          _Macro(
            value: '${result.totalProteinG.toStringAsFixed(1)}g',
            label: 'Protein',
            color: MacroColors.protein,
          ),
          _divider(),
          _Macro(
            value: '${result.totalCarbsG.toStringAsFixed(1)}g',
            label: 'Carbs',
            color: MacroColors.carbs,
          ),
          _divider(),
          _Macro(
            value: '${result.totalFatG.toStringAsFixed(1)}g',
            label: 'Fat',
            color: MacroColors.fat,
          ),
        ],
      ),
    );
  }

  Widget _divider() => Container(height: 36, width: 1, color: NutriColors.border);
}

class _Macro extends StatelessWidget {
  final String value;
  final String label;
  final Color color;
  const _Macro({required this.value, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(value, style: NutriTypography.displaySm.copyWith(color: color)),
        const SizedBox(height: 2),
        Text(label,
            style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted)),
      ],
    );
  }
}

class _FoodItemRow extends StatelessWidget {
  final RecognizedFoodItem item;
  const _FoodItemRow({required this.item});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: NutriColors.canvas,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: NutriColors.border),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.name, style: NutriTypography.bodySm.copyWith(fontWeight: FontWeight.w600)),
                if (item.region != null)
                  Text(item.region!, style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${item.calories.toStringAsFixed(0)} kcal',
                style: NutriTypography.bodySm.copyWith(fontWeight: FontWeight.w600),
              ),
              Text(
                '${item.portionG.toStringAsFixed(0)}g',
                style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _WarningChip extends StatelessWidget {
  final String message;
  const _WarningChip({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFF59E0B).withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFF59E0B).withValues(alpha: 0.25)),
      ),
      child: Text(
        message,
        style: NutriTypography.bodySm.copyWith(
          color: const Color(0xFFB45309),
        ),
      ),
    );
  }
}

class _MealTypePicker extends StatelessWidget {
  final String selected;
  final ValueChanged<String> onChanged;

  const _MealTypePicker({required this.selected, required this.onChanged});

  static const _types = [
    ('breakfast', '☀️', 'Breakfast'),
    ('lunch', '🍽️', 'Lunch'),
    ('dinner', '🌙', 'Dinner'),
    ('snack', '🍎', 'Snack'),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Log as',
          style: NutriTypography.bodySm.copyWith(
            fontWeight: FontWeight.w600,
            color: NutriColors.inkMuted,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: _types.map((t) {
            final (value, emoji, label) = t;
            final isSelected = selected == value;
            return Expanded(
              child: GestureDetector(
                onTap: () => onChanged(value),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  margin: const EdgeInsets.only(right: 6),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? NutriColors.primary.withValues(alpha: 0.12)
                        : NutriColors.canvas,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isSelected ? NutriColors.primary : NutriColors.border,
                      width: isSelected ? 1.5 : 1,
                    ),
                  ),
                  child: Column(
                    children: [
                      Text(emoji, style: const TextStyle(fontSize: 18)),
                      const SizedBox(height: 2),
                      Text(
                        label,
                        style: NutriTypography.dataSm.copyWith(
                          color: isSelected ? NutriColors.primary : NutriColors.inkMuted,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class _CircleIconButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _CircleIconButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white.withValues(alpha: 0.15),
              border: Border.all(color: Colors.white.withValues(alpha: 0.3)),
            ),
            child: Icon(icon, color: Colors.white, size: 26),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: NutriTypography.dataSm.copyWith(color: Colors.white.withValues(alpha: 0.7)),
          ),
        ],
      ),
    );
  }
}

class _OutlineButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final bool disabled;

  const _OutlineButton({
    required this.label,
    required this.icon,
    this.onTap,
    this.disabled = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: disabled ? null : onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: disabled
                ? Colors.white.withValues(alpha: 0.2)
                : Colors.white.withValues(alpha: 0.5),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 16,
                color: disabled
                    ? Colors.white.withValues(alpha: 0.3)
                    : Colors.white),
            const SizedBox(width: 8),
            Text(
              label,
              style: NutriTypography.bodySm.copyWith(
                color: disabled
                    ? Colors.white.withValues(alpha: 0.3)
                    : Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
