import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Models
// ─────────────────────────────────────────────────────────────────────────────

class DiaryEntry {
  final String id; // Required for DELETE /diary/entries/{id}
  final String mealType;
  final String foodName;
  final double calories;
  final double protein;
  final double carbs;
  final double fat;
  final String loggedAt;

  DiaryEntry({
    required this.id,
    required this.mealType,
    required this.foodName,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.loggedAt,
  });
}

class _DayTrend {
  final String day;
  final double calories;
  final double protein;
  final double carbs;
  final double fat;
  const _DayTrend({
    required this.day,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
  });
}

class _FoodSearchResult {
  final String name;
  final double calories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  const _FoodSearchResult({
    required this.name,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
  });

  factory _FoodSearchResult.fromJson(Map<String, dynamic> json) {
    return _FoodSearchResult(
      name: json['name'] as String? ?? 'Food',
      calories: (json['calories'] as num? ?? 0).toDouble(),
      proteinG: (json['protein_g'] as num? ?? 0).toDouble(),
      carbsG: (json['carbs_g'] as num? ?? 0).toDouble(),
      fatG: (json['fat_g'] as num? ?? 0).toDouble(),
    );
  }
}

extension StringCasingExtension on String {
  String toCapitalized() =>
      length > 0 ? '${this[0].toUpperCase()}${substring(1).toLowerCase()}' : '';
}

// ─────────────────────────────────────────────────────────────────────────────
// Screen
// ─────────────────────────────────────────────────────────────────────────────

class DailyDiaryScreen extends StatefulWidget {
  const DailyDiaryScreen({super.key});

  @override
  State<DailyDiaryScreen> createState() => _DailyDiaryScreenState();
}

