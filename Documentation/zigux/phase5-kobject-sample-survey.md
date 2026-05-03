# Phase 5 Kobject Sample Survey

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L12`
- `PHASE5_SURVEYED_COMMIT=db7498c99a89c4d166eede6dc59c43d32459c2f5`
- scope: roadmap-vs-repo sample reviewability, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay
- product boundary:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

This sample-backed survey note keeps the top-level docs-root guide in `Documentation/zigux/README.md`, the shared sample-root catalog in `samples/zigux/README.md`, the shared tests-root guide in `zigux/tests/README.md`, and the shared review checklist aligned with the shipped review surface.

The landed sample remains an approved Phase 5 ownership-and-lifetime idiom. `ownershipSummary()` now keeps replay readiness reviewable alongside the cold, initialized, registered, and exited stages, so reviewers do not have to infer when `runAnchorReplay()` is valid from method guards alone. `runInitializedExitReplay()` now keeps the initialized-only abandonment path sample-owned too, so the direct sample packet no longer leaves that exit summary as a one-off assertion trail.

The note still points back to the direct `zig test samples/zigux/kobject_example.zig` replay, the paired `zig test zigux/tests/phase5_kobject_example_survey.zig` replay, and the shared `phase5_build.zig` entrypoint.

Exact reviewability cues remain explicit:

- `ownershipSummary()` keeps replay readiness plus the `cold`, `initialized`, `registered`, and `exited` stages directly reviewable
- the replay-readiness boundary only allows `runAnchorReplay()` in the initialized stage
- the pre-registration zero-active-attributes boundary, the sample-owned initialized-only abandonment replay, and the post-exit rejection boundaries remain explicit
- sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope

Latest verification snapshot:

- `zig test samples/zigux/kobject_example.zig`
  - `All 5 tests passed.`
- `zig test zigux/tests/phase5_kobject_example_survey.zig`
  - `All 2 tests passed.`

