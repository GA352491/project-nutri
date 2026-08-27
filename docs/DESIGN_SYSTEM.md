# Design System — NutriPlan (Web + Mobile)

One token source, two implementations (Vue 3 web, Flutter mobile) so the product feels like one app across platforms.

## 1. Foundations

### Color (semantic, not raw hex in components)
| Token | Purpose |
|---|---|
| `color-primary` | Main brand/CTA (a calm green — health, growth, not alarm) |
| `color-secondary` | Supporting accent (warm amber, used sparingly — e.g., "adjusted plan" banners) |
| `color-success` | On-target macro/micro, completed log |
| `color-warning` | Over/under budget, approaching allergy conflict |
| `color-danger` | Allergy conflict, missed critical log, compliance violation |
| `color-info` | AI chatbot / activity-adjustment messaging |
| `color-surface` / `color-surface-alt` | Card backgrounds, light/dark variants |
| `color-text-primary` / `color-text-muted` | Body text vs secondary text |

Ship both a light and dark theme from day one — logging happens at all hours (breakfast at 6am, dinner logging at night).

### Typography
- One variable sans family with an open license (e.g., Inter or Public Sans) across web and mobile.
- **Tabular figures** for all numeric macro/micro values so diary tables and rings align visually — this matters more in a nutrition app than most.
- Scale: display / h1–h3 / body / caption / numeric-large (for the big "kcal remaining" number) / numeric-small.

### Spacing & grid
- 4px base unit, 8px rhythm for components, 16/24px page gutters on mobile, 24/32 on web.
- Web: 12-column responsive grid. Mobile: single-column, bottom-tab navigation (Home/Plan/Log/Chat/Profile).

### Iconography
- One open-source icon set used consistently (e.g., Phosphor or Lucide) — both have Vue and Flutter packages, avoiding a mismatched look between platforms.

## 2. Core components (build once conceptually, implement per platform)

- **Macro/Micro Ring** — circular progress per macro (protein/carb/fat) + a secondary micronutrient gap indicator; used on home screen, diary, and meal detail.
- **Meal Card** — image, name, calories, macro chips, "swap" and "log" actions; same card used in curated and generative plan views.
- **Day Timeline** — breakfast → lunch → snack → dinner, with a running kcal-remaining header; this is the primary screen.
- **Activity Adjustment Banner** — `color-info` styled, shows the wearable-driven target change with accept/dismiss (see TRD §9) — must never auto-apply silently, always an explicit user action.
- **Photo-Log Capture Sheet** — camera view → detected food chips (editable, multi-item) → quantity steppers → confirm; this is the highest-frequency interaction in the app, so it gets the most design attention (fewest taps to log).
- **Chat Bubble (dual mode)** — visually distinct styling for AI chatbot vs. human nutritionist messages, so the user always knows which they're talking to (important for trust/compliance — AI nutrition chat should never be visually confusable with licensed-professional advice).
- **Appointment Slot Picker**, **Grocery List Item** (checkbox + store-section grouping), **Compliance Badge** (e.g., "meets ICMR-NIN RDA" / "meets USDA DRI").

## 3. Platform-specific notes

- **Web (Vue 3)**: build components in a shared component library (Storybook-documented), themed via CSS variables generated from the token file; use PrimeVue or shadcn-vue as the unstyled/headless base rather than building every primitive from scratch.
- **Mobile (Flutter)**: implement the same tokens as a `ThemeData`/`ThemeExtension`, and mirror each web component 1:1 in Flutter widgets (`MacroRing`, `MealCard`, etc.) so designers hand off one Figma spec that both teams implement against — avoids web/mobile visual drift.
- **Camera screen** gets platform-native camera APIs (not a generic webview capture) for speed and accuracy of the food-recognition flow — this is the main reason Flutter/React Native was chosen over Capacitor.

## 4. Accessibility
- WCAG AA contrast minimum everywhere, but especially on macro/micro numbers and warning/danger states — these carry health-relevant meaning and must not rely on color alone (pair with icon/text).
- All logging actions reachable via screen reader with clear labels ("Protein, 24 of 90 grams, on target").
- Minimum 44×44px (mobile) / 40×40px (web) tap targets, given logging is often done one-handed while eating.

## 5. Motion — functional, not decorative
2026's motion consensus (confirmed against current design trend reporting) is restraint: animation confirms state and guides attention, it doesn't perform. Every motion in NutriPlan should answer "what changed?" — nothing moves just to look alive.

### Motion tokens
| Token | Value | Use |
|---|---|---|
| `motion-ease-standard` | `cubic-bezier(.4,0,.2,1)` | default for all transitions |
| `motion-ease-out` | `cubic-bezier(0,0,.2,1)` | entrances (banners, sheets, chips appearing) |
| `motion-ease-spring` | `cubic-bezier(.34,1.56,.64,1)` | one-time confirmation "pop" only (log-complete checkmark) — used sparingly, on purpose |
| `motion-duration-instant` | 100ms | hover/press feedback |
| `motion-duration-fast` | 180ms | chip/checkbox toggles, tab switches |
| `motion-duration-base` | 260ms | card entrances, banner slide-in |
| `motion-duration-ring` | 700ms | macro ring fill on load — the one deliberately slower "counting up" moment |

### Named micro-interactions
- **Log confirmation** — the meal card's "Log" button morphs into a filled "Logged" state: background fades to `color-primary` over `motion-duration-fast`, a checkmark scales in with `motion-ease-spring`. This is the single highest-frequency action in the app, so it's the one interaction allowed a touch of personality.
- **Macro ring fill** — on load, the ring's stroke animates from 0 to its value over `motion-duration-ring` with `motion-ease-out`, so daily progress reads as counting up rather than snapping in — softens the usual jarring instant-full-data feel of a health dashboard.
- **Activity-adjustment banner** — slides down + fades in (`motion-duration-base`, `motion-ease-out`) when a wearable sync changes targets; reverses on dismiss. It should never appear instantly — the motion itself signals "something changed," which matters because this banner represents an automatic plan edit the user needs to actually notice.
- **Button press** — 2% scale-down + reduced shadow at `motion-duration-instant`, identical across every button in the system.
- **Chip/status change** (e.g. "Swap available" → "On target") — cross-fades over `motion-duration-fast`, no layout shift.
- **Tab/section switch** — the active indicator slides to its new position rather than jump-cutting.
- **Toast/system messages** — fade only, no slide — keep system messages calm, not attention-grabbing.

### Rules
- Respect `prefers-reduced-motion: reduce` everywhere — swap all of the above to instant opacity/state changes, no exceptions.
- No scroll-triggered or ambient animation — this is a daily-use utility app, not a marketing site; the entire motion budget goes to state confirmation.
- The spring easing is reserved for the log-confirmation moment only. Using it elsewhere dilutes it into decoration — the exact failure mode current motion-design guidance warns against.
