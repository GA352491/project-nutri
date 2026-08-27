---
name: nutriplan-design-system
description: Use whenever building or editing UI for the NutriPlan app — any Vue component, page, screen, or Flutter widget. Covers brand colors, typography, spacing, and component patterns (macro ring, meal card, nutrition-facts stat block, chat bubbles, banners). Trigger on any frontend/UI task in this repo, even if the person doesn't mention "design system" by name.
---

# NutriPlan Design System

Reference files in this repo: `DESIGN_SYSTEM.md` (full spec), `01-design-tokens.html` / `02-component-library.html` (live reference), `tailwind-theme.css` (Tailwind v4 `@theme` mapping).

## Rules for any UI you generate
1. **Never use Tailwind's default palette classes** (`bg-indigo-*`, `text-gray-*`, etc.) — use the theme tokens: `bg-primary`, `bg-secondary`, `text-ink`, `text-ink-muted`, `bg-canvas`, `bg-canvas-raised`, `border-border`, and the semantic states `success` / `warning` / `danger` / `info` (each with a `-soft` tint variant for backgrounds).
2. **Three fonts, three jobs** — `font-display` (Fraunces) for headlines only, `font-body` (IBM Plex Sans) for everything else, `font-data` (IBM Plex Mono, always paired with `tabular-nums`) for every macro/micro/calorie number. Never put a number in `font-body`.
3. **Reuse the established component patterns** rather than inventing new ones for the same job:
   - Macro/micro progress → the ring pattern in `02-component-library.html` (SVG circle, `--color-border` track + semantic-colored progress).
   - Meal display → the meal-card pattern (thumbnail, title, macro line in `font-data`, a status chip, a log/swap action).
   - Any nutrient total → the nutrition-facts-styled stat block (thick `--color-ink` rules, right-aligned tabular numbers, %DV column). This is the app's signature motif — reuse it, don't design a new stat layout.
   - AI vs. human messages → visually distinct chat bubbles (`bg-info-soft` for AI, `bg-secondary-soft` for human nutritionist, `bg-primary` solid for the user) — never let AI and human messages look the same; this is a trust/compliance requirement, not a style preference.
4. **Radius**: `rounded-sm` (6px) for chips, `rounded-md` (12px) for cards, `rounded-lg` (20px) for sheets/modals — mapped in `tailwind-theme.css`.
5. **Accessibility floor**: WCAG AA contrast, 44px minimum tap targets on mobile, never convey status (on-target/over-budget/allergy conflict) by color alone — pair with an icon or text label.
6. **Web (Vue) and mobile (Flutter) must look identical** for the same component — if you're implementing a Flutter widget, mirror the Vue/Tailwind version's spacing and color mapping exactly using the same hex values from `tailwind-theme.css`, via a Flutter `ThemeExtension`.

## When integrating Tailwind Plus blocks
Tailwind Plus markup uses Tailwind's default palette. When adapting a block: swap `indigo`→`primary`, `gray-900`→`ink`, `gray-500`→`ink-muted`, `white`→`canvas-raised`, `gray-200` borders→`border`, and check radius against the mapping in `tailwind-theme.css`. Leave structural/layout utilities untouched.
