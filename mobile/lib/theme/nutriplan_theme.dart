import 'package:flutter/material.dart';
import 'colors.dart';
import 'typography.dart';

class NutriTheme {
  NutriTheme._();

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: NutriColors.canvas,
      colorScheme: const ColorScheme.light(
        primary: NutriColors.primary,
        onPrimary: Colors.white,
        secondary: NutriColors.secondary,
        onSecondary: Colors.white,
        error: NutriColors.danger,
        surface: NutriColors.canvasRaised,
        onSurface: NutriColors.ink,
      ),
      fontFamily: NutriTypography.bodyFont,
      textTheme: const TextTheme(
        displayLarge: NutriTypography.displayXl,
        displayMedium: NutriTypography.displayLg,
        displaySmall: NutriTypography.displayMd,
        bodyLarge: NutriTypography.bodyLg,
        bodyMedium: NutriTypography.bodyMd,
        bodySmall: NutriTypography.bodySm,
        labelLarge: NutriTypography.dataLg,
        labelMedium: NutriTypography.dataMd,
        labelSmall: NutriTypography.dataSm,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: NutriColors.canvas,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: NutriColors.ink),
        titleTextStyle: NutriTypography.displaySm,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: NutriColors.primary,
          foregroundColor: Colors.white,
          textStyle: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.w600),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: NutriColors.ink,
          side: const BorderSide(color: NutriColors.border),
          textStyle: NutriTypography.bodyMd.copyWith(fontWeight: FontWeight.w600),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      cardTheme: CardThemeData(
        color: NutriColors.canvasRaised,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: NutriColors.border),
        ),
        margin: EdgeInsets.zero,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: NutriColors.canvasRaised,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: NutriColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: NutriColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: NutriColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: NutriColors.danger),
        ),
        labelStyle: NutriTypography.dataMd,
        hintStyle: NutriTypography.bodyMd.copyWith(color: NutriColors.inkMuted),
      ),
    );
  }
}
