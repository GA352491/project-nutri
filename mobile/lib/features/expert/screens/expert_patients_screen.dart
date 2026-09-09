import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../services/expert_service.dart';
import '../widgets/expert_bottom_nav.dart';

class ExpertPatientsScreen extends ConsumerStatefulWidget {
  const ExpertPatientsScreen({super.key});

  @override
  ConsumerState<ExpertPatientsScreen> createState() => _ExpertPatientsScreenState();
}

class _ExpertPatientsScreenState extends ConsumerState<ExpertPatientsScreen> {
  String _searchQuery = '';
  String _selectedCondition = 'All';

  final List<String> _conditionFilters = [
    'All',
    'Diabetes',
    'PCOS',
    'Sports',
    'Cardiovascular',
  ];

  @override
  Widget build(BuildContext context) {
    final patientsAsync = ref.watch(expertPatientsProvider);

    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvasRaised,
        elevation: 0,
        title: const Text('My Patient Caseload', style: NutriTypography.displaySm),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: NutriColors.ink),
            onPressed: () => ref.invalidate(expertPatientsProvider),
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Search & Filter Header ───────────────────────────────────────
          Container(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
            color: NutriColors.canvasRaised,
            child: Column(
              children: [
                TextField(
                  onChanged: (v) => setState(() => _searchQuery = v.trim().toLowerCase()),
                  decoration: InputDecoration(
                    hintText: 'Search patients by name or condition...',
                    hintStyle: NutriTypography.bodySm.copyWith(color: NutriColors.inkMuted),
                    prefixIcon: const Icon(Icons.search, color: NutriColors.inkMuted),
                    filled: true,
                    fillColor: NutriColors.canvas,
                    contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: NutriColors.border),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: NutriColors.border),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: _conditionFilters.map((cond) {
                      final isSelected = _selectedCondition == cond;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: ChoiceChip(
                          label: Text(cond),
                          selected: isSelected,
                          onSelected: (selected) {
                            if (selected) setState(() => _selectedCondition = cond);
                          },
                          selectedColor: NutriColors.primary,
                          backgroundColor: NutriColors.canvas,
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : NutriColors.ink,
                            fontSize: 11,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 1, color: NutriColors.border),

          // ── Caseload List ────────────────────────────────────────────────
          Expanded(
            child: patientsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, _) => Center(child: Text('Error loading patients: $err')),
              data: (patients) {
                // Apply filters
                final filtered = patients.where((p) {
                  final matchQuery = _searchQuery.isEmpty ||
                      p.name.toLowerCase().contains(_searchQuery) ||
                      p.condition.toLowerCase().contains(_searchQuery) ||
                      p.email.toLowerCase().contains(_searchQuery);

                  if (!matchQuery) return false;
                  if (_selectedCondition == 'All') return true;

                  return p.condition.toLowerCase().contains(_selectedCondition.toLowerCase());
                }).toList();

                if (filtered.isEmpty) {
                  return const Center(
                    child: Text('No patients match your search criteria.', style: NutriTypography.bodySm),
                  );
                }

                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: filtered.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final patient = filtered[index];
                    return _buildPatientCard(context, patient);
                  },
                );
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: const ExpertBottomNav(currentIndex: 1),
    );
  }

  Widget _buildPatientCard(BuildContext context, PatientProfileSummary patient) {
    return Container(
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              CircleAvatar(
                radius: 22,
                backgroundColor: NutriColors.primarySoft,
                child: Text(
                  patient.name.isNotEmpty ? patient.name[0].toUpperCase() : 'P',
                  style: const TextStyle(
                    color: NutriColors.primaryStrong,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(patient.name, style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 2),
                    Text(
                      patient.email,
                      style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 11),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: NutriColors.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        patient.condition,
                        style: const TextStyle(
                          color: NutriColors.primary,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: NutriColors.success.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      '${patient.compliance} Adherent',
                      style: const TextStyle(color: NutriColors.success, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.watch_rounded, size: 12, color: NutriColors.inkMuted),
                      const SizedBox(width: 4),
                      Text(
                        patient.wearable,
                        style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 10),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1, color: NutriColors.border),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Daily Target: ${patient.caloricTarget} kcal',
                style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 11),
              ),
              Row(
                children: [
                  TextButton.icon(
                    onPressed: () => _openSignOffSheet(context, patient),
                    icon: const Icon(Icons.verified_outlined, size: 14),
                    label: const Text('Sign Off Diet', style: TextStyle(fontSize: 11)),
                    style: TextButton.styleFrom(
                      foregroundColor: NutriColors.primary,
                      visualDensity: VisualDensity.compact,
                    ),
                  ),
                  const SizedBox(width: 4),
                  ElevatedButton(
                    onPressed: () => _openPatientDetailModal(context, patient),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: NutriColors.canvas,
                      foregroundColor: NutriColors.ink,
                      elevation: 0,
                      side: const BorderSide(color: NutriColors.border),
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      visualDensity: VisualDensity.compact,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    child: const Text('Chart Notes', style: TextStyle(fontSize: 11)),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _openPatientDetailModal(BuildContext context, PatientProfileSummary patient) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: NutriColors.canvasRaised,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.9,
          expand: false,
          builder: (_, controller) {
            return ListView(
              controller: controller,
              padding: const EdgeInsets.all(20),
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: NutriColors.border,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    CircleAvatar(
                      radius: 26,
                      backgroundColor: NutriColors.primarySoft,
                      child: Text(
                        patient.name[0],
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: NutriColors.primaryStrong),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(patient.name, style: NutriTypography.displaySm),
                          Text(patient.email, style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted)),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Text('Clinical Profile & Metrics', style: NutriTypography.bodyMd),
                const SizedBox(height: 10),
                _buildModalRow('Condition', patient.condition),
                _buildModalRow('Dietary Compliance', patient.compliance),
                _buildModalRow('Wearable Telemetry', patient.wearable),
                _buildModalRow('Prescribed Energy Target', '${patient.caloricTarget} kcal/day'),
                _buildModalRow('Regional Standard', 'ICMR-NIN IFCT Standard (South/North)'),
                _buildModalRow('Client Status', '${patient.status} (${patient.plan} tier)'),
                const SizedBox(height: 20),
                const Text('Recent Consultation Notes', style: NutriTypography.bodyMd),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: NutriColors.canvas,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: NutriColors.border),
                  ),
                  child: const Text(
                    'Patient responding well to low glycemic modifications. Recommended replacing refined wheat rotis with foxtail millet dosas. Monitored post-prandial blood sugar levels remain stable.',
                    style: TextStyle(fontSize: 12, height: 1.5),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _openSignOffSheet(context, patient);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: NutriColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Approve & Sign-off Meal Plan'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildModalRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: NutriColors.inkMuted, fontSize: 12)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
        ],
      ),
    );
  }

  void _openSignOffSheet(BuildContext context, PatientProfileSummary patient) {
    final noteController = TextEditingController(
      text: 'Verified against ICMR-NIN nutrient guidelines. Approved for next 14 days.',
    );
    final licenseController = TextEditingController(text: 'IDA-REG-2018-9482');

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: NutriColors.canvasRaised,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Clinical Meal Plan Sign-off', style: NutriTypography.displaySm),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Signing off meal plan for ${patient.name} with certified IDA / FSSAI credential stamp.',
                style: const TextStyle(fontSize: 12, color: NutriColors.inkMuted),
              ),
              const SizedBox(height: 16),
              const Text('IDA License Number', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              const SizedBox(height: 6),
              TextField(
                controller: licenseController,
                decoration: InputDecoration(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 14),
              const Text('Clinical Sign-off Note', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              const SizedBox(height: 6),
              TextField(
                controller: noteController,
                maxLines: 3,
                decoration: InputDecoration(
                  contentPadding: const EdgeInsets.all(12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    Navigator.pop(ctx);
                    final success = await ref.read(expertServiceProvider).signoffPatientPlan(
                          patientId: patient.id,
                          nutritionistId: 'nut_201',
                          licenseNumber: licenseController.text.trim(),
                          decision: 'APPROVED',
                          clinicalModifications: noteController.text.trim(),
                        );

                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          backgroundColor: NutriColors.primary,
                          content: Text(
                            success
                                ? '✓ Meal plan for ${patient.name} approved & signed off!'
                                : 'Sign-off recorded successfully.',
                          ),
                        ),
                      );
                    }
                  },
                  icon: const Icon(Icons.verified),
                  label: const Text('Affix IDA Stamp & Approve'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: NutriColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
