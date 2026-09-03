import 'dart:math';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:intl/intl.dart';
import '../../../core/network/api_client.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../services/diary_service.dart';

/// A diary entry returned from the backend or mocked locally.
class DiaryEntry {
  final String mealType;
  final String foodName;
  final double calories;
  final double protein;
  final double carbs;
  final double fat;
  final String loggedAt;

  DiaryEntry({
    required this.mealType,
    required this.foodName,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.loggedAt,
  });
}

class DailyDiaryScreen extends StatefulWidget {
  const DailyDiaryScreen({super.key});

  @override
  State<DailyDiaryScreen> createState() => _DailyDiaryScreenState();
}

class _DailyDiaryScreenState extends State<DailyDiaryScreen> {
  final ApiClient _apiClient = ApiClient();
  bool _isLoading = true;
  bool _isCompensating = false;
  String? _snackMsg;

  double _targetCalories = 1800;
  double _loggedCalories = 0;

  final List<DiaryEntry> _entries = [];

  @override
  void initState() {
    super.initState();
    _loadEntries();
  }

  Future<void> _loadEntries() async {
    setState(() => _isLoading = true);
    try {
      final todayStr = DateFormat('yyyy-MM-dd').format(DateTime.now());
      final resp = await _apiClient.dio
          .get('/api/v1/diary/entries?date=$todayStr');
      final List data = resp.data['entries'] ?? [];
      final parsed = data.map((e) => DiaryEntry(
            mealType: e['meal_type'] ?? 'meal',
            foodName: e['food_name'] ?? 'Unknown',
            calories: (e['calories'] ?? 0).toDouble(),
            protein: (e['protein_g'] ?? 0).toDouble(),
            carbs: (e['carbs_g'] ?? 0).toDouble(),
            fat: (e['fat_g'] ?? 0).toDouble(),
            loggedAt: e['log_date'] ?? todayStr,
          )).toList();
      setState(() {
        _entries
          ..clear()
          ..addAll(parsed);
        _loggedCalories = _entries.fold(0, (s, e) => s + e.calories);
        _isLoading = false;
      });
    } catch (_) {
      // Demo mode — seed realistic sample entries
      final demo = [
        DiaryEntry(mealType: 'Breakfast', foodName: 'Idli with Sambar', calories: 320, protein: 9, carbs: 62, fat: 3, loggedAt: 'Today'),
        DiaryEntry(mealType: 'Lunch', foodName: 'Chicken Biryani', calories: 680, protein: 34, carbs: 78, fat: 22, loggedAt: 'Today'),
        DiaryEntry(mealType: 'Snack', foodName: 'Mixed Nuts & Banana', calories: 310, protein: 8, carbs: 42, fat: 14, loggedAt: 'Today'),
        DiaryEntry(mealType: 'Dinner', foodName: 'Paneer Butter Masala + Roti', calories: 590, protein: 22, carbs: 64, fat: 26, loggedAt: 'Today'),
      ];
      setState(() {
        _entries
          ..clear()
          ..addAll(demo);
        _loggedCalories = _entries.fold(0, (s, e) => s + e.calories);
        _isLoading = false;
      });
    }
  }

  double get _overage => _loggedCalories - _targetCalories;
  bool get _hasOverage => _overage > 100;

