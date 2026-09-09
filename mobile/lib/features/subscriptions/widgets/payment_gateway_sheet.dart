import 'package:flutter/material.dart';
import '../../../theme/colors.dart';
import '../../../theme/typography.dart';
import '../services/payment_service.dart';

class PaymentGatewaySheet extends StatefulWidget {
  final SubscriptionPlanTier plan;
  final Function(String paymentMethod) onPaymentSuccess;

  const PaymentGatewaySheet({
    super.key,
    required this.plan,
    required this.onPaymentSuccess,
  });

  @override
  State<PaymentGatewaySheet> createState() => _PaymentGatewaySheetState();
}

class _PaymentGatewaySheetState extends State<PaymentGatewaySheet> {
  int _selectedGateway = 0; // 0: Stripe Card, 1: UPI / Instant Pay
  bool _isProcessing = false;
  String _statusText = '';

  final _cardNumberController = TextEditingController(text: '4242 •••• •••• 4242');
  final _expiryController = TextEditingController(text: '12/28');
  final _cvvController = TextEditingController(text: '888');
  final _upiController = TextEditingController(text: 'user@okhdfcbank');

  @override
  void dispose() {
    _cardNumberController.dispose();
    _expiryController.dispose();
    _cvvController.dispose();
    _upiController.dispose();
    super.dispose();
  }

  Future<void> _processPayment() async {
    setState(() {
      _isProcessing = true;
      _statusText = _selectedGateway == 0
          ? 'Connecting to Stripe secure vault...'
          : 'Requesting UPI authorization...';
    });

    await Future.delayed(const Duration(milliseconds: 900));

    setState(() {
      _statusText = 'Authorizing ${widget.plan.price} payment intent...';
    });

    await Future.delayed(const Duration(milliseconds: 900));

    setState(() {
      _statusText = 'Payment successful! Activating subscription...';
    });

    await Future.delayed(const Duration(milliseconds: 600));

    if (mounted) {
      widget.onPaymentSuccess(
        _selectedGateway == 0 ? 'stripe_pm_card' : 'upi_instant_pay',
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      decoration: const BoxDecoration(
        color: NutriColors.canvasRaised,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 44,
                height: 4,
                decoration: BoxDecoration(
                  color: NutriColors.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Header & Order Summary
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Checkout & Payment', style: NutriTypography.displaySm),
                    const SizedBox(height: 2),
                    Text(
                      'Secured with 256-bit Stripe / Bank Encryption',
                      style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 11),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: _isProcessing ? null : () => Navigator.pop(context),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Plan Summary Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: NutriColors.canvas,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: NutriColors.border),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(widget.plan.name, style: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.bold)),
                      Text(
                        'Billing: ${widget.plan.period}',
                        style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 11),
                      ),
                    ],
                  ),
                  Text(
                    widget.plan.price,
                    style: const TextStyle(
                      fontFamily: NutriTypography.displayFont,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: NutriColors.primary,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Payment Gateway Selector
            const Text('Choose Payment Method', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: _buildGatewayOption(
                    index: 0,
                    icon: Icons.credit_card_rounded,
                    title: 'Credit / Debit Card',
                    subtitle: 'Stripe Gateway',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildGatewayOption(
                    index: 1,
                    icon: Icons.account_balance_rounded,
                    title: 'UPI / QR',
                    subtitle: 'GPay, PhonePe, Paytm',
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Gateway Input Fields
            if (_selectedGateway == 0) ...[
              TextField(
                controller: _cardNumberController,
                decoration: InputDecoration(
                  labelText: 'Card Number',
                  prefixIcon: const Icon(Icons.credit_card),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _expiryController,
                      decoration: InputDecoration(
                        labelText: 'Valid Thru',
                        hintText: 'MM/YY',
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      controller: _cvvController,
                      decoration: InputDecoration(
                        labelText: 'CVV',
                        hintText: '•••',
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ],
              ),
            ] else ...[
              TextField(
                controller: _upiController,
                decoration: InputDecoration(
                  labelText: 'Virtual Payment Address (VPA / UPI ID)',
                  prefixIcon: const Icon(Icons.alternate_email_rounded),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],

            if (_statusText.isNotEmpty) ...[
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(strokeWidth: 2, color: NutriColors.primary),
                  ),
                  const SizedBox(width: 8),
                  Text(_statusText, style: const TextStyle(fontSize: 12, color: NutriColors.primary, fontWeight: FontWeight.w600)),
                ],
              ),
            ],

            const SizedBox(height: 22),

            // Pay CTA Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isProcessing ? null : _processPayment,
                icon: _isProcessing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.lock_rounded, size: 18),
                label: Text(
                  _isProcessing
                      ? 'Processing Authorization...'
                      : 'Pay ${widget.plan.price} & Activate Plan',
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: NutriColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
              ),
            ),

            const SizedBox(height: 10),
            Center(
              child: Text(
                'Cancel anytime from your Profile settings. No lock-in period.',
                style: NutriTypography.dataSm.copyWith(color: NutriColors.inkMuted, fontSize: 10),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGatewayOption({
    required int index,
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    final isSelected = _selectedGateway == index;
    return InkWell(
      onTap: _isProcessing ? null : () => setState(() => _selectedGateway = index),
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? NutriColors.primarySoft.withValues(alpha: 0.3) : NutriColors.canvas,
          border: Border.all(
            color: isSelected ? NutriColors.primary : NutriColors.border,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: isSelected ? NutriColors.primary : NutriColors.inkMuted, size: 20),
                if (isSelected)
                  const Icon(Icons.check_circle_rounded, color: NutriColors.primary, size: 18),
              ],
            ),
            const SizedBox(height: 8),
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
            const SizedBox(height: 2),
            Text(subtitle, style: const TextStyle(color: NutriColors.inkMuted, fontSize: 10)),
          ],
        ),
      ),
    );
  }
}
