import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../../auth/providers/auth_provider.dart';
import '../services/expert_service.dart';
import '../widgets/expert_bottom_nav.dart';

class ExpertSettingsScreen extends ConsumerStatefulWidget {
  const ExpertSettingsScreen({super.key});

  @override
  ConsumerState<ExpertSettingsScreen> createState() => _ExpertSettingsScreenState();
}

class _ExpertSettingsScreenState extends ConsumerState<ExpertSettingsScreen> {
  late TextEditingController _nameController;
  late TextEditingController _bioController;
  late TextEditingController _rateController;
  late TextEditingController _licenseController;

  bool _instantConsultEnabled = true;
  bool _isSaving = false;

  final List<String> _specialties = [
    'Diabetes Care (ICMR-NIN)',
    'PCOS & Hormonal Health',
    'Sports Nutrition & Hypertrophy',
    'Gut Microbiome & IBS',
    'Cardiovascular & Hypertension',
  ];

  @override
  void initState() {
    super.initState();
    final user = ref.read(authProvider).user;
    _nameController = TextEditingController(text: user?.name ?? 'Dr. Sarah Jenkins, RD');
    _bioController = TextEditingController(
      text: 'Clinical Dietitian & Diabetes Specialist with 9+ years experience prescribing medical nutrition therapy.',
    );
    _rateController = TextEditingController(text: '120');
    _licenseController = TextEditingController(text: 'IDA-REG-2018-9482');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _bioController.dispose();
    _rateController.dispose();
    _licenseController.dispose();
    super.dispose();
  }

  Future<void> _saveSettings() async {
    setState(() => _isSaving = true);
    final rate = double.tryParse(_rateController.text.trim()) ?? 100.0;

    await ref.read(expertServiceProvider).updateExpertProfile(
          nutritionistId: 'nut_201',
          name: _nameController.text.trim(),
          bio: _bioController.text.trim(),
          hourlyRate: rate,
          specialties: _specialties,
          licenseNumber: _licenseController.text.trim(),
        );

    setState(() => _isSaving = false);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: NutriColors.primary,
          content: Text('✓ Practice profile and consultation rates saved!'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).user;

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvasRaised,
        elevation: 0,
        title: const Text('Practice Settings & Credentials', style: NutriTypography.displaySm),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded, color: NutriColors.danger),
            onPressed: () async {
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Provider Card ─────────────────────────────────────────────
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: NutriColors.canvasRaised,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: NutriColors.border),
              ),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: NutriColors.primary, width: 2),
                      image: const DecorationImage(
                        image: NetworkImage(
                          'https://images.unsplash.com/photo-1594824813580-c1fd9f939e6a?w=200&q=80',
                        ),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _nameController.text,
                          style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          user?.email ?? 'expert@nutriplan.local',
                          style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted),
                        ),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: NutriColors.success.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.verified, color: NutriColors.success, size: 12),
                              SizedBox(width: 4),
                              Text(
                                'IDA Certified Clinical Dietitian',
                                style: TextStyle(
                                  color: NutriColors.success,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
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
            ),

            const SizedBox(height: 20),

            // ── IDA Credentials ───────────────────────────────────────────
            const Text('Official Credential Seal', style: NutriTypography.displaySm),
            const SizedBox(height: 10),
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
                  const Text('IDA Registration Number', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _licenseController,
                    decoration: InputDecoration(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      prefixIcon: const Icon(Icons.card_membership_rounded, size: 18),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text('Issuing Body', style: TextStyle(fontSize: 11, color: NutriColors.inkMuted)),
                  const SizedBox(height: 2),
                  const Text('Indian Dietetic Association (IDA) · FSSAI Regulated', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  const Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: [
                      Chip(
                        avatar: Icon(Icons.check_circle, color: NutriColors.success, size: 16),
                        label: Text('M.Sc Clinical Nutrition (NIN)', style: TextStyle(fontSize: 11)),
                        backgroundColor: NutriColors.canvas,
                      ),
                      Chip(
                        avatar: Icon(Icons.check_circle, color: NutriColors.success, size: 16),
                        label: Text('Certified Diabetes Educator (CDE)', style: TextStyle(fontSize: 11)),
                        backgroundColor: NutriColors.canvas,
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ── Consultation Details & Rate ───────────────────────────────
            const Text('Consultation & Pricing', style: NutriTypography.displaySm),
            const SizedBox(height: 10),
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
                      const Text('Accept Instant Consultations', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      Switch(
                        value: _instantConsultEnabled,
                        activeThumbColor: NutriColors.primary,
                        onChanged: (val) => setState(() => _instantConsultEnabled = val),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Text('Hourly Consultation Rate (USD)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _rateController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      prefixText: '\$ ',
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                  const SizedBox(height: 14),
                  const Text('Professional Clinical Bio', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _bioController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      contentPadding: const EdgeInsets.all(12),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ── Save Button ───────────────────────────────────────────────
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveSettings,
                icon: _isSaving
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.save_rounded),
                label: Text(_isSaving ? 'Saving Changes...' : 'Save Practice Profile'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: NutriColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),

            const SizedBox(height: 16),

            // ── Demo Switcher (Patient View) ──────────────────────────────
            Center(
              child: TextButton.icon(
                onPressed: () => context.go('/today'),
                icon: const Icon(Icons.swap_horiz_rounded, size: 16),
                label: const Text('Preview Patient App Mode'),
                style: TextButton.styleFrom(foregroundColor: NutriColors.inkMuted),
              ),
            ),

            const SizedBox(height: 20),
          ],
        ),
      ),
      bottomNavigationBar: const ExpertBottomNav(currentIndex: 3),
    );
  }
}
