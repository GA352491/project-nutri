import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/typography.dart';

enum NutriChipVariant { primary, secondary, danger, info, outline }

class NutriChip extends StatelessWidget {
  final String label;
  final NutriChipVariant variant;
  final Widget? icon;

  const NutriChip({
    super.key,
    required this.label,
    this.variant = NutriChipVariant.primary,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final colors = _getColors();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: colors.background,
        border: Border.all(color: colors.border),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            IconTheme(
              data: IconThemeData(color: colors.text, size: 14),
              child: icon!,
            ),
            const SizedBox(width: 4),
          ],
          Text(
            label.toUpperCase(),
            style: NutriTypography.dataSm.copyWith(
              color: colors.text,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  _ChipColors _getColors() {
    switch (variant) {
      case NutriChipVariant.primary:
        return _ChipColors(
            background: NutriColors.primarySoft,
            text: NutriColors.primary,
            border: NutriColors.primarySoft);
      case NutriChipVariant.secondary:
        return _ChipColors(
            background: NutriColors.secondarySoft,
            text: NutriColors.secondaryStrong,
            border: NutriColors.secondarySoft);
      case NutriChipVariant.danger:
        return _ChipColors(
            background: NutriColors.tertiarySoft,
            text: NutriColors.danger,
            border: NutriColors.tertiarySoft);
      case NutriChipVariant.info:
        return _ChipColors(
            background: NutriColors.infoSoft,
            text: NutriColors.info,
            border: NutriColors.infoSoft);
      case NutriChipVariant.outline:
        return _ChipColors(
            background: Colors.transparent,
            text: NutriColors.inkMuted,
            border: NutriColors.border);
    }
  }
}

class _ChipColors {
  final Color background;
  final Color text;
  final Color border;

  _ChipColors({required this.background, required this.text, required this.border});
}
