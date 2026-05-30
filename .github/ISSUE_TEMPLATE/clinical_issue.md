---
name: Clinical Issue
about: Report a clinical concern (ambiguous case, missed signal, wrong recommendation)
title: "clinical: "
labels: ["safety/clinical-review-needed", "status/needs-design"]
assignees: []
---

> WARNING: Do NOT include real patient data, identifiable information, or actual clinical records. Use synthetic or fully anonymized examples only.

## Clinical Concern Type

- [ ] Missed signal (false negative, e.g. MI not flagged)
- [ ] False alarm (false positive)
- [ ] Wrong/unsafe recommendation text
- [ ] Misleading HiResCAM heatmap
- [ ] Decision tree rule misfire
- [ ] Triage level inappropriate
- [ ] Other

## Description

<!-- Describe the clinical scenario (synthetic/anonymized) -->

## Expected Clinical Behavior

<!-- What should the system have shown, per guideline (ESC 2023 / Thygesen 2018)? -->

## Actual System Output

- Predicted class:
- Confidence:
- Risk/Triage level:
- Recommendation shown:
- Rules fired (if known):

## Guideline Reference

<!-- ESC 2023 section, Thygesen 2018, etc. -->

## Suggested Rule/Threshold Change

<!-- If applicable -->

## Requires Sp.JP Review?

- [ ] Yes (escalate to cardiologist co-design)
- [ ] No