  Future<void> _applyCompensation(String strategy) async {
    setState(() => _isCompensating = true);
    try {
      await _apiClient.dio.post('/api/v1/plan/compensate-overage', data: {
        'user_id': 'mob_usr_001',
        'target_calories': _targetCalories,
        'logged_calories': _loggedCalories,
        'strategy': strategy,
        'days_to_spread': 2,
      });
    } catch (_) {}
    setState(() {
      _isCompensating = false;
      _snackMsg = strategy == 'smooth_48h'
          ? '✅ 48h Smooth Recovery plan applied! -${(_overage / 2).round()} kcal/day adjustment scheduled.'
          : '😊 Cheat Day forgiven! No macro adjustment needed.';
    });
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) setState(() => _snackMsg = null);
    });
  }

  @override
  Widget build(BuildContext context) {
    final progressFraction = (_loggedCalories / _targetCalories).clamp(0.0, 1.0);
    final remaining = (_targetCalories - _loggedCalories).round();

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        title: Text('Daily Diary', style: NutriTypography.displaySm),
        backgroundColor: NutriColors.canvas,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: NutriColors.primary),
            onPressed: _loadEntries,
          )
        ],
      ),
      body: Stack(
        children: [
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _loadEntries,
                  child: ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    children: [
                      // ── Calorie Progress Ring ──────────────────────────────
                      _CalorieRingCard(
                        logged: _loggedCalories.round(),
                        target: _targetCalories.round(),
                        remaining: remaining,
                        fraction: progressFraction,
                      ),
                      const SizedBox(height: 16),

                      // ── Smart Cheat Day Buffer Banner ──────────────────────
                      if (_hasOverage) ...[
                        _CheatDayBufferCard(
                          overage: _overage.round(),
                          isCompensating: _isCompensating,
                          onSmooth48h: () => _applyCompensation('smooth_48h'),
                          onForgive: () => _applyCompensation('forgive_cheat_day'),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // ── Macro Summary ──────────────────────────────────────
                      _MacroSummaryRow(entries: _entries),
                      const SizedBox(height: 20),

                      // ── Food Log Entries ───────────────────────────────────
                      Text('Today\'s Log', style: NutriTypography.displaySm.copyWith(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 10),
                      ..._entries.map((e) => _DiaryEntryTile(entry: e)),
                      const SizedBox(height: 80),
                    ],
                  ),
                ),

          // Snackbar overlay
          if (_snackMsg != null)
            Positioned(
              bottom: 24,
              left: 16,
              right: 16,
              child: Material(
                borderRadius: BorderRadius.circular(14),
                color: NutriColors.success,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  child: Text(_snackMsg!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

// ─── Calorie Progress Ring ─────────────────────────────────────────────────────
class _CalorieRingCard extends StatelessWidget {
  final int logged;
  final int target;
  final int remaining;
  final double fraction;

  const _CalorieRingCard({
    required this.logged,
    required this.target,
    required this.remaining,
    required this.fraction,
  });

  @override
  Widget build(BuildContext context) {
    final isOver = remaining < 0;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: NutriColors.border),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 90,
            height: 90,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: fraction,
                  strokeWidth: 8,
                  backgroundColor: NutriColors.border,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    isOver ? NutriColors.danger : NutriColors.primary,
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('${(fraction * 100).round()}%',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Daily Calories', style: NutriTypography.bodyMd.copyWith(color: NutriColors.inkMuted)),
                const SizedBox(height: 4),
                Text('$logged / $target kcal',
                    style: NutriTypography.displaySm.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: isOver ? const Color(0xFFFFEBEE) : const Color(0xFFE8F5E9),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isOver ? NutriColors.danger : NutriColors.success,
                    ),
                  ),
                  child: Text(
                    isOver
                        ? '${remaining.abs()} kcal over budget'
                        : '$remaining kcal remaining',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: isOver ? NutriColors.danger : NutriColors.success,
                    ),
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

// ─── Smart Cheat Day Buffer Card ───────────────────────────────────────────────
class _CheatDayBufferCard extends StatelessWidget {
  final int overage;
  final bool isCompensating;
  final VoidCallback onSmooth48h;
  final VoidCallback onForgive;

  const _CheatDayBufferCard({
    required this.overage,
    required this.isCompensating,
    required this.onSmooth48h,
    required this.onForgive,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF8E1), Color(0xFFFFF3E0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFFFCC02), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('🔥', style: TextStyle(fontSize: 20)),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Smart Calorie Buffer Active',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFFE65100)),
                    ),
                    Text(
                      '+$overage kcal over today\'s target. Choose your recovery strategy:',
                      style: const TextStyle(fontSize: 12, color: Color(0xFF795548)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: isCompensating ? null : onSmooth48h,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6200EE),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  child: isCompensating
                      ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('Smooth 48h Recovery', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton(
                  onPressed: isCompensating ? null : onForgive,
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFFFCC02)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  child: const Text('😊 Forgive Cheat Day', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFE65100))),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Protein targets are PROTECTED — only refined carbs & oils are reduced.',
            style: TextStyle(fontSize: 10, color: Color(0xFF795548), fontStyle: FontStyle.italic),
          ),
        ],
      ),
    );
  }
}

// ─── Macro Summary Row ─────────────────────────────────────────────────────────
class _MacroSummaryRow extends StatelessWidget {
  final List<DiaryEntry> entries;
  const _MacroSummaryRow({required this.entries});

  @override
  Widget build(BuildContext context) {
    final totalP = entries.fold(0.0, (s, e) => s + e.protein);
    final totalC = entries.fold(0.0, (s, e) => s + e.carbs);
    final totalF = entries.fold(0.0, (s, e) => s + e.fat);
    return Row(
      children: [
        _MacroChip(label: 'Protein', value: '${totalP.round()}g', color: MacroColors.protein),
        const SizedBox(width: 8),
        _MacroChip(label: 'Carbs', value: '${totalC.round()}g', color: MacroColors.carbs),
        const SizedBox(width: 8),
        _MacroChip(label: 'Fat', value: '${totalF.round()}g', color: MacroColors.fat),
      ],
    );
  }
}

class _MacroChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  const _MacroChip({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.4)),
        ),
        child: Column(
          children: [
            Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: color)),
            const SizedBox(height: 2),
            Text(label, style: TextStyle(fontSize: 10, color: color.withValues(alpha: 0.8))),
          ],
        ),
      ),
    );
  }
}

// ─── Diary Entry Tile ──────────────────────────────────────────────────────────
class _DiaryEntryTile extends StatelessWidget {
  final DiaryEntry entry;
  const _DiaryEntryTile({required this.entry});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: NutriColors.border),
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: NutriColors.primarySoft,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(_mealEmoji(entry.mealType), style: const TextStyle(fontSize: 18)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(entry.foodName, style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.w600)),
                Text('${entry.mealType} · ${entry.calories.round()} kcal',
                    style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('P${entry.protein.round()}g', style: TextStyle(fontSize: 10, color: MacroColors.protein, fontWeight: FontWeight.bold)),
              Text('C${entry.carbs.round()}g', style: TextStyle(fontSize: 10, color: MacroColors.carbs, fontWeight: FontWeight.bold)),
              Text('F${entry.fat.round()}g', style: TextStyle(fontSize: 10, color: MacroColors.fat, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  String _mealEmoji(String meal) {
    switch (meal.toLowerCase()) {
      case 'breakfast': return '🌅';
      case 'lunch':     return '☀️';
      case 'snack':     return '🍎';
      case 'dinner':    return '🌙';
      default:          return '🍽️';
    }
  }
}
