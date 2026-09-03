import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';

/// A recycled dish suggestion returned from the backend.
class RecycledDish {
  final String name;
  final String emoji;
  final List<String> ingredientsUsed;
  final int prepMinutes;
  final int savedInr;

  RecycledDish({
    required this.name,
    required this.emoji,
    required this.ingredientsUsed,
    required this.prepMinutes,
    required this.savedInr,
  });

  factory RecycledDish.fromJson(Map<String, dynamic> json) => RecycledDish(
        name: json['dish_name'] ?? 'Unknown',
        emoji: json['emoji'] ?? '🍲',
        ingredientsUsed: List<String>.from(json['matching_leftovers_used'] ?? []),
        prepMinutes: json['prep_time_minutes'] ?? 15,
        savedInr: json['waste_saved_estimate_inr']?.round() ?? 0,
      );
}

class GroceryScreen extends StatefulWidget {
  const GroceryScreen({super.key});

  @override
  State<GroceryScreen> createState() => _GroceryScreenState();
}

class _GroceryScreenState extends State<GroceryScreen> {
  final ApiClient _apiClient = ApiClient();

  bool _isRecycling = false;
  bool _recyclerOpen = false;
  String? _snackMsg;

  List<RecycledDish> _recycledDishes = [];
  int _totalSaved = 0;

  // Simulated pantry items that the user entered or synced
  final List<Map<String, dynamic>> _pantryItems = [
    {'name': 'Paneer', 'qty': '200g', 'emoji': '🧀', 'expiring': true},
    {'name': 'Spinach (Palak)', 'qty': '1 bunch', 'emoji': '🥬', 'expiring': true},
    {'name': 'Cooked Rice', 'qty': '1 cup', 'emoji': '🍚', 'expiring': true},
    {'name': 'Curd / Yogurt', 'qty': '250ml', 'emoji': '🥛', 'expiring': false},
    {'name': 'Tomatoes', 'qty': '3 pcs', 'emoji': '🍅', 'expiring': false},
    {'name': 'Coriander', 'qty': 'handful', 'emoji': '🌿', 'expiring': true},
  ];

  // Simulated weekly grocery checklist
  final List<Map<String, dynamic>> _groceryList = [
    {'item': 'Brown Rice (1 kg)', 'category': 'Grains', 'checked': true},
    {'item': 'Chicken Breast (500g)', 'category': 'Protein', 'checked': true},
    {'item': 'Moong Dal (500g)', 'category': 'Protein', 'checked': false},
    {'item': 'Broccoli', 'category': 'Vegetables', 'checked': false},
    {'item': 'Sweet Potato (3 pcs)', 'category': 'Carbs', 'checked': false},
    {'item': 'Greek Yogurt', 'category': 'Dairy', 'checked': true},
    {'item': 'Almonds (100g)', 'category': 'Fats', 'checked': false},
    {'item': 'Olive Oil (250ml)', 'category': 'Fats', 'checked': true},
    {'item': 'Spinach (2 bunches)', 'category': 'Vegetables', 'checked': false},
    {'item': 'Banana (6 pcs)', 'category': 'Fruits', 'checked': false},
  ];

