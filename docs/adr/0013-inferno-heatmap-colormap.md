# ADR-0013: Inferno heatmap colormap

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: color-system-and-tokens-design.md, decision-engine-design.md

## Context

HiResCAM produces a heatmap overlay that is the most prominent visualization on the Result page. The colormap choice affects perceptual accuracy, accessibility, and defensibility in a medical-imaging publication. The default OpenCV JET colormap is widely discredited (perceptually non-uniform).

## Decision

Render HiResCAM heatmaps with the inferno colormap (matplotlib / OpenCV) in the backend Python service. This is a backend decision; the frontend only displays the resulting PNG.

## Options Considered

### Option A - Inferno (chosen)
- Pros: Perceptually uniform, colorblind-safe, high contrast (good on cheap displays), warm hues harmonize with the petrol+charcoal UI, defensible per Crameri et al. 2020.
- Cons: Slightly less common than viridis in some venues.

### Option B - Viridis
- Pros: Most common perceptually-uniform map in papers; cool tones.
- Cons: Lower contrast for subtle ECG patterns on low-quality displays.

### Option C - JET (OpenCV default)
- Pros: Familiar.
- Cons: Perceptually non-uniform, misleading; poor for publication.

## Consequences

- Positive: Scientifically defensible; strong contrast for pattern review; visual harmony with UI.
- Negative: Must explicitly configure (not rely on library default).
- Risks: None significant.

## Notes

Colormap lives in `backend/app/services/hirescam/colormap.py`. UI keeps a reference token `viz.heatmap.colormap = "inferno"` for documentation only.
