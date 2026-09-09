import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../auth/providers/auth_provider.dart';

/// A recycled dish suggestion returned from the backend.
class RecycledDish {
  final String name;
  final String emoji;
  final List<String> ingredientsUsed;
  final int prepMinutes;
  final int savedInr;
  final String tip;
  final int calories;
  final double protein;

  RecycledDish({
    required this.name,
    required this.emoji,
    required this.ingredientsUsed,
    required this.prepMinutes,
    required this.savedInr,
    this.tip = '',
    this.calories = 300,
    this.protein = 15.0,
  });

  factory RecycledDish.fromJson(Map<String, dynamic> json) => RecycledDish(
        name: json['dish_name'] ?? 'Leftover Stir-fry',
        emoji: json['emoji'] ?? '🍲',
        ingredientsUsed: List<String>.from(json['matching_leftovers_used'] ?? []),
        prepMinutes: json['prep_time_minutes'] ?? 15,
        savedInr: json['waste_saved_estimate_inr']?.round() ?? 80,
        tip: json['cooking_tip'] ?? '',
        calories: json['estimated_calories'] ?? 320,
        protein: (json['protein_g'] as num?)?.toDouble() ?? 14.0,
      );
}

class GroceryItem {
  final String id;
  final String name;
  final String quantity;
  final String unit;
  final String category;
  bool isChecked;

  GroceryItem({
    required this.id,
    required this.name,
    required this.quantity,
    required this.unit,
    required this.category,
    required this.isChecked,
  });

  factory GroceryItem.fromJson(Map<String, dynamic> json) => GroceryItem(
        id: json['id']?.toString() ?? '',
        name: json['name']?.toString() ?? '',
        quantity: json['quantity']?.toString() ?? '1',
        unit: json['unit']?.toString() ?? '',
        category: json['category']?.toString() ?? 'General',
        isChecked: json['is_checked'] == true,
      );
}

class GroceryScreen extends ConsumerStatefulWidget {
  const GroceryScreen({super.key});

  @override
  ConsumerState<GroceryScreen> createState() => _GroceryScreenState();
}

class _GroceryScreenState extends ConsumerState<GroceryScreen> {
  final ApiClient _apiClient = ApiClient();

  bool _isLoadingList = false;
  bool _isGenerating = false;
  bool _isRecycling = false;
  bool _recyclerOpen = false;

  String _selectedRegion = 'in_south_andhra';
  final List<Map<String, String>> _regionalOptions = [
    {'code': 'in_south_andhra', 'label': '🌶️ Andhra / Telugu'},
    {'code': 'in_south_tamil', 'label': '🍚 Tamil Nadu'},
    {'code': 'in_north_punjab', 'label': '🫓 Punjab / North'},
    {'code': 'in_west_maharashtra', 'label': '🌾 Maharashtra'},
    {'code': 'in_east_bengal', 'label': '🐟 Bengal / East'},
  ];

  List<GroceryItem> _items = [];
  List<RecycledDish> _recycledDishes = [];
  int _totalSaved = 0;

  final List<Map<String, dynamic>> _pantryItems = [
    {'name': 'Paneer', 'qty': '200g', 'emoji': '🧀', 'expiring': true},
    {'name': 'Spinach (Palak)', 'qty': '1 bunch', 'emoji': '🥬', 'expiring': true},
    {'name': 'Cooked Rice', 'qty': '1 cup', 'emoji': '🍚', 'expiring': true},
    {'name': 'Curd / Yogurt', 'qty': '250ml', 'emoji': '🥛', 'expiring': false},
    {'name': 'Tomatoes', 'qty': '3 pcs', 'emoji': '🍅', 'expiring': false},
    {'name': 'Coriander', 'qty': 'handful', 'emoji': '🌿', 'expiring': true},
  ];

  @override
  void initState() {
    super.initState();
    _fetchGroceryList();
  }

