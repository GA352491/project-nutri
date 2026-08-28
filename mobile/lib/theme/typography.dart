import 'package:flutter/material.dart';
import 'colors.dart';

class NutriTypography {
  NutriTypography._();

  // Display font — Fraunces (serif, for headings)
  static const String displayFont = 'Fraunces';

  // Body font — IBM Plex Sans (for body text)
  static const String bodyFont = 'IBMPlexSans';

  // Data font — IBM Plex Mono (for numbers, labels)
  static const String dataFont = 'IBMPlexMono';

  // Display styles
  static const TextStyle displayXl = TextStyle(
    fontFamily: displayFont,
    fontWeight: FontWeight.w700,
    fontSize: 32,
    height: 1.1,
    letterSpacing: -0.5,
    color: NutriColors.ink,
  );

  static const TextStyle displayLg = TextStyle(
    fontFamily: displayFont,
    fontWeight: FontWeight.w600,
    fontSize: 24,
    height: 1.2,
    letterSpacing: -0.3,
    color: NutriColors.ink,
  );

  static const TextStyle displayMd = TextStyle(
    fontFamily: displayFont,
    fontWeight: FontWeight.w600,
    fontSize: 20,
    height: 1.25,
    color: NutriColors.ink,
  );

  static const TextStyle displaySm = TextStyle(
    fontFamily: displayFont,
    fontWeight: FontWeight.w600,
    fontSize: 16,
    height: 1.3,
    color: NutriColors.ink,
  );

  // Body styles
  static const TextStyle bodyLg = TextStyle(
    fontFamily: bodyFont,
    fontWeight: FontWeight.w400,
    fontSize: 17,
    height: 1.5,
    color: NutriColors.ink,
  );

  static const TextStyle bodyMd = TextStyle(
    fontFamily: bodyFont,
    fontWeight: FontWeight.w400,
    fontSize: 15,
    height: 1.5,
    color: NutriColors.ink,
  );

  static const TextStyle bodySm = TextStyle(
    fontFamily: bodyFont,
    fontWeight: FontWeight.w400,
    fontSize: 13,
    height: 1.4,
    color: NutriColors.inkMuted,
  );

  // Data / Mono styles
  static const TextStyle dataLg = TextStyle(
    fontFamily: dataFont,
    fontWeight: FontWeight.w500,
    fontSize: 15,
    height: 1.3,
    color: NutriColors.ink,
  );

  static const TextStyle dataMd = TextStyle(
    fontFamily: dataFont,
    fontWeight: FontWeight.w400,
    fontSize: 13,
    height: 1.3,
    letterSpacing: 0.5,
    color: NutriColors.inkMuted,
  );

  static const TextStyle dataSm = TextStyle(
    fontFamily: dataFont,
    fontWeight: FontWeight.w400,
    fontSize: 11,
    height: 1.3,
    letterSpacing: 0.8,
    color: NutriColors.inkMuted,
  );
}
