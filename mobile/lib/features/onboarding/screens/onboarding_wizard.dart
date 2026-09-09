import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/button.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../subscriptions/services/payment_service.dart';
import '../../subscriptions/widgets/payment_gateway_sheet.dart';

class OnboardingWizard extends ConsumerStatefulWidget {
  const OnboardingWizard({super.key});

  @override
  ConsumerState<OnboardingWizard> createState() => _OnboardingWizardState();
}

class _OnboardingWizardState extends ConsumerState<OnboardingWizard> {
  final PageController _pageController = PageController();
  int _currentIndex = 0;
  bool _isSaving = false;

  final int _totalPages = 5;

  // ── Step 1 State: Demographics ─────────────────────────────────────────────
  final _ageController = TextEditingController(text: '28');
  final _weightController = TextEditingController(text: '68');
  final _heightController = TextEditingController(text: '172');
  String _gender = 'Male';

  // ── Step 2 State: Diet & Regional Palate ────────────────────────────────────
  String _dietaryPreference = 'Vegetarian';
  String _regionalPreference = 'in_south_andhra';

  // ── Step 3 State: Goals & Activity ─────────────────────────────────────────
  String _primaryGoal = 'Weight Management & Fat Loss';

  // ── Step 4 State: Digital Pantry ───────────────────────────────────────────
  final List<String> _pantryItems = [
    'Rice',
    'Toor Dal',
    'Olive Oil',
    'Onions',
    'Garlic',
    'Tomatoes',
    'Ragi Flour',
    'Curd',
  ];
  final _pantryAddController = TextEditingController();

  // ── Step 5 State: Subscription Tier ────────────────────────────────────────
  String _selectedTier = 'pro';