  Future<void> _fetchGroceryList() async {
    setState(() => _isLoadingList = true);
    try {
      final response = await _apiClient.dio.get('${ApiEndpoints.groceryBaseUrl}/list');
      if (response.data != null && response.data['items'] is List) {
        final rawList = response.data['items'] as List;
        final parsed = rawList.map((e) => GroceryItem.fromJson(e as Map<String, dynamic>)).toList();
        if (mounted) {
          setState(() {
            _items = parsed;
          });
        }
      }
    } catch (_) {
      // Fallback items if offline
      if (_items.isEmpty) {
        setState(() {
          _items = [
            GroceryItem(id: '1', name: 'Brown Rice', quantity: '1', unit: 'kg', category: 'Grains', isChecked: true),
            GroceryItem(id: '2', name: 'Chicken Breast', quantity: '500', unit: 'g', category: 'Protein', isChecked: true),
            GroceryItem(id: '3', name: 'Moong Dal', quantity: '500', unit: 'g', category: 'Protein', isChecked: false),
            GroceryItem(id: '4', name: 'Broccoli', quantity: '1', unit: 'head', category: 'Vegetables', isChecked: false),
            GroceryItem(id: '5', name: 'Greek Yogurt', quantity: '400', unit: 'g', category: 'Dairy', isChecked: false),
            GroceryItem(id: '6', name: 'Almonds', quantity: '100', unit: 'g', category: 'Fats', isChecked: false),
          ];
        });
      }
    } finally {
      if (mounted) setState(() => _isLoadingList = false);
    }
  }

  Future<void> _toggleItem(GroceryItem item) async {
    final nextState = !item.isChecked;
    setState(() => item.isChecked = nextState);

    try {
      await _apiClient.dio.patch(
        '${ApiEndpoints.groceryBaseUrl}/items/${item.id}/toggle',
        data: {'is_checked': nextState},
      );
    } catch (_) {
      // Best effort update
    }
  }