class _DailyDiaryScreenState extends State<DailyDiaryScreen>
    with SingleTickerProviderStateMixin {
  final ApiClient _apiClient = ApiClient();

  bool _isLoading = true;
  bool _isCompensating = false;

  final double _targetCalories = 2000;
  double _loggedCalories = 0;

  final List<DiaryEntry> _entries = [];
  List<_DayTrend> _weekTrends = [];
  bool _trendsLoading = true;

  // Trend chart state
  int _selectedMetric = 0; // 0=Cal, 1=Protein, 2=Carbs, 3=Fat
  static const _metrics = [
    ('Calories', NutriColors.primary, 2000.0),
    ('Protein', MacroColors.protein, 120.0),
    ('Carbs', MacroColors.carbs, 220.0),
    ('Fat', MacroColors.fat, 65.0),
  ];

  @override
  void initState() {
    super.initState();
    _loadEntries();
    _loadWeekTrends();
  }

  // ── Data loading ────────────────────────────────────────────────────────────

  Future<void> _loadEntries() async {
    setState(() => _isLoading = true);
    try {
      final todayStr = DateFormat('yyyy-MM-dd').format(DateTime.now());
      final resp =
          await _apiClient.dio.get('${ApiEndpoints.diaryBaseUrl}/day/$todayStr');
      final List data = resp.data['entries'] ?? [];
      final parsed = data.map((e) => DiaryEntry(
            id: e['id']?.toString() ?? '',
            mealType: (e['meal_type'] ?? 'meal').toString().toCapitalized(),
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
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadWeekTrends() async {
    setState(() => _trendsLoading = true);
    final now = DateTime.now();
    final futures = List.generate(7, (i) async {
      final d = now.subtract(Duration(days: 6 - i));
      final dateStr = DateFormat('yyyy-MM-dd').format(d);
      final dayLabel = DateFormat('E').format(d);
      try {
        final resp = await _apiClient.dio
            .get('${ApiEndpoints.diaryBaseUrl}/day/$dateStr');
        final data = resp.data as Map<String, dynamic>;
        return _DayTrend(
          day: dayLabel,
          calories: (data['total_calories'] ?? 0).toDouble(),
          protein: (data['total_protein_g'] ?? 0).toDouble(),
          carbs: (data['total_carbs_g'] ?? 0).toDouble(),
          fat: (data['total_fat_g'] ?? 0).toDouble(),
        );
      } catch (_) {
        return _DayTrend(
          day: dayLabel,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
        );
      }
    });
    final results = await Future.wait(futures);
    if (mounted) {
      setState(() {
        _weekTrends = results;
        _trendsLoading = false;
      });
    }
  }

  // ── Delete entry ────────────────────────────────────────────────────────────

  Future<void> _deleteEntry(DiaryEntry entry) async {
    // Optimistic UI removal
    setState(() {
      _entries.removeWhere((e) => e.id == entry.id);
      _loggedCalories = _entries.fold(0, (s, e) => s + e.calories);
    });

    if (entry.id.isNotEmpty) {
      try {
        await _apiClient.dio
            .delete('${ApiEndpoints.diaryBaseUrl}/entries/${entry.id}');
      } catch (_) {
        // Non-critical — entry is already removed from UI
      }
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: NutriColors.danger,
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          content: Text('Removed "${entry.foodName}" from diary',
              style: const TextStyle(color: Colors.white)),
          action: SnackBarAction(
            label: 'Undo',
            textColor: Colors.white,
            onPressed: () {
              // Re-add to UI (backend deletion may have already happened)
              setState(() {
                _entries.add(entry);
                _loggedCalories += entry.calories;
              });
            },
          ),
        ),
      );
    }
  }

  // ── Compensation ────────────────────────────────────────────────────────────

  double get _overage => _loggedCalories - _targetCalories;
  bool get _hasOverage => _overage > 100;

  Future<void> _applyCompensation(String strategy) async {
    setState(() => _isCompensating = true);
    try {
      await _apiClient.dio.post(
        '${ApiEndpoints.planBaseUrl}/compensate-overage',
        data: {
          'user_id': 'current_user',
          'target_calories': _targetCalories,
          'logged_calories': _loggedCalories,
          'strategy': strategy,
          'days_to_spread': 2,
        },
      );
    } catch (_) {}
    if (!mounted) return;
    setState(() => _isCompensating = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: NutriColors.success,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        content: Text(
          strategy == 'smooth_48h'
              ? '✅ 48h Smooth Recovery applied! -${(_overage / 2).round()} kcal/day adjustment scheduled.'
              : '😊 Cheat Day forgiven! No macro adjustment needed.',
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }

  // ── Log Food sheet ──────────────────────────────────────────────────────────

  void _showLogFoodSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _LogFoodSheet(
        onLogged: () {
          _loadEntries();
          _loadWeekTrends();
        },
      ),
    );
  }

  // ── Build ───────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final progressFraction =
        (_loggedCalories / _targetCalories).clamp(0.0, 1.0);
    final remaining = (_targetCalories - _loggedCalories).round();

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        title: const Text('Food Diary', style: NutriTypography.displaySm),
        backgroundColor: NutriColors.canvas,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: NutriColors.primary),
            onPressed: () {
              _loadEntries();
              _loadWeekTrends();
            },
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showLogFoodSheet,
        backgroundColor: NutriColors.primary,
        icon: const Icon(Icons.add_rounded, color: Colors.white),
        label: const Text('Log Food',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: NutriColors.primary))
          : RefreshIndicator(
              onRefresh: () async {
                await _loadEntries();
                await _loadWeekTrends();
              },
              color: NutriColors.primary,
              child: ListView(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                children: [
                  // ── Calorie ring ──────────────────────────────────────────
                  _CalorieRingCard(
                    logged: _loggedCalories.round(),
                    target: _targetCalories.round(),
                    remaining: remaining,
                    fraction: progressFraction,
                  ),
                  const SizedBox(height: 16),

                  // ── Macro summary ─────────────────────────────────────────
                  _MacroSummaryRow(entries: _entries),
                  const SizedBox(height: 20),

                  // ── 7-day trend chart ─────────────────────────────────────
                  _WeeklyTrendChart(
                    trends: _weekTrends,
                    isLoading: _trendsLoading,
                    selectedMetric: _selectedMetric,
                    onMetricChanged: (i) =>
                        setState(() => _selectedMetric = i),
                    metrics: _metrics,
                  ),
                  const SizedBox(height: 20),

                  // ── Smart calorie buffer ──────────────────────────────────
                  if (_hasOverage) ...[
                    _CheatDayBufferCard(
                      overage: _overage.round(),
                      isCompensating: _isCompensating,
                      onSmooth48h: () => _applyCompensation('smooth_48h'),
                      onForgive: () =>
                          _applyCompensation('forgive_cheat_day'),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // ── Food log ──────────────────────────────────────────────
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("Today's Log",
                          style: NutriTypography.displaySm
                              .copyWith(fontWeight: FontWeight.bold)),
                      Text('${_entries.length} items',
                          style: NutriTypography.dataSm
                              .copyWith(color: NutriColors.inkMuted)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  if (_entries.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(32),
                      decoration: BoxDecoration(
                        color: NutriColors.canvasRaised,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: NutriColors.border),
                      ),
                      child: Column(
                        children: [
                          Icon(Icons.restaurant_menu_rounded,
                              size: 40,
                              color: NutriColors.inkMuted.withValues(alpha: 0.5)),
                          const SizedBox(height: 12),
                          Text('Nothing logged yet',
                              style: NutriTypography.bodyMd
                                  .copyWith(color: NutriColors.inkMuted)),
                          const SizedBox(height: 4),
                          Text('Tap + Log Food to add your first entry',
                              style: NutriTypography.bodySm
                                  .copyWith(color: NutriColors.inkMuted.withValues(alpha: 0.6))),
                        ],
                      ),
                    )
                  else
                    ..._entries.map((e) => _DiaryEntryTile(
                          entry: e,
                          onDelete: () => _deleteEntry(e),
                        )),

                  const SizedBox(height: 100),
                ],
              ),
            ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Log Food Bottom Sheet
// ─────────────────────────────────────────────────────────────────────────────

class _LogFoodSheet extends StatefulWidget {
  final VoidCallback onLogged;
  const _LogFoodSheet({required this.onLogged});

  @override
  State<_LogFoodSheet> createState() => _LogFoodSheetState();
}

class _LogFoodSheetState extends State<_LogFoodSheet> {
  final ApiClient _apiClient = ApiClient();
  final TextEditingController _searchCtrl = TextEditingController();

  String _selectedMealType = 'lunch';
  List<_FoodSearchResult> _results = [];
  bool _searching = false;
  bool _logging = false;

  static const _mealTypes = [
    ('breakfast', '☀️'),
    ('lunch', '🍽️'),
    ('snack', '🍎'),
    ('dinner', '🌙'),
  ];

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _search(String q) async {
    if (q.trim().isEmpty) {
      setState(() => _results = []);
      return;
    }
    setState(() => _searching = true);
    try {
      final resp = await _apiClient.dio.get(
        '${ApiEndpoints.visionBaseUrl}/foods/search',
        queryParameters: {'q': q.trim(), 'limit': 12},
      );
      final list = resp.data['results'] as List? ?? [];
      setState(() {
        _results = list
            .whereType<Map<String, dynamic>>()
            .map((j) => _FoodSearchResult.fromJson(j))
            .toList();
      });
    } catch (_) {
      setState(() => _results = []);
    } finally {
      setState(() => _searching = false);
    }
  }

  Future<void> _logItem(_FoodSearchResult item) async {
    setState(() => _logging = true);
    try {
      final todayStr = DateFormat('yyyy-MM-dd').format(DateTime.now());
      await _apiClient.dio.post(
        '${ApiEndpoints.diaryBaseUrl}/entries',
        data: {
          'log_date': todayStr,
          'meal_type': _selectedMealType,
          'food_name': item.name,
          'quantity_g': 100.0,
          'calories': item.calories,
          'protein_g': item.proteinG,
          'carbs_g': item.carbsG,
          'fat_g': item.fatG,
          'fiber_g': 3.0,
          'source': 'manual_search',
        },
      );
      if (mounted) {
        Navigator.pop(context);
        widget.onLogged();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: NutriColors.success,
            behavior: SnackBarBehavior.floating,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            content: Row(
              children: [
                const Icon(Icons.check_circle_rounded,
                    color: Colors.white, size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Logged ${item.name} to ${_selectedMealType.toCapitalized()}!',
                    style: const TextStyle(
                        color: Colors.white, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
        );
      }
    } catch (_) {
      setState(() => _logging = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to log food. Please try again.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      builder: (_, scrollController) => Container(
        decoration: const BoxDecoration(
          color: NutriColors.canvasRaised,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
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

            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Log Food',
                      style: NutriTypography.displaySm
                          .copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),

                  // Meal type tabs
                  Row(
                    children: _mealTypes.map((t) {
                      final (value, emoji) = t;
                      final selected = _selectedMealType == value;
                      return Expanded(
                        child: GestureDetector(
                          onTap: () =>
                              setState(() => _selectedMealType = value),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 160),
                            margin: const EdgeInsets.only(right: 6),
                            padding:
                                const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: selected
                                  ? NutriColors.primary.withValues(alpha: 0.12)
                                  : NutriColors.canvas,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                color: selected
                                    ? NutriColors.primary
                                    : NutriColors.border,
                                width: selected ? 1.5 : 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                Text(emoji,
                                    style: const TextStyle(fontSize: 16)),
                                const SizedBox(height: 2),
                                Text(
                                  value.toCapitalized(),
                                  style: NutriTypography.dataSm.copyWith(
                                    color: selected
                                        ? NutriColors.primary
                                        : NutriColors.inkMuted,
                                    fontWeight: selected
                                        ? FontWeight.w700
                                        : FontWeight.normal,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 14),

                  // Search field
                  TextField(
                    controller: _searchCtrl,
                    onChanged: _search,
                    autofocus: true,
                    style: NutriTypography.bodyMd,
                    decoration: InputDecoration(
                      hintText: 'Search food (e.g. Roti, Dal, Paneer, Rice…)',
                      hintStyle: NutriTypography.bodyMd
                          .copyWith(color: NutriColors.inkMuted),
                      prefixIcon: const Icon(Icons.search_rounded,
                          color: NutriColors.inkMuted),
                      suffixIcon: _searching
                          ? const Padding(
                              padding: EdgeInsets.all(12),
                              child: SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: NutriColors.primary,
                                ),
                              ),
                            )
                          : null,
                      filled: true,
                      fillColor: NutriColors.canvas,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: NutriColors.border),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: NutriColors.border),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(
                            color: NutriColors.primary, width: 1.5),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Results
            Expanded(
              child: ListView.separated(
                controller: scrollController,
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
                itemCount: _results.isEmpty && _searchCtrl.text.isEmpty
                    ? 0
                    : _results.isEmpty
                        ? 1
                        : _results.length,
                separatorBuilder: (_, __) => const SizedBox(height: 6),
                itemBuilder: (_, i) {
                  if (_results.isEmpty) {
                    return Center(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 32),
                        child: Text(
                          _searching
                              ? 'Searching…'
                              : 'No results found for "${_searchCtrl.text}"',
                          style: NutriTypography.bodySm
                              .copyWith(color: NutriColors.inkMuted),
                        ),
                      ),
                    );
                  }
                  final item = _results[i];
                  return GestureDetector(
                    onTap: _logging ? null : () => _logItem(item),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 12),
                      decoration: BoxDecoration(
                        color: NutriColors.canvas,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: NutriColors.border),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(item.name,
                                    style: NutriTypography.bodyMd
                                        .copyWith(fontWeight: FontWeight.w600)),
                                const SizedBox(height: 2),
                                Text(
                                  '${item.calories.toStringAsFixed(0)} kcal / 100g',
                                  style: NutriTypography.dataSm
                                      .copyWith(color: NutriColors.inkMuted),
                                ),
                              ],
                            ),
                          ),
                          Row(
                            children: [
                              _MacroTag('P${item.proteinG.toStringAsFixed(0)}g',
                                  MacroColors.protein),
                              const SizedBox(width: 4),
                              _MacroTag('C${item.carbsG.toStringAsFixed(0)}g',
                                  MacroColors.carbs),
                              const SizedBox(width: 4),
                              _MacroTag('F${item.fatG.toStringAsFixed(0)}g',
                                  MacroColors.fat),
                            ],
                          ),
                          const SizedBox(width: 8),
                          const Icon(Icons.add_circle_outline_rounded,
                              color: NutriColors.primary, size: 22),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MacroTag extends StatelessWidget {
  final String label;
  final Color color;
  const _MacroTag(this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Text(label,
        style: TextStyle(
            fontSize: 10, fontWeight: FontWeight.w700, color: color));
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 7-Day Weekly Trend Chart
// ─────────────────────────────────────────────────────────────────────────────

class _WeeklyTrendChart extends StatelessWidget {
  final List<_DayTrend> trends;
  final bool isLoading;
  final int selectedMetric;
  final ValueChanged<int> onMetricChanged;
  final List<(String, Color, double)> metrics;

  const _WeeklyTrendChart({
    required this.trends,
    required this.isLoading,
    required this.selectedMetric,
    required this.onMetricChanged,
    required this.metrics,
  });

  double _valueForTrend(_DayTrend t, int metricIdx) {
    switch (metricIdx) {
      case 1: return t.protein;
      case 2: return t.carbs;
      case 3: return t.fat;
      default: return t.calories;
    }
  }

  @override
  Widget build(BuildContext context) {
    final (label, color, target) = metrics[selectedMetric];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: NutriColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('7-Day Trends',
                      style: NutriTypography.displaySm
                          .copyWith(fontWeight: FontWeight.bold)),
                  Text('Past week nutrition overview',
                      style: NutriTypography.dataSm
                          .copyWith(color: NutriColors.inkMuted)),
                ],
              ),
              if (isLoading)
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                      strokeWidth: 2, color: NutriColors.primary),
                ),
            ],
          ),
          const SizedBox(height: 14),

          // Metric selector chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: List.generate(metrics.length, (i) {
                final (mlabel, mcolor, _) = metrics[i];
                final selected = i == selectedMetric;
                return GestureDetector(
                  onTap: () => onMetricChanged(i),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 160),
                    margin: const EdgeInsets.only(right: 8),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: selected
                          ? mcolor.withValues(alpha: 0.12)
                          : NutriColors.canvas,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: selected
                            ? mcolor
                            : NutriColors.border,
                        width: selected ? 1.5 : 1,
                      ),
                    ),
                    child: Text(
                      mlabel,
                      style: NutriTypography.dataSm.copyWith(
                        color: selected ? mcolor : NutriColors.inkMuted,
                        fontWeight: selected
                            ? FontWeight.w700
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                );
              }),
            ),
          ),
          const SizedBox(height: 20),

          // Line chart
          SizedBox(
            height: 160,
            child: isLoading || trends.isEmpty
                ? Center(
                    child: Text(
                      isLoading ? 'Loading…' : 'No data yet',
                      style: NutriTypography.bodySm
                          .copyWith(color: NutriColors.inkMuted),
                    ),
                  )
                : LineChart(
                    LineChartData(
                      gridData: FlGridData(
                        show: true,
                        drawVerticalLine: false,
                        getDrawingHorizontalLine: (value) => const FlLine(
                          color: NutriColors.border,
                          strokeWidth: 1,
                        ),
                      ),
                      titlesData: FlTitlesData(
                        leftTitles: const AxisTitles(
                          sideTitles: SideTitles(showTitles: false),
                        ),
                        topTitles: const AxisTitles(
                          sideTitles: SideTitles(showTitles: false),
                        ),
                        rightTitles: const AxisTitles(
                          sideTitles: SideTitles(showTitles: false),
                        ),
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            reservedSize: 28,
                            getTitlesWidget: (value, meta) {
                              final idx = value.toInt();
                              if (idx < 0 || idx >= trends.length) {
                                return const SizedBox.shrink();
                              }
                              return Text(
                                trends[idx].day,
                                style: NutriTypography.dataSm.copyWith(
                                    fontSize: 10,
                                    color: NutriColors.inkMuted),
                              );
                            },
                          ),
                        ),
                      ),
                      borderData: FlBorderData(show: false),
                      lineTouchData: LineTouchData(
                        touchTooltipData: LineTouchTooltipData(
                          getTooltipItems: (spots) {
                            return spots.map((spot) {
                              final isTrend = spot.barIndex == 0;
                              return LineTooltipItem(
                                isTrend
                                    ? '${spot.y.toStringAsFixed(0)} ${label.contains('(') ? 'g' : label == 'Calories' ? 'kcal' : 'g'}'
                                    : 'Target',
                                TextStyle(
                                  color: isTrend ? color : Colors.grey,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 11,
                                ),
                              );
                            }).toList();
                          },
                        ),
                      ),
                      lineBarsData: [
                        // Actual data line
                        LineChartBarData(
                          spots: trends.asMap().entries.map((e) {
                            return FlSpot(
                              e.key.toDouble(),
                              _valueForTrend(e.value, selectedMetric),
                            );
                          }).toList(),
                          isCurved: true,
                          color: color,
                          barWidth: 2.5,
                          dotData: FlDotData(
                            show: true,
                            getDotPainter: (spot, pct, bar, idx) {
                              return FlDotCirclePainter(
                                radius: 3.5,
                                color: color,
                                strokeWidth: 1.5,
                                strokeColor: Colors.white,
                              );
                            },
                          ),
                          belowBarData: BarAreaData(
                            show: true,
                            color: color.withValues(alpha: 0.08),
                          ),
                        ),
                        // Target dashed line
                        LineChartBarData(
                          spots: List.generate(
                            trends.length,
                            (i) => FlSpot(i.toDouble(), target),
                          ),
                          isCurved: false,
                          color: NutriColors.border,
                          barWidth: 1.5,
                          dashArray: [6, 4],
                          dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(show: false),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Calorie Ring Card
// ─────────────────────────────────────────────────────────────────────────────

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
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.02),
              blurRadius: 8,
              offset: const Offset(0, 3)),
        ],
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
                Text(
                  '${(fraction * 100).round()}%',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Daily Calories',
                    style: NutriTypography.bodyMd
                        .copyWith(color: NutriColors.inkMuted)),
                const SizedBox(height: 4),
                Text('$logged / $target kcal',
                    style: NutriTypography.displaySm
                        .copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: isOver
                        ? const Color(0xFFFFEBEE)
                        : const Color(0xFFE8F5E9),
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

// ─────────────────────────────────────────────────────────────────────────────
// Smart Cheat Day Buffer Card
// ─────────────────────────────────────────────────────────────────────────────

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
                      style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: Color(0xFFE65100)),
                    ),
                    Text(
                      '+$overage kcal over today\'s target. Choose your recovery strategy:',
                      style: const TextStyle(
                          fontSize: 12, color: Color(0xFF795548)),
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
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  child: isCompensating
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2))
                      : const Text('⚡ Smooth 48h Recovery',
                          style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Colors.white)),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton(
                  onPressed: isCompensating ? null : onForgive,
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFFFCC02)),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  child: const Text('😊 Forgive Cheat Day',
                      style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFE65100))),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Protein targets are PROTECTED — only refined carbs & oils are reduced.',
            style: TextStyle(
                fontSize: 10,
                color: Color(0xFF795548),
                fontStyle: FontStyle.italic),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Macro Summary Row
// ─────────────────────────────────────────────────────────────────────────────

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
        _MacroChip(
            label: 'Protein',
            value: '${totalP.round()}g',
            color: MacroColors.protein),
        const SizedBox(width: 8),
        _MacroChip(
            label: 'Carbs',
            value: '${totalC.round()}g',
            color: MacroColors.carbs),
        const SizedBox(width: 8),
        _MacroChip(
            label: 'Fat',
            value: '${totalF.round()}g',
            color: MacroColors.fat),
      ],
    );
  }
}

