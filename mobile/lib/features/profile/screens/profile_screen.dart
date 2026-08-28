import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Form states
  final _nameController = TextEditingController(text: 'Ananya Sharma');
  final _emailController = TextEditingController(text: 'ananya@example.com');
  final _phoneController = TextEditingController(text: '+91 98765 43210');
  
  double _weightKg = 62.5;
  double _heightCm = 168.0;
  int _targetCalories = 1850;
  String _dietaryPreference = 'Vegetarian';
  List<String> _allergens = ['Peanuts', 'Lactose'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NutriColors.canvas,
      appBar: AppBar(
        backgroundColor: NutriColors.canvasRaised,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: NutriColors.ink),
          onPressed: () => context.pop(),
        ),
        title: const Text('Profile & Settings', style: NutriTypography.displaySm),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: NutriColors.danger),
            tooltip: 'Logout',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Logged out successfully')),
              );
              context.go('/login');
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: NutriColors.primary,
          unselectedLabelColor: NutriColors.inkMuted,
          indicatorColor: NutriColors.primary,
          indicatorWeight: 3,
          isScrollable: true,
          tabs: const [
            Tab(icon: Icon(Icons.person_outline, size: 20), text: 'Personal'),
            Tab(icon: Icon(Icons.restaurant_menu, size: 20), text: 'Diet & Goals'),
            Tab(icon: Icon(Icons.card_membership, size: 20), text: 'Plan & Billing'),
            Tab(icon: Icon(Icons.lock_outline, size: 20), text: 'Security'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildPersonalTab(),
          _buildDietTab(),
          _buildSubscriptionTab(),
          _buildSecurityTab(),
        ],
      ),
    );
  }

  Widget _buildPersonalTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Stack(
              children: [
                const CircleAvatar(
                  radius: 46,
                  backgroundImage: NetworkImage('https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&fit=crop&q=80'),
                ),
                Positioned(
                  right: 0,
                  bottom: 0,
                  child: CircleAvatar(
                    radius: 16,
                    backgroundColor: NutriColors.primary,
                    child: IconButton(
                      icon: const Icon(Icons.camera_alt, size: 16, color: Colors.white),
                      onPressed: () {},
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          _buildCard(
            title: 'Personal Information',
            children: [
              _buildTextField('Full Name', _nameController),
              const SizedBox(height: 14),
              _buildTextField('Email Address', _emailController, keyboardType: TextInputType.emailAddress),
              const SizedBox(height: 14),
              _buildTextField('Phone Number', _phoneController, keyboardType: TextInputType.phone),
            ],
          ),
          const SizedBox(height: 20),
          _buildCard(
            title: 'Biometrics & Body Composition',
            children: [
              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile(
                      label: 'Weight',
                      value: '${_weightKg.toStringAsFixed(1)} kg',
                      icon: Icons.monitor_weight_outlined,
                      onTap: () => _editNumber('Weight (kg)', _weightKg, (val) => setState(() => _weightKg = val)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricTile(
                      label: 'Height',
                      value: '${_heightCm.toInt()} cm',
                      icon: Icons.height,
                      onTap: () => _editNumber('Height (cm)', _heightCm, (val) => setState(() => _heightCm = val)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              _buildBmiIndicator(),
            ],
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: NutriColors.primary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Profile details updated successfully!')),
                );
              },
              child: const Text('Save Profile Changes', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDietTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCard(
            title: 'Caloric & Macro Targets',
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Daily Calorie Budget', style: TextStyle(fontWeight: FontWeight.w500, color: NutriColors.ink)),
                  Text('$_targetCalories kcal', style: const TextStyle(fontWeight: FontWeight.bold, color: NutriColors.primary, fontSize: 16)),
                ],
              ),
              Slider(
                value: _targetCalories.toDouble(),
                min: 1200,
                max: 3500,
                divisions: 46,
                activeColor: NutriColors.primary,
                onChanged: (val) => setState(() => _targetCalories = val.round()),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildCard(
            title: 'Dietary Preference',
            children: [
              Wrap(
                spacing: 8,
                children: ['Vegetarian', 'Vegan', 'Eggetarian', 'Non-Vegetarian', 'Keto', 'Jain'].map((diet) {
                  final isSelected = _dietaryPreference == diet;
                  return ChoiceChip(
                    label: Text(diet),
                    selected: isSelected,
                    selectedColor: NutriColors.primarySoft,
                    labelStyle: TextStyle(
                      color: isSelected ? NutriColors.primaryStrong : NutriColors.inkMuted,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                    onSelected: (selected) {
                      if (selected) setState(() => _dietaryPreference = diet);
                    },
                  );
                }).toList(),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildCard(
            title: 'Known Allergens & Avoidances',
            children: [
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _allergens.map((allergen) {
                  return Chip(
                    label: Text(allergen, style: const TextStyle(color: NutriColors.tertiary, fontWeight: FontWeight.w500)),
                    backgroundColor: NutriColors.tertiarySoft,
                    deleteIcon: const Icon(Icons.close, size: 16, color: NutriColors.tertiary),
                    onDeleted: () => setState(() => _allergens.remove(allergen)),
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                icon: const Icon(Icons.add, size: 16, color: NutriColors.primary),
                label: const Text('Add Allergen', style: TextStyle(color: NutriColors.primary)),
                onPressed: _showAddAllergenDialog,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSubscriptionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [NutriColors.primaryStrong, NutriColors.primary],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(color: NutriColors.primary.withValues(alpha: 0.25), blurRadius: 10, offset: const Offset(0, 4)),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('PREMIUM PRO', style: TextStyle(color: NutriColors.secondarySoft, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(20)),
                      child: const Text('ACTIVE', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11)),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text('AI Precision Nutritionist + Unlimited Wearable Sync', style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w500)),
                const SizedBox(height: 16),
                const Divider(color: Colors.white24),
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Next Billing Date', style: TextStyle(color: Colors.white70, fontSize: 13)),
                    Text('September 28, 2026', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          _buildCard(
            title: 'Your Referral Code',
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: NutriColors.canvas,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: NutriColors.border),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('NUTRI-VIP-2026', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, letterSpacing: 1.5, color: NutriColors.primary)),
                    IconButton(
                      icon: const Icon(Icons.copy, size: 20, color: NutriColors.primary),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Referral code copied to clipboard!')),
                        );
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              const Text('Share with friends to earn 1 free month for every referral.', style: TextStyle(color: NutriColors.inkMuted, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSecurityTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        _buildCard(
          title: 'Account Security',
          children: [
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.lock_reset, color: NutriColors.primary),
              title: const Text('Change Password'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.fingerprint, color: NutriColors.primary),
              title: const Text('Biometric Authentication (FaceID/Fingerprint)'),
              trailing: Switch(
                value: true,
                activeThumbColor: NutriColors.primary,
                onChanged: (val) {},
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        _buildCard(
          title: 'Data & Privacy',
          children: [
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.download, color: NutriColors.inkMuted),
              title: const Text('Export My Health Data (GDPR/DISHA)'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            const Divider(),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.delete_outline, color: NutriColors.danger),
              title: const Text('Delete Account', style: TextStyle(color: NutriColors.danger)),
              trailing: const Icon(Icons.chevron_right, color: NutriColors.danger),
              onTap: () {},
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCard({required String title, required List<Widget> children}) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: NutriColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: NutriColors.ink)),
          const SizedBox(height: 14),
          ...children,
        ],
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, {TextInputType keyboardType = TextInputType.text}) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: NutriColors.inkMuted, fontSize: 13),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: NutriColors.border)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      ),
    );
  }

  Widget _buildMetricTile({required String label, required String value, required IconData icon, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: NutriColors.canvas,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: NutriColors.border),
        ),
        child: Row(
          children: [
            Icon(icon, color: NutriColors.primary, size: 20),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(color: NutriColors.inkMuted, fontSize: 11)),
                Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: NutriColors.ink)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBmiIndicator() {
    final heightM = _heightCm / 100;
    final bmi = _weightKg / (heightM * heightM);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: NutriColors.primarySoft,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text('Calculated BMI', style: TextStyle(color: NutriColors.primaryStrong, fontWeight: FontWeight.w500)),
          Text('${bmi.toStringAsFixed(1)} (Normal)', style: const TextStyle(color: NutriColors.primaryStrong, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  void _editNumber(String title, double currentVal, Function(double) onSave) {
    final textController = TextEditingController(text: currentVal.toString());
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Edit $title'),
        content: TextField(
          controller: textController,
          keyboardType: TextInputType.number,
          autofocus: true,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              final val = double.tryParse(textController.text);
              if (val != null) onSave(val);
              Navigator.pop(ctx);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showAddAllergenDialog() {
    final textController = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Allergen / Avoidance'),
        content: TextField(
          controller: textController,
          decoration: const InputDecoration(hintText: 'e.g. Shellfish, Gluten, Soy'),
          autofocus: true,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              if (textController.text.trim().isNotEmpty) {
                setState(() => _allergens.add(textController.text.trim()));
              }
              Navigator.pop(ctx);
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}
