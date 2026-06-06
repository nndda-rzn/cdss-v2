# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to a modified [Semantic Versioning](https://semver.org/)
scheme: `v0.<sprint>.<patch>` during prototype phase, reaching `v1.0.0` at the
Sprint 8 demo-ready milestone.

This file is managed automatically by release-please. Manual edits may be
overwritten.

## [0.8.0-fsd-refactor](https://github.com/nndda-rzn/cdss-v2/compare/v0.7.0-fsd-refactor...v0.8.0-fsd-refactor) (2026-06-06)


### Features

* **admin:** admin panel - user/facility CRUD, tuning RBAC, role-gated sidebar ([#30](https://github.com/nndda-rzn/cdss-v2/issues/30)) ([022d590](https://github.com/nndda-rzn/cdss-v2/commit/022d5902a28b2db2846c17ac68e27f57e94f876e))
* **admin:** Cloudflare-style admin dashboard with AI performance metrics ([#31](https://github.com/nndda-rzn/cdss-v2/issues/31)) ([da74628](https://github.com/nndda-rzn/cdss-v2/commit/da74628176a46a6e0438d24d3d976b49e8156c86))
* **admin:** separate admin dashboard + role-specific sidebar + role-based login redirect ([63547ac](https://github.com/nndda-rzn/cdss-v2/commit/63547acce4952d99f866d09e21cdedf466755553))
* **ai-analysis:** full-page detail view (5-model comparison) ([#22](https://github.com/nndda-rzn/cdss-v2/issues/22)) ([17f2b3b](https://github.com/nndda-rzn/cdss-v2/commit/17f2b3be90d59765f605d3e61e8a97942da3d612))
* **ai-analysis:** medical-grade focus shell with patient identity ([#23](https://github.com/nndda-rzn/cdss-v2/issues/23)) ([99424d7](https://github.com/nndda-rzn/cdss-v2/commit/99424d701e8d41de1b10910db9881f1f75efdb85))
* clinician seeder + rbac ux guards (fix patient register 403) ([#21](https://github.com/nndda-rzn/cdss-v2/issues/21)) ([93ffa88](https://github.com/nndda-rzn/cdss-v2/commit/93ffa8830fd15b0c97c650cfbb89f1977d4d0bdd))
* **clinician:** full clinician flow cleanup ([#48](https://github.com/nndda-rzn/cdss-v2/issues/48)) ([5bff93e](https://github.com/nndda-rzn/cdss-v2/commit/5bff93e0479906336d5ba7c02b72ac4041dfbe42))
* **dashboard:** add charts to clinical dashboard (SaaS style) ([#32](https://github.com/nndda-rzn/cdss-v2/issues/32)) ([fd38143](https://github.com/nndda-rzn/cdss-v2/commit/fd38143dd8123bd64fa06b901d188d4e3d39523e))
* **encounter:** clinical workspace layout for encounter detail ([#24](https://github.com/nndda-rzn/cdss-v2/issues/24)) ([cbb50bf](https://github.com/nndda-rzn/cdss-v2/commit/cbb50bf36be95d0ad0ea3e53ab40c2d41f12c6cc))
* **hirescam:** add API endpoints + auto-generate after inference ([4ecd36e](https://github.com/nndda-rzn/cdss-v2/commit/4ecd36e70ed784fa7217bc997828ba1644856eb5))
* **hirescam:** add backfill script for existing analyses ([efd0c47](https://github.com/nndda-rzn/cdss-v2/commit/efd0c4705a9776ef5f064ff8b34f0b9d47bbafae))
* **hirescam:** add CLI experiment runner for tuning pipeline ([1443cff](https://github.com/nndda-rzn/cdss-v2/commit/1443cff858f98fca6c6d48449c96b56f71b82855))
* **hirescam:** add EmptyState for missing HiResCAM data ([c0241af](https://github.com/nndda-rzn/cdss-v2/commit/c0241afed663dc0452874046cbb8e7521588d53c))
* **hirescam:** add frontend heatmap viewer, status badge, and page integration ([ccb2e0f](https://github.com/nndda-rzn/cdss-v2/commit/ccb2e0f20a0be9cabf7e155f852888be064b8f57))
* **hirescam:** add generator_v2 with multi-layer + letterbox support (split for file budget) ([d92479b](https://github.com/nndda-rzn/cdss-v2/commit/d92479b56725730ef72d1bd12851f4c7907c0692))
* **hirescam:** add HiResCAMArtifact model, services, and unit tests ([37503fa](https://github.com/nndda-rzn/cdss-v2/commit/37503fa6de2a4b44b30598b27f45c66de2807c67))
* **hirescam:** add letterbox module with reverse mapping ([fad3227](https://github.com/nndda-rzn/cdss-v2/commit/fad3227dcd26670eaf5a5759ad721d7713f08887))
* **hirescam:** add postprocess module with clip/smooth/top_percent pipeline ([501d389](https://github.com/nndda-rzn/cdss-v2/commit/501d389611a07773d7f57c108e7c924380ae144c))
* **hirescam:** extend colormap to support turbo/jet/viridis/plasma ([e727b66](https://github.com/nndda-rzn/cdss-v2/commit/e727b6673386b4a21beb892c05868504eed29680))
* **hirescam:** HiResCAM explainability — heatmap, overlay, status, frontend viewer ([8925cfc](https://github.com/nndda-rzn/cdss-v2/commit/8925cfcc2eca721581888aa7b5b3fbf2bcd31733))
* **hirescam:** use generate_hirescam_v2 in production orchestration ([19362aa](https://github.com/nndda-rzn/cdss-v2/commit/19362aa47221bc57c4af9588675cec7d9295ac98))
* model selector + visual explanation layout improvements ([#45](https://github.com/nndda-rzn/cdss-v2/issues/45)) ([48e0268](https://github.com/nndda-rzn/cdss-v2/commit/48e02686a6fed4e92a0f9b425bdf71a467e0d99a))
* **patient:** saas-style card and grid register form ([#20](https://github.com/nndda-rzn/cdss-v2/issues/20)) ([b3bb373](https://github.com/nndda-rzn/cdss-v2/commit/b3bb373ecf128bdd702ed24a26efd9dc1b6b914f))
* **scripts:** seed model metadata for AI analysis ([#33](https://github.com/nndda-rzn/cdss-v2/issues/33)) ([5863898](https://github.com/nndda-rzn/cdss-v2/commit/5863898ca23fc5bfaee9fca721678d6348883b74))
* **sprint-4:** HiResCAM tuning pipeline — letterbox, multi-layer, postprocess, CLI runner ([c08bb97](https://github.com/nndda-rzn/cdss-v2/commit/c08bb975b684a493bfb8c97eb3391cc0c8310ee7))
* **sprint-7:** UI/UX audit improvements ([#46](https://github.com/nndda-rzn/cdss-v2/issues/46)) ([8cb5c62](https://github.com/nndda-rzn/cdss-v2/commit/8cb5c62ae958b56109148335df7cddc560403e15))
* **tuning:** HiResCAM tuning viewer + config integration ([#29](https://github.com/nndda-rzn/cdss-v2/issues/29)) ([3080da9](https://github.com/nndda-rzn/cdss-v2/commit/3080da948a6cae4b2d60f5e6b74b7c07cef3d960))
* **ui:** apply UI/UX Pro Max saas-clinical design to encounter detail page ([3d7712f](https://github.com/nndda-rzn/cdss-v2/commit/3d7712f32d07a356d4fcd0048d6bdb37eb9e0b29))
* **ui:** redesign clinical context and ecg upload forms for clinical workspace ([144ae4e](https://github.com/nndda-rzn/cdss-v2/commit/144ae4e85621c5538b3a8b65c9989396d2252378))


### Bug Fixes

* **api:** replace Role.CLINICIAN/NURSE with Role.CLINICAL in encounters ([3012e7d](https://github.com/nndda-rzn/cdss-v2/commit/3012e7d89b74f5351260c85356a61041e0416866))
* **hirescam:** 10 bug fixes for HiResCAM generation and display ([d206045](https://github.com/nndda-rzn/cdss-v2/commit/d2060452ac2c9ee7d3fda34fa37995795de475ec))
* **hirescam:** add heatmaps/ prefix to serve_heatmap path resolution ([403d768](https://github.com/nndda-rzn/cdss-v2/commit/403d768a2e406c6a3cde7818f66c20d66bcbc59a))
* **hirescam:** add idempotency check + session.rollback to prevent 500 on re-analyze ([0bd690f](https://github.com/nndda-rzn/cdss-v2/commit/0bd690f896481d1aa2a682d8148997a9cdd6404e))
* **hirescam:** fix heatmapUrl to include /encounters/ prefix matching backend route ([d602446](https://github.com/nndda-rzn/cdss-v2/commit/d602446f5f4de973a6f900fbaac71939197aa414))
* **hirescam:** fix HeatmapViewer URL prefix to include /encounters/ ([251f235](https://github.com/nndda-rzn/cdss-v2/commit/251f2351360dbfa64e3cace95eaa867e33fca9b1))
* **hirescam:** fix model.args dict access in generator ([f23da50](https://github.com/nndda-rzn/cdss-v2/commit/f23da50612efe62da36d9f78b90bbec6b4bfb00f))
* **hirescam:** invalidate hirescam query after re-run analysis ([31df8e7](https://github.com/nndda-rzn/cdss-v2/commit/31df8e7f78e009f75b9df1c375fc37d718acc1a7))
* **hirescam:** store artifact paths relative to heatmaps dir, not storage root ([24b74a1](https://github.com/nndda-rzn/cdss-v2/commit/24b74a1c10ba9dc5a6153fa633d8cb8efe1aaff8))
* **hirescam:** strip leading heatmaps/ prefix in heatmapUrl for safety ([5b70281](https://github.com/nndda-rzn/cdss-v2/commit/5b70281d9f53e3a9c8fcd99710dfe12e63afd076))
* **hirescam:** use float32 for ImageNet normalization to prevent type mismatch ([468fcca](https://github.com/nndda-rzn/cdss-v2/commit/468fcca2bd1b7ce25521af158d4dc35f1d99edaa))
* **search:** add DialogDescription to GlobalSearch palette ([#19](https://github.com/nndda-rzn/cdss-v2/issues/19)) ([b36390d](https://github.com/nndda-rzn/cdss-v2/commit/b36390d63c800fb057cfae3a716831f023e3a994))
* **sidebar:** add Dashboard link to admin sidebar ([fc6bd4c](https://github.com/nndda-rzn/cdss-v2/commit/fc6bd4ce1f6dfd162391e73eb02c8085af21822c))
* **sidebar:** remove Tuning from Admin section ([5832607](https://github.com/nndda-rzn/cdss-v2/commit/583260703393af74bea541f8669d49efbcc99c66))
* **sidebar:** use exact match for admin dashboard nav ([92d6fd3](https://github.com/nndda-rzn/cdss-v2/commit/92d6fd31248beadde5b62367474d71bbb3350618))
* **tuning:** remove RBAC from image endpoint (img tags cannot send auth headers) ([cb14b9d](https://github.com/nndda-rzn/cdss-v2/commit/cb14b9d1348b935e16fcea13221d65f15d45d0ac))
* **ui:** import Button in EcgStudyList ([a0bee6d](https://github.com/nndda-rzn/cdss-v2/commit/a0bee6d4d432a14605c84221924590504834c8c7))

## [Unreleased]

### Added
- Initial repository documentation baseline (Sprint 0):
  - Architecture, data model & PHI, decision engine, color system, Sprint 1 design docs
  - PRD v3 and v3.1 delta
  - Rule-based system reference
  - GitHub operations docs (git workflow, commit convention, PR flow, release, branch protection, repo setup)
  - 14 Architecture Decision Records
  - Contribution, security, and code of conduct policies
  - CI pipeline, issue/PR templates, dependabot, labels