  Future<void> _runRecycler() async {
    setState(() { _isRecycling = true; _recyclerOpen = true; });
    try {
      final resp = await _apiClient.dio.post('/api/v1/grocery/recycle-leftovers', data: {
        'user_id': 'mob_usr_001',
        'pantry_items': _pantryItems.map((p) => p['name'].toString().toLowerCase()).toList(),
        'regional_preference': 'in_south_andhra',
      });
      final List data = resp.data['recycled_dishes'] ?? [];
      setState(() {
        _recycledDishes = data.map((d) => RecycledDish.fromJson(d)).toList();
        _totalSaved = resp.data['total_waste_saved_inr']?.round() ?? 0;
        _isRecycling = false;
      });
    } catch (_) {
      // Demo fallback
      await Future.delayed(const Duration(milliseconds: 800));
      setState(() {
        _recycledDishes = [
          RecycledDish(name: 'Palak Paneer Pulao', emoji: '🍲', ingredientsUsed: ['Paneer', 'Spinach', 'Cooked Rice'], prepMinutes: 12, savedInr: 95),
          RecycledDish(name: 'Paneer Curd Sabzi', emoji: '🧀', ingredientsUsed: ['Paneer', 'Curd', 'Tomatoes'], prepMinutes: 10, savedInr: 75),
          RecycledDish(name: 'Rice Curd Bowl', emoji: '🥗', ingredientsUsed: ['Cooked Rice', 'Curd', 'Coriander'], prepMinutes: 5, savedInr: 40),
        ];
        _totalSaved = 210;
        _isRecycling = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final checked = _groceryList.where((g) => g['checked'] == true).length;

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        title: Text('Weekly Grocery', style: NutriTypography.displaySm),
        backgroundColor: NutriColors.canvas,
        elevation: 0,
      ),
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            children: [
              // ── Progress Bar ─────────────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: NutriColors.canvasRaised,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: NutriColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Grocery Progress', style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold)),
                        Text('$checked / ${_groceryList.length} items', style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: LinearProgressIndicator(
                        value: checked / _groceryList.length,
                        minHeight: 8,
                        backgroundColor: NutriColors.border,
                        valueColor: const AlwaysStoppedAnimation<Color>(NutriColors.primary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Pantry Zero-Waste Recycler ────────────────────────────────
              _PantryRecyclerCard(
                pantryItems: _pantryItems,
                recycledDishes: _recycledDishes,
                totalSaved: _totalSaved,
                isRecycling: _isRecycling,
                isOpen: _recyclerOpen,
                onRecycle: _runRecycler,
              ),
              const SizedBox(height: 20),

              // ── Grocery Checklist ─────────────────────────────────────────
              Text('This Week\'s List', style: NutriTypography.displaySm.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              ..._groceryList.asMap().entries.map((entry) {
                final item = entry.value;
                return StatefulBuilder(
                  builder: (ctx, setLocal) => CheckboxListTile(
                    value: item['checked'] as bool,
                    onChanged: (v) {
                      setLocal(() => item['checked'] = v ?? false);
                    },
                    title: Text(
                      item['item'] as String,
                      style: TextStyle(
                        decoration: item['checked'] == true ? TextDecoration.lineThrough : null,
                        color: item['checked'] == true ? NutriColors.inkMuted : NutriColors.ink,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    subtitle: Text(item['category'] as String, style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted)),
                    activeColor: NutriColors.primary,
                    contentPadding: EdgeInsets.zero,
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                );
              }),
              const SizedBox(height: 60),
            ],
          ),
        ],
      ),
    );
  }
}

// ─── Pantry Recycler Card ──────────────────────────────────────────────────────
class _PantryRecyclerCard extends StatelessWidget {
  final List<Map<String, dynamic>> pantryItems;
  final List<RecycledDish> recycledDishes;
  final int totalSaved;
  final bool isRecycling;
  final bool isOpen;
  final VoidCallback onRecycle;

  const _PantryRecyclerCard({
    required this.pantryItems,
    required this.recycledDishes,
    required this.totalSaved,
    required this.isRecycling,
    required this.isOpen,
    required this.onRecycle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE8F5E9), Color(0xFFF1F8E9)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFF66BB6A), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              const Text('♻️', style: TextStyle(fontSize: 22)),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Pantry Zero-Waste Recycler',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF2E7D32))),
                    Text('Turn fridge leftovers into quick meals',
                        style: TextStyle(fontSize: 11, color: Color(0xFF558B2F))),
                  ],
                ),
              ),
              if (totalSaved > 0)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2E7D32),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text('₹$totalSaved saved',
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                ),
            ],
          ),
          const SizedBox(height: 12),

          // Pantry items
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: pantryItems.map((p) => Chip(
                  label: Text('${p['emoji']} ${p['name']}',
                      style: TextStyle(
                          fontSize: 11,
                          color: (p['expiring'] as bool) ? const Color(0xFFE65100) : const Color(0xFF2E7D32))),
                  backgroundColor: (p['expiring'] as bool) ? const Color(0xFFFFF3E0) : const Color(0xFFE8F5E9),
                  side: BorderSide(color: (p['expiring'] as bool) ? const Color(0xFFFFA726) : const Color(0xFF66BB6A)),
                  padding: EdgeInsets.zero,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                )).toList(),
          ),
          const SizedBox(height: 12),

          // CTA Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: isRecycling ? null : onRecycle,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2E7D32),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: isRecycling
                  ? const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(height: 16, width: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
                        SizedBox(width: 8),
                        Text('Finding recipes...', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      ],
                    )
                  : const Text('♻️ Generate Zero-Waste Recipes',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ),

          // Results
          if (isOpen && recycledDishes.isNotEmpty) ...[
            const SizedBox(height: 14),
            const Divider(color: Color(0xFF66BB6A)),
            const SizedBox(height: 8),
            ...recycledDishes.map((dish) => Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.7),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFA5D6A7)),
                  ),
                  child: Row(
                    children: [
                      Text(dish.emoji, style: const TextStyle(fontSize: 24)),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(dish.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(height: 2),
                            Text(dish.ingredientsUsed.join(' · '),
                                style: const TextStyle(fontSize: 10, color: Color(0xFF558B2F))),
                          ],
                        ),
                      ),
                      Column(
                        children: [
                          Text('${dish.prepMinutes}m',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF2E7D32))),
                          Text('₹${dish.savedInr}',
                              style: const TextStyle(fontSize: 10, color: Color(0xFF558B2F))),
                        ],
                      ),
                    ],
                  ),
                )),
          ],
        ],
      ),
    );
  }
}
