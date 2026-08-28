import 'package:flutter/material.dart';
import '../../../shared/widgets/button.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import 'package:go_router/go_router.dart';

class OnboardingWizard extends StatefulWidget {
  const OnboardingWizard({super.key});

  @override
  State<OnboardingWizard> createState() => _OnboardingWizardState();
}

class _OnboardingWizardState extends State<OnboardingWizard> {
  final PageController _pageController = PageController();
  int _currentIndex = 0;
  bool _isSaving = false;

  final int _totalPages = 4;

  void _nextPage() {
    if (_currentIndex < _totalPages - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _finishOnboarding();
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

  void _finishOnboarding() async {
    setState(() => _isSaving = true);
    await Future.delayed(const Duration(milliseconds: 800));
    setState(() => _isSaving = false);
    if (!mounted) return;
    context.go('/today');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Progress Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
              child: Row(
                children: List.generate(
                  _totalPages,
                  (index) => Expanded(
                    child: Container(
                      margin: const EdgeInsets.only(right: 8.0),
                      height: 4,
                      decoration: BoxDecoration(
                        color: index <= _currentIndex
                            ? NutriColors.primary
                            : NutriColors.border,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                )..removeLast(),
              ),
            ),
            
            // Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (index) {
                  setState(() {
                    _currentIndex = index;
                  });
                },
                children: [
                  _buildStepDemographics(),
                  _buildStepDiet(),
                  _buildStepGoals(),
                  _buildStepPantry(),
                ],
              ),
            ),
            
            // Bottom Actions
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Row(
                children: [
                  if (_currentIndex > 0) ...[
                    NutriButton(
                      text: 'Back',
                      variant: ButtonVariant.outline,
                      isFullWidth: false,
                      onPressed: _prevPage,
                    ),
                    const SizedBox(width: 16),
                  ],
                  if (_currentIndex == _totalPages - 1) ...[
                    Expanded(
                      child: NutriButton(
                        text: 'Skip',
                        variant: ButtonVariant.ghost,
                        onPressed: _finishOnboarding,
                      ),
                    ),
                    const SizedBox(width: 16),
                  ],
                  Expanded(
                    flex: 2,
                    child: NutriButton(
                      text: _currentIndex == _totalPages - 1 ? 'Save Pantry' : 'Continue',
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

  Widget _buildStepDemographics() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('About You', style: NutriTypography.displayLg),
          const SizedBox(height: 8),
          const Text('Help us personalize your experience.', style: NutriTypography.bodyMd),
          const SizedBox(height: 32),
          TextFormField(
            decoration: const InputDecoration(labelText: 'Age (Years)', hintText: 'e.g. 28'),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 20),
          TextFormField(
            decoration: const InputDecoration(labelText: 'Weight (kg)', hintText: 'e.g. 70'),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 20),
          TextFormField(
            decoration: const InputDecoration(labelText: 'Height (cm)', hintText: 'e.g. 175'),
            keyboardType: TextInputType.number,
          ),
        ],
      ),
    );
  }

  Widget _buildStepDiet() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Dietary Preferences', style: NutriTypography.displayLg),
          const SizedBox(height: 8),
          const Text('What type of diet do you follow?', style: NutriTypography.bodyMd),
          const SizedBox(height: 32),
          _buildSelectableCard('Vegetarian', 'No meat or fish'),
          const SizedBox(height: 12),
          _buildSelectableCard('Vegan', 'No animal products'),
          const SizedBox(height: 12),
          _buildSelectableCard('Omnivore', 'I eat everything', isSelected: true),
          const SizedBox(height: 12),
          _buildSelectableCard('Pescatarian', 'Vegetarian + Fish'),
        ],
      ),
    );
  }

  Widget _buildStepGoals() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Your Goals', style: NutriTypography.displayLg),
          const SizedBox(height: 8),
          const Text('What do you want to achieve?', style: NutriTypography.bodyMd),
          const SizedBox(height: 32),
          _buildSelectableCard('Lose Weight', 'Burn fat and get leaner'),
          const SizedBox(height: 12),
          _buildSelectableCard('Maintain Weight', 'Stay healthy and fit', isSelected: true),
          const SizedBox(height: 12),
          _buildSelectableCard('Gain Muscle', 'Build strength and size'),
        ],
      ),
    );
  }

  Widget _buildStepPantry() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Digital Pantry', style: NutriTypography.displayLg),
          const SizedBox(height: 8),
          const Text('What do you already have at home? We\'ll prioritize recipes using these ingredients.', style: NutriTypography.bodyMd),
          const SizedBox(height: 32),
          TextFormField(
            decoration: const InputDecoration(
              hintText: 'Search for ingredients...',
              prefixIcon: Icon(Icons.search),
            ),
          ),
          const SizedBox(height: 24),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildPantryChip('Rice'),
              _buildPantryChip('Lentils'),
              _buildPantryChip('Olive Oil'),
              _buildPantryChip('Onions'),
              _buildPantryChip('Garlic'),
              _buildPantryChip('Tomatoes'),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildSelectableCard(String title, String subtitle, {bool isSelected = false}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isSelected ? NutriColors.primarySoft.withValues(alpha: 0.3) : NutriColors.canvasRaised,
        border: Border.all(color: isSelected ? NutriColors.primary : NutriColors.border, width: isSelected ? 2 : 1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: NutriTypography.displaySm.copyWith(color: isSelected ? NutriColors.primaryStrong : NutriColors.ink)),
                const SizedBox(height: 4),
                Text(subtitle, style: NutriTypography.bodySm),
              ],
            ),
          ),
          if (isSelected)
            const Icon(Icons.check_circle, color: NutriColors.primary),
        ],
      ),
    );
  }

  Widget _buildPantryChip(String label) {
    return Chip(
      label: Text(label),
      backgroundColor: NutriColors.canvasRaised,
      side: const BorderSide(color: NutriColors.border),
      labelStyle: NutriTypography.bodySm,
      deleteIcon: const Icon(Icons.close, size: 16),
      onDeleted: () {},
    );
  }
}
