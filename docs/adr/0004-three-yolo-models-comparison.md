# ADR-0004: Multiple YOLO models for comparison (3, expanded to 5)

- Status: Accepted
- Date: 2026-05-30
- Deciders: Maintainer
- Related: architecture-overview-design.md, decision-engine-design.md

## Context

The research contribution includes benchmarking lightweight classification models for ECG image screening. The thesis title initially highlighted a single YOLOv8, but the PRD specifies three model variants.

## Decision

Integrate and compare three classification models: YOLOv8n-cls, YOLOv11n-cls, and YOLOv26n-cls. Build a model registry supporting multi-model loading and switching from Sprint 1 onward (schema), with inference in Sprint 3.

> **Amendment (2026-05-31, Sprint 3):** scope expanded from 3 to **5 models** after the training pass produced five comparable classifiers: `yolov8n-cls`, `yolov8s-cls`, `yolov11n-cls`, `yolov11s-cls`, `yolov26n-cls` (nano + small variants across three generations). All five share the same 4-class output (`normal` / `mi` / `homi` / `abnormal`). Every active model runs per ECG study (synchronous, CPU), producing one `AIAnalysis` row each for comparative metrics. The registry, multi-model loading, and per-model SHA256 checksum decisions below hold unchanged — only the count increased.

## Options Considered

### Option A - Three models (benchmark)
- Pros: Stronger novelty (comparative study), meaningful research dashboard (model comparison), supports McNemar's test and per-model metrics.
- Cons: More inference plumbing (registry, switching), larger evaluation surface.

### Option B - Single YOLOv8
- Pros: Simpler, faster to ship.
- Cons: Weak novelty; research dashboard "comparison" becomes meaningless.

## Consequences

- Positive: Publication-grade comparative analysis; `model_metadata` becomes a first-class entity; registry pattern enables switching without restart.
- Negative: Additional complexity in inference subsystem and evaluation.
- Risks: Training all three on Kaggle; mitigated since v2 only consumes exported `.pt` artifacts.

## Notes

Thesis title should be updated to reflect multiple YOLO variants. Reproducibility requires per-model `metadata.json` with SHA256 checksum.
