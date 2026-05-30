# ADR-0010: Petrol + charcoal color system

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: color-system-and-tokens-design.md

## Context

Most healthcare UIs default to white + blue, often producing a generic, template-like look. The product needs medical recognizability and trust, while being distinctive enough for a publication-grade tool, and must not let UI chrome compete with clinical signals and the HiResCAM heatmap.

## Decision

Adopt a hybrid "data-as-protagonist" system: a deliberate balanced petrol blue (hue ~200) as a minimal brand color, a warm-tinted charcoal/off-white scale as the dominant neutral surface, pure clinical signals (RED/AMBER/GREEN) independent of brand, and the inferno heatmap as the most intense visualization. Light mode only.

## Options Considered

### Option A - Petrol + charcoal hybrid (chosen)
- Pros: Medical recognizability + distinctive; neutral canvas lets data dominate; strict tier separation prevents clashes.
- Cons: Requires discipline on "where brand color belongs".

### Option B - Conventional white + default blue
- Pros: Familiar, low effort.
- Cons: Generic; brand competes with data.

### Option C - Non-blue (green/teal/earth/charcoal-only)
- Pros: Distinctive.
- Cons: Green clashes with safety GREEN; warm tones too "wellness" for acute MI.

## Consequences

- Positive: Distinctive yet clinically credible; defensible in the paper (data-as-protagonist, Crameri et al. 2020).
- Negative: Token discipline and accessibility audits required.
- Risks: Brand/signal blur; mitigated by locked hues, saturation hierarchy, and clash-avoidance rulebook.

## Notes

Info signal uses slate (not blue) to avoid brand blur. Petrol hue locked 195-210.