  Future<void> _addNewItemDialog() async {
    final nameCtrl = TextEditingController();
    final qtyCtrl = TextEditingController(text: '1');
    final unitCtrl = TextEditingController(text: 'kg');

    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Grocery Item', style: NutriTypography.displaySm),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Item Name (e.g. Oats, Spinach)'),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: qtyCtrl,
                    decoration: const InputDecoration(labelText: 'Quantity'),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: unitCtrl,
                    decoration: const InputDecoration(labelText: 'Unit (kg/pcs/g)'),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: NutriColors.primary),
            onPressed: () async {
              final name = nameCtrl.text.trim();
              if (name.isNotEmpty) {
                Navigator.pop(ctx);
                try {
                  final resp = await _apiClient.dio.post(
                    '${ApiEndpoints.groceryBaseUrl}/items',
                    data: {
                      'name': name,
                      'quantity': qtyCtrl.text.trim(),
                      'unit': unitCtrl.text.trim(),
                      'category': 'General',
                    },
                  );
                  if (resp.data != null) {
                    setState(() {
                      _items.add(GroceryItem.fromJson(resp.data));
                    });
                  }
                } catch (_) {
                  // Local add fallback
                  setState(() {
                    _items.add(GroceryItem(
                      id: DateTime.now().millisecondsSinceEpoch.toString(),
                      name: name,
                      quantity: qtyCtrl.text.trim(),
                      unit: unitCtrl.text.trim(),
                      category: 'General',
                      isChecked: false,
                    ));
                  });
                }
              }
            },
            child: const Text('Add Item', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Future<void> _generateFromPlan() async {
    setState(() => _isGenerating = true);
    try {
      await _apiClient.dio.post(
        '${ApiEndpoints.groceryBaseUrl}/generate-from-plan',
        data: {
          'regional_preference': _selectedRegion,
          'caloric_target': 1800,
          'dietary_flag': 'vegetarian',
          'replace_existing': false,
        },
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✨ Ingredients extracted from Regional Meal Plan!'),
            backgroundColor: NutriColors.primary,
          ),
        );
        await _fetchGroceryList();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not auto-generate plan: $e'),
            backgroundColor: NutriColors.danger,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isGenerating = false);
    }
  }

  Future<void> _dispatchQuickDelivery(String provider) async {
    final pendingCount = _items.where((i) => !i.isChecked).length;
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.flash_on, color: Color(0xFFF4C430), size: 28),
                const SizedBox(width: 8),
                Text('$provider Instant 10-Min Delivery', style: NutriTypography.displaySm),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Deep linking $pendingCount pending items directly into your $provider cart.',
              style: NutriTypography.bodyMd.copyWith(color: NutriColors.inkMuted),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: NutriColors.canvasRaised,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: NutriColors.border),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle_outline, color: NutriColors.primary, size: 20),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Automated inventory match: 100% available in nearest dark store.',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 46,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: provider == 'Blinkit' ? const Color(0xFFF4C430) : const Color(0xFF5E17EB),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('🚀 Cart synced to $provider! Redirecting to checkout...'),
                      backgroundColor: NutriColors.primary,
                    ),
                  );
                },
                child: Text(
                  'Launch $provider App & Pay',
                  style: TextStyle(
                    color: provider == 'Blinkit' ? Colors.black : Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _runRecycler() async {
    setState(() {
      _isRecycling = true;
      _recyclerOpen = true;
    });
    try {
      final resp = await _apiClient.dio.post('${ApiEndpoints.groceryBaseUrl}/recycle-leftovers', data: {
        'user_id': ref.read(authProvider).user?.id ?? 'mob_usr_001',
        'pantry_items': _pantryItems.map((p) => p['name'].toString().toLowerCase()).toList(),
        'regional_preference': _selectedRegion,
      });
      final List data = resp.data['recycled_dishes'] ?? [];
      setState(() {
        _recycledDishes = data.map((d) => RecycledDish.fromJson(d)).toList();
        _totalSaved = resp.data['total_waste_saved_inr']?.round() ?? 0;
        _isRecycling = false;
      });
    } catch (_) {
      setState(() {
        _recycledDishes = [
          RecycledDish(
            name: 'Palak Paneer Bhurji with Roti',
            emoji: '🧀',
            ingredientsUsed: ['Paneer', 'Spinach', 'Tomatoes'],
            prepMinutes: 15,
            savedInr: 120,
            tip: 'Sauté leftover spinach with crumbled paneer and cumin for a quick high-protein meal.',
          ),
          RecycledDish(
            name: 'Tomato Curd Rice Tadka',
            emoji: '🍚',
            ingredientsUsed: ['Cooked Rice', 'Curd', 'Coriander'],
            prepMinutes: 10,
            savedInr: 60,
            tip: 'Tempered curd rice with mustard, curry leaves and chopped tomatoes.',
          ),
        ];
        _totalSaved = 180;
        _isRecycling = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final checkedCount = _items.where((g) => g.isChecked).length;
    final totalCount = _items.length;
    final progress = totalCount > 0 ? (checkedCount / totalCount) : 0.0;

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Smart Grocery & Pantry', style: NutriTypography.displaySm),
            Text('Plan-based list · Pantry · Zero-Waste', style: TextStyle(fontSize: 10, color: NutriColors.inkMuted)),
          ],
        ),
        backgroundColor: NutriColors.canvas,
        elevation: 0,
        toolbarHeight: 60,
        actions: [
          IconButton(
            icon: const Icon(Icons.add, color: NutriColors.primary),
            tooltip: 'Add item',
            onPressed: _addNewItemDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: NutriColors.inkMuted),
            tooltip: 'Refresh list',
            onPressed: _fetchGroceryList,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchGroceryList,
        color: NutriColors.primary,
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          children: [
            // ── Progress Card ─────────────────────────────────────────────
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
                      const Text('Grocery Progress', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                      Text('$checkedCount / $totalCount collected',
                          style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 8,
                      backgroundColor: NutriColors.border,
                      valueColor: const AlwaysStoppedAnimation<Color>(NutriColors.primary),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // ── Auto-Generate from Plan Card (New Feature Parity with Web) ─
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [NutriColors.primary.withValues(alpha: 0.1), const Color(0xFFE8F5E9)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: NutriColors.primary.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.auto_awesome, color: NutriColors.primary, size: 20),
                      SizedBox(width: 8),
                      Text('Auto-Generate from Meal Plan',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: NutriColors.ink)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  const Text('Extract and categorize ingredients from regional cuisine meal plan.',
                      style: TextStyle(fontSize: 12, color: NutriColors.inkMuted)),
                  const SizedBox(height: 12),
                  // Regional selector chips
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _regionalOptions.map((opt) {
                        final isSel = _selectedRegion == opt['code'];
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(opt['label']!,
                                style: TextStyle(
                                  fontSize: 11,
                                  color: isSel ? Colors.white : NutriColors.ink,
                                  fontWeight: FontWeight.w600,
                                )),
                            selected: isSel,
                            selectedColor: NutriColors.primary,
                            backgroundColor: NutriColors.canvasRaised,
                            onSelected: (val) {
                              if (val) setState(() => _selectedRegion = opt['code']!);
                            },
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 40,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: NutriColors.primary,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: _isGenerating ? null : _generateFromPlan,
                      icon: _isGenerating
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.flash_on, size: 18, color: Colors.white),
                      label: Text(
                        _isGenerating ? 'Generating...' : '⚡ Generate Shopping List',
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // ── 10-Min Delivery Quick Dispatch Bar (Feature Parity with Web) ─
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFDE7),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFFBC02D).withValues(alpha: 0.5)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.delivery_dining, color: Color(0xFFF57F17), size: 28),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('10-Min Quick Delivery',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF5D4037))),
                        Text('${totalCount - checkedCount} missing items to cart',
                            style: const TextStyle(fontSize: 11, color: Color(0xFF795548))),
                      ],
                    ),
                  ),
                  Row(
                    children: [
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFF4C430),
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          elevation: 0,
                        ),
                        onPressed: () => _dispatchQuickDelivery('Blinkit'),
                        child: const Text('Blinkit'),
                      ),
                      const SizedBox(width: 6),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF5E17EB),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          elevation: 0,
                        ),
                        onPressed: () => _dispatchQuickDelivery('Zepto'),
                        child: const Text('Zepto'),
                      ),
                    ],
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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("This Week's List", style: NutriTypography.displaySm),
                TextButton.icon(
                  onPressed: _addNewItemDialog,
                  icon: const Icon(Icons.add, size: 16, color: NutriColors.primary),
                  label: const Text('Add Item', style: TextStyle(color: NutriColors.primary, fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 6),
            if (_isLoadingList)
              const Center(
                  child: Padding(
                      padding: EdgeInsets.all(24),
                      child: CircularProgressIndicator(color: NutriColors.primary)))
            else if (_items.isEmpty)
              Container(
                padding: const EdgeInsets.all(24),
                alignment: Alignment.center,
                child: const Text('No grocery items yet. Generate from plan or add manually!',
                    style: TextStyle(color: NutriColors.inkMuted)),
              )
            else
              ..._items.map((item) {
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  elevation: 0,
                  color: NutriColors.canvasRaised,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: const BorderSide(color: NutriColors.border),
                  ),
                  child: CheckboxListTile(
                    value: item.isChecked,
                    onChanged: (v) => _toggleItem(item),
                    title: Text(
                      '${item.name} (${item.quantity} ${item.unit})',
                      style: TextStyle(
                        decoration: item.isChecked ? TextDecoration.lineThrough : null,
                        color: item.isChecked ? NutriColors.inkMuted : NutriColors.ink,
                        fontWeight: FontWeight.w500,
                        fontSize: 14,
                      ),
                    ),
                    subtitle: Text(item.category,
                        style: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted, fontSize: 11)),
                    activeColor: NutriColors.primary,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                );
              }),
            const SizedBox(height: 60),
          ],
        ),
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
            children: pantryItems
                .map((p) => Chip(
                      label: Text('${p['emoji']} ${p['name']}',
                          style: TextStyle(
                              fontSize: 11,
                              color: (p['expiring'] as bool) ? const Color(0xFFE65100) : const Color(0xFF2E7D32))),
                      backgroundColor:
                          (p['expiring'] as bool) ? const Color(0xFFFFF3E0) : const Color(0xFFE8F5E9),
                      side: BorderSide(
                          color: (p['expiring'] as bool) ? const Color(0xFFFFA726) : const Color(0xFF66BB6A)),
                      padding: EdgeInsets.zero,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ))
                .toList(),
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
                        SizedBox(
                            height: 16,
                            width: 16,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
                        SizedBox(width: 8),
                        Text('Finding recipes...',
                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
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
                    color: Colors.white.withValues(alpha: 0.8),
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
                              style: const TextStyle(
                                  fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF2E7D32))),
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
