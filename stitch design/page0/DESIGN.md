---
name: Clinical Precision
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#00201d'
  on-tertiary-container: '#0c9488'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#89f5e7'
  tertiary-fixed-dim: '#6bd8cb'
  on-tertiary-fixed: '#00201d'
  on-tertiary-fixed-variant: '#005049'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system is engineered for the intersection of pharmaceutical research and artificial intelligence. It prioritizes clarity, structural integrity, and an "institutional modern" aesthetic that balances high-tech capability with academic rigor. 

The visual style is **Corporate Minimalism**. It avoids decorative flourishes in favor of purposeful whitespace and a clear information hierarchy. The interface should feel like a high-end laboratory instrument: precise, reliable, and unobtrusive. The target audience—scientists, data analysts, and executive stakeholders—requires a UI that minimizes cognitive load during complex data synthesis.

## Colors
The palette is rooted in a "Clinical White" environment to maximize legibility and perceived cleanliness. 

- **Primary:** Deep Slate (#0F172A) is used for high-level headings and primary navigation to provide a grounded, authoritative feel.
- **Secondary:** Professional Blue (#2563EB) is reserved for primary actions and interactive states, signaling intelligence and reliability.
- **Tertiary:** Scientific Teal (#0D9488) serves as a secondary accent for data visualization categories or success states, reinforcing the pharmaceutical context.
- **Neutral:** A range of grays from Slate-50 (#F8FAFC) for backgrounds to Slate-200 (#E2E8F0) for borders ensures subtle structural separation without visual noise.

## Typography
Inter is the sole typeface for this design system, chosen for its exceptional legibility in data-dense environments. 

Headlines utilize a slightly tighter letter-spacing and medium-to-semibold weights to convey importance. Body text is optimized for long-form reading of research papers and data reports, utilizing a 1.5x line-height ratio. Labels and data points use medium weights to ensure they are distinguishable from standard body text. For tabular data, a tabular-nums Opentype feature should be enabled to ensure alignment of numerical research results.

## Layout & Spacing
The system utilizes a 12-column fixed grid for desktop (max 1440px) to maintain focus and prevent scanning fatigue across ultra-wide monitors. 

Spacing follows a strict 4px baseline grid. Generous internal padding within cards and containers (typically 24px or 32px) is used to create "breathing room" around complex datasets. Layouts should prioritize a top-down, left-to-right flow that mirrors the scientific method: Hypothesis/Parameters (Sidebar/Top), Analysis (Center), and Results/Metadata (Right/Bottom).

## Elevation & Depth
Depth is conveyed through **Tonal Layers** and extremely **Soft Shadows**. 

The main application background uses a light neutral (#F8FAFC). Interactive surfaces and data cards use a pure white background with a 1px border (#E2E8F0). Elevation is reserved for active overlays like dropdowns or modals, utilizing a low-opacity, wide-spread shadow (0px 4px 20px rgba(15, 23, 42, 0.05)) to suggest a gentle lift without breaking the clean, flat aesthetic of the interface.

## Shapes
A consistent 10px-12px corner radius is applied to all primary containers and buttons. This "Rounded" approach softens the technical nature of the AI platform, making it feel more modern and accessible while remaining professional. Smaller elements like tags or input fields should mirror this radius (8px-10px) to maintain a cohesive visual language.

## Components
- **Buttons:** Primary buttons are solid Blue (#2563EB) with white text. Secondary buttons use a Slate-200 border and Slate-900 text. Use 12px vertical and 24px horizontal padding for a substantial, professional feel.
- **Data Cards:** White background, 1px border, 12px radius. Header areas within cards should be separated by a subtle horizontal rule.
- **Inputs:** Focused states use a 2px Blue (#2563EB) ring with a soft offset. Labels are always positioned above the input in `label-md` style.
- **Chips/Badges:** Used for molecular properties or status. Use high-contrast text on very desaturated background tints of the primary/tertiary colors.
- **Lists/Tables:** Use "Zebra striping" only for very wide datasets; otherwise, use subtle 1px horizontal dividers. Row height should be a minimum of 48px to ensure touch-targets and readability.
- **Status Indicators:** Small, circular dots for "Processing," "Complete," or "Error," using standard scientific color conventions (Blue, Green, Red).