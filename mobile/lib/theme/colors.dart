import 'package:flutter/material.dart';

/// NutriPlan Design System Colours
/// Mirrors the Tailwind v4 @theme tokens exactly
class NutriColors {
  NutriColors._();

  // Canvas
  static const Color canvas = Color(0xFFFAF9F5);
  static const Color canvasRaised = Color(0xFFFFFFFF);

  // Ink (text)
  static const Color ink = Color(0xFF1C2620);
  static const Color inkMuted = Color(0xFF52635A);

  // Primary — Moss Green
  static const Color primary = Color(0xFF2F5233);
  static const Color primaryStrong = Color(0xFF1E3621);
  static const Color primarySoft = Color(0xFFDDE8DF);

  // Secondary — Turmeric
  static const Color secondary = Color(0xFFA87E00);
  static const Color secondaryStrong = Color(0xFF7A5C00);
  static const Color secondarySoft = Color(0xFFFFF3CC);

  // Tertiary — Chili
  static const Color tertiary = Color(0xFFA32B00);
  static const Color tertiarySoft = Color(0xFFFFE5DC);

  // State colours
  static const Color success = Color(0xFF2A7A2F);
  static const Color warning = Color(0xFFC97B00);
  static const Color danger = Color(0xFFC62800);
  static const Color info = Color(0xFF1D5FAC);
  static const Color infoSoft = Color(0xFFD9E9FA);

  // Borders
  static const Color border = Color(0xFFDFE4E0);

  // Semantic UI aliases for components
  static const Color background = canvas;
  static const Color surface = canvasRaised;
  static const Color surfaceAlt = primarySoft;
  static const Color textPrimary = ink;
  static const Color textSecondary = inkMuted;
}

/// Alias so both AppColors and NutriColors work at call sites
typedef AppColors = NutriColors;

/// Macro nutrient colours for charts
class MacroColors {
  MacroColors._();
  static const Color protein = Color(0xFF1D5FAC);  // info
  static const Color carbs = Color(0xFFA87E00);    // secondary
  static const Color fat = Color(0xFFA32B00);      // tertiary
  static const Color fiber = Color(0xFF2F5233);    // primary
}