  @override
  void dispose() {
    _pageController.dispose();
    _ageController.dispose();
    _weightController.dispose();
    _heightController.dispose();
    _pantryAddController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentIndex < _totalPages - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _handleCompleteOnboarding();
    }
  }

  void _prevPage() {
    if (_currentIndex > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _handleCompleteOnboarding() async {
    final paymentService = ref.read(paymentServiceProvider);

    if (_selectedTier == 'free') {
      await _syncAndFinish();
      return;
    }

    // Pro or Family tier selected: open Payment Gateway Bottom Sheet
    final chosenPlan = paymentService.availablePlans.firstWhere(
      (p) => p.tier == _selectedTier,
      orElse: () => paymentService.availablePlans[1],
    );

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => PaymentGatewaySheet(
        plan: chosenPlan,
        onPaymentSuccess: (paymentMethodId) async {
          Navigator.pop(ctx); // Close sheet
          setState(() => _isSaving = true);

          // 1. Activate subscription on backend
          await paymentService.activateSubscription(
            tier: _selectedTier,
            paymentMethodId: paymentMethodId,
          );

          // 2. Persist profile data to backend
          await _syncAndFinish();
        },
      ),
    );
  }

  Future<void> _syncAndFinish() async {
    setState(() => _isSaving = true);

    final paymentService = ref.read(paymentServiceProvider);
    final age = int.tryParse(_ageController.text.trim()) ?? 28;
    final weight = double.tryParse(_weightController.text.trim()) ?? 68.0;
    final height = double.tryParse(_heightController.text.trim()) ?? 172.0;

    await paymentService.updateProfile(
      age: age,
      weightKg: weight,
      heightCm: height,
      dietaryPreference: _dietaryPreference.toLowerCase(),
      regionalPreference: _regionalPreference,
      primaryGoal: _primaryGoal,
      pantryItems: _pantryItems,
    );

    setState(() => _isSaving = false);
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: NutriColors.primary,
        content: Text('✓ Profile configured and ${_selectedTier.toUpperCase()} activated!'),
      ),
    );

    context.go('/today');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NutriColors.canvas,
      body: SafeArea(
        child: Column(
          children: [
            // Segmented Progress Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
              child: Column(
                children: [
                  Row(
                    children: List.generate(
                      _totalPages,
                      (index) => Expanded(
                        child: Container(
                          margin: const EdgeInsets.symmetric(horizontal: 3.0),
                          height: 5,
                          decoration: BoxDecoration(
                            color: index <= _currentIndex
                                ? NutriColors.primary
                                : NutriColors.border,
                            borderRadius: BorderRadius.circular(3),
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'STEP ${_currentIndex + 1} OF $_totalPages',
                    style: NutriTypography.dataSm.copyWith(
                      color: NutriColors.primary,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.0,
                    ),
                  ),
                ],
              ),
            ),

            // Onboarding Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (index) => setState(() => _currentIndex = index),
                children: [
                  _buildStepDemographics(),
                  _buildStepRegionalDiet(),
                  _buildStepGoals(),
                  _buildStepPantry(),
                  _buildStepSubscriptionPlans(),
                ],
              ),
            ),

            // Bottom Navigation Actions
            Container(
              padding: const EdgeInsets.all(20.0),
              decoration: BoxDecoration(
                color: NutriColors.canvasRaised,
                border: Border(top: BorderSide(color: NutriColors.border.withValues(alpha: 0.6))),
              ),
              child: Row(
                children: [
                  if (_currentIndex > 0) ...[
                    NutriButton(
                      text: 'Back',
                      variant: ButtonVariant.outline,
                      isFullWidth: false,
                      onPressed: _prevPage,
                    ),
                    const SizedBox(width: 14),
                  ],
                  Expanded(
                    child: NutriButton(
                      text: _currentIndex == _totalPages - 1
                          ? (_selectedTier == 'free' ? 'Get Started' : 'Subscribe & Continue')
                          : 'Continue',
                      isLoading: _isSaving,
                      onPressed: _nextPage,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Step 1: Demographics ───────────────────────────────────────────────────
  Widget _buildStepDemographics() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('About You', style: NutriTypography.displayLg),
          const SizedBox(height: 6),
          const Text('Precision clinical nutrition calibrated to your biometric metrics.', style: NutriTypography.bodyMd),
          const SizedBox(height: 24),
          const Text('Gender Identity', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          const SizedBox(height: 8),
          Row(
            children: ['Male', 'Female', 'Non-Binary'].map((g) {
              final isSel = _gender == g;
              return Padding(
                padding: const EdgeInsets.only(right: 8.0),
                child: ChoiceChip(
                  label: Text(g),
                  selected: isSel,
                  onSelected: (val) {
                    if (val) setState(() => _gender = g);
                  },
                  selectedColor: NutriColors.primary,
                  backgroundColor: NutriColors.canvasRaised,
                  labelStyle: TextStyle(
                    color: isSel ? Colors.white : NutriColors.ink,
                    fontWeight: isSel ? FontWeight.bold : FontWeight.normal,
                    fontSize: 12,
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 20),
          TextFormField(
            controller: _ageController,
            decoration: InputDecoration(
              labelText: 'Age (Years)',
              prefixIcon: const Icon(Icons.cake_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _weightController,
            decoration: InputDecoration(
              labelText: 'Current Weight (kg)',
              prefixIcon: const Icon(Icons.monitor_weight_outlined),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _heightController,
            decoration: InputDecoration(
              labelText: 'Height (cm)',
              prefixIcon: const Icon(Icons.height),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
            keyboardType: TextInputType.number,
          ),
        ],
      ),
    );
  }

  // ── Step 2: Regional ICMR-NIN Palate ────────────────────────────────────────
  Widget _buildStepRegionalDiet() {
    final diets = ['Vegetarian', 'Vegan', 'Omnivore', 'Eggetarian', 'Pescatarian'];
    final regions = [
      {
        'id': 'in_south_andhra',
        'name': 'South Indian (Andhra / Telangana)',
        'desc': 'High-protein pesarattu, ragi mudda, pappu & cold-pressed sesame oil.',
      },
      {
        'id': 'in_south_tamilnadu',
        'name': 'South Indian (Tamil Nadu / Kerala)',
        'desc': 'Millet adai, moringa sambhar, sundal & virgin coconut oil.',
      },
      {
        'id': 'in_north_punjab',
        'name': 'North Indian (Punjab / Delhi / UP)',
        'desc': 'Jammu rajma, low-oil paneer bhurji, missi roti & saag.',
      },
      {
        'id': 'in_west_maharashtra',
        'name': 'West Indian (Maharashtra / Gujarat)',
        'desc': 'Sprouted matki usal, jowar bhakri, methi thepla & sattu.',
      },
      {
        'id': 'global',
        'name': 'Global / Mediterranean Balanced',
        'desc': 'Whole grain sourdough, Greek salads, quinoa & extra-virgin olive oil.',
      },
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Diet & Regional Palate', style: NutriTypography.displayLg),
          const SizedBox(height: 6),
          const Text('Select your staple regional diet for accurate ICMR-NIN nutrient profiles.', style: NutriTypography.bodyMd),
          const SizedBox(height: 20),
          const Text('Dietary Category', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: diets.map((d) {
                final isSel = _dietaryPreference == d;
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: ChoiceChip(
                    label: Text(d),
                    selected: isSel,
                    onSelected: (val) {
                      if (val) setState(() => _dietaryPreference = d);
                    },
                    selectedColor: NutriColors.primary,
                    backgroundColor: NutriColors.canvasRaised,
                    labelStyle: TextStyle(
                      color: isSel ? Colors.white : NutriColors.ink,
                      fontWeight: isSel ? FontWeight.bold : FontWeight.normal,
                      fontSize: 12,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 24),
          const Text('Regional Cuisine Focus', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          const SizedBox(height: 10),
          ...regions.map((r) {
            final isSel = _regionalPreference == r['id'];
            return InkWell(
              onTap: () => setState(() => _regionalPreference = r['id']!),
              borderRadius: BorderRadius.circular(12),
              child: Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: isSel ? NutriColors.primarySoft.withValues(alpha: 0.35) : NutriColors.canvasRaised,
                  border: Border.all(
                    color: isSel ? NutriColors.primary : NutriColors.border,
                    width: isSel ? 2 : 1,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            r['name']!,
                            style: NutriTypography.bodySm.copyWith(
                              fontWeight: FontWeight.bold,
                              color: isSel ? NutriColors.primaryStrong : NutriColors.ink,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(r['desc']!, style: const TextStyle(fontSize: 11, color: NutriColors.inkMuted)),
                        ],
                      ),
                    ),
                    if (isSel)
                      const Icon(Icons.check_circle_rounded, color: NutriColors.primary, size: 20),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  // ── Step 3: Health Goals ───────────────────────────────────────────────────
  Widget _buildStepGoals() {
    final goals = [
      {'title': 'Weight Management & Fat Loss', 'desc': 'Calibrated caloric deficit with satiety fiber'},
      {'title': 'Clinical Condition Support', 'desc': 'Low GI for Diabetes, anti-androgen for PCOS, DASH for BP'},
      {'title': 'Sports Hypertrophy & Muscle Gain', 'desc': 'High protein targets (1.6 - 2.0g/kg) and clean carbs'},
      {'title': 'Gut Microbiome & Immunity', 'desc': 'Diverse fermented staples, prebiotic fiber and low FODMAP'},
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Health Goal', style: NutriTypography.displayLg),
          const SizedBox(height: 6),
          const Text('What primary metabolic outcome do you want to accomplish?', style: NutriTypography.bodyMd),
          const SizedBox(height: 20),
          ...goals.map((g) {
            final isSel = _primaryGoal == g['title'];
            return InkWell(
              onTap: () => setState(() => _primaryGoal = g['title']!),
              borderRadius: BorderRadius.circular(14),
              child: Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isSel ? NutriColors.primarySoft.withValues(alpha: 0.35) : NutriColors.canvasRaised,
                  border: Border.all(
                    color: isSel ? NutriColors.primary : NutriColors.border,
                    width: isSel ? 2 : 1,
                  ),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            g['title']!,
                            style: NutriTypography.bodyMd.copyWith(
                              fontWeight: FontWeight.bold,
                              color: isSel ? NutriColors.primaryStrong : NutriColors.ink,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(g['desc']!, style: const TextStyle(fontSize: 12, color: NutriColors.inkMuted)),
                        ],
                      ),
                    ),
                    if (isSel)
                      const Icon(Icons.check_circle_rounded, color: NutriColors.primary, size: 22),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  // ── Step 4: Digital Pantry ─────────────────────────────────────────────────
  Widget _buildStepPantry() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Smart Digital Pantry', style: NutriTypography.displayLg),
          const SizedBox(height: 6),
          const Text('Tell us what is in your kitchen right now to generate zero-waste meal plans.', style: NutriTypography.bodyMd),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _pantryAddController,
                  decoration: InputDecoration(
                    hintText: 'Add an ingredient (e.g. Paneer, Oats)...',
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.add_circle, color: NutriColors.primary, size: 32),
                onPressed: () {
                  final text = _pantryAddController.text.trim();
                  if (text.isNotEmpty && !_pantryItems.contains(text)) {
                    setState(() => _pantryItems.add(text));
                    _pantryAddController.clear();
                  }
                },
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Text('Current Pantry Inventory', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _pantryItems.map((item) {
              return Chip(
                label: Text(item),
                backgroundColor: NutriColors.canvasRaised,
                side: const BorderSide(color: NutriColors.border),
                deleteIcon: const Icon(Icons.close, size: 16),
                onDeleted: () => setState(() => _pantryItems.remove(item)),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // ── Step 5: Subscription Tiers & Plans ─────────────────────────────────────
  Widget _buildStepSubscriptionPlans() {
    final plans = ref.read(paymentServiceProvider).availablePlans;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Select Your Plan', style: NutriTypography.displayLg),
          const SizedBox(height: 6),
          const Text('Choose the right level of clinical guidance and AI precision.', style: NutriTypography.bodyMd),
          const SizedBox(height: 20),
          ...plans.map((plan) {
            final isSel = _selectedTier == plan.tier;
            return InkWell(
              onTap: () => setState(() => _selectedTier = plan.tier),
              borderRadius: BorderRadius.circular(16),
              child: Container(
                margin: const EdgeInsets.only(bottom: 14),
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: isSel ? NutriColors.primarySoft.withValues(alpha: 0.35) : NutriColors.canvasRaised,
                  border: Border.all(
                    color: isSel ? NutriColors.primary : NutriColors.border,
                    width: isSel ? 2.5 : 1,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: isSel
                      ? [
                          BoxShadow(
                            color: NutriColors.primary.withValues(alpha: 0.12),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ]
                      : null,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Text(plan.name, style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold)),
                            if (plan.isPopular) ...[
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: NutriColors.secondary,
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Text(
                                  'RECOMMENDED',
                                  style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ],
                        ),
                        Text(
                          '${plan.price}${plan.period}',
                          style: const TextStyle(
                            fontFamily: NutriTypography.displayFont,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: NutriColors.primary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(plan.description, style: const TextStyle(fontSize: 12, color: NutriColors.inkMuted)),
                    const SizedBox(height: 12),
                    const Divider(height: 1, color: NutriColors.border),
                    const SizedBox(height: 10),
                    ...plan.features.map((f) => Padding(
                          padding: const EdgeInsets.only(bottom: 4.0),
                          child: Row(
                            children: [
                              const Icon(Icons.check_circle_rounded, size: 14, color: NutriColors.success),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(f, style: const TextStyle(fontSize: 11, color: NutriColors.ink)),
                              ),
                            ],
                          ),
                        )),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