class _MacroChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  const _MacroChip(
      {required this.label, required this.value, required this.color});

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
            Text(value,
                style: TextStyle(
                    fontWeight: FontWeight.bold, fontSize: 16, color: color)),
            const SizedBox(height: 2),
            Text(label,
                style: TextStyle(
                    fontSize: 10, color: color.withValues(alpha: 0.8))),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Diary Entry Tile — Dismissible swipe-to-delete
// ─────────────────────────────────────────────────────────────────────────────

class _DiaryEntryTile extends StatelessWidget {
  final DiaryEntry entry;
  final VoidCallback onDelete;
  const _DiaryEntryTile({required this.entry, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key('diary_${entry.id}_${entry.foodName}'),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        margin: const EdgeInsets.only(bottom: 10),
        decoration: BoxDecoration(
          color: NutriColors.danger.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(14),
        ),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.delete_rounded, color: NutriColors.danger, size: 22),
            SizedBox(height: 2),
            Text('Remove',
                style: TextStyle(
                    color: NutriColors.danger,
                    fontSize: 10,
                    fontWeight: FontWeight.w600)),
          ],
        ),
      ),
      confirmDismiss: (direction) async {
        return await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Remove entry?'),
            content: Text('Remove "${entry.foodName}" from your diary?'),
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            actions: [
              TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Cancel')),
              TextButton(
                onPressed: () => Navigator.pop(ctx, true),
                child: const Text('Remove',
                    style: TextStyle(color: NutriColors.danger)),
              ),
            ],
          ),
        );
      },
      onDismissed: (_) => onDelete(),
      child: Container(
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
              child: Text(_mealEmoji(entry.mealType),
                  style: const TextStyle(fontSize: 18)),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(entry.foodName,
                      style: NutriTypography.bodyMd
                          .copyWith(fontWeight: FontWeight.w600)),
                  Text(
                    '${entry.mealType} · ${entry.calories.round()} kcal',
                    style: NutriTypography.bodySm
                        .copyWith(color: NutriColors.inkMuted),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text('P${entry.protein.round()}g',
                    style: const TextStyle(
                        fontSize: 10,
                        color: MacroColors.protein,
                        fontWeight: FontWeight.bold)),
                Text('C${entry.carbs.round()}g',
                    style: const TextStyle(
                        fontSize: 10,
                        color: MacroColors.carbs,
                        fontWeight: FontWeight.bold)),
                Text('F${entry.fat.round()}g',
                    style: const TextStyle(
                        fontSize: 10,
                        color: MacroColors.fat,
                        fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(width: 8),
            Icon(Icons.swipe_left_rounded,
                size: 14, color: NutriColors.inkMuted.withValues(alpha: 0.4)),
          ],
        ),
      ),
    );
  }

  String _mealEmoji(String meal) {
    switch (meal.toLowerCase()) {
      case 'breakfast': return '🌅';
      case 'lunch': return '☀️';
      case 'snack': return '🍎';
      case 'dinner': return '🌙';
      default: return '🍽️';
    }
  }
}
