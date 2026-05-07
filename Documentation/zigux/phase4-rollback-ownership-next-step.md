# Phase 4 Rollback Ownership Next Step

This note records one bounded same-lane verification pass for the shared Phase 4 rollback-ownership and lab-matrix gate definitions.

## Status
- lane: `P4-L21`
- phase: `Phase 4`
- date: `2026-05-07`
- evidence mode: `github_connector_readback`
- scope: `rollback_ownership_and_lab_matrix_current_gate_definitions`

## Current Repo Evidence
- `Documentation/zigux/phase4-validation-matrix.md` and `Documentation/zigux/phase4-gate-evidence.md` remain the shared Phase 4 rollback-ownership and lab-matrix notes on `master`.
- `zigux/tests/phase4_build.zig` already wires `zigux/tests/phase4_bitmap_diff_survey.zig` into the shared Phase 4 entrypoint as both `phase4-bitmap-diff-survey-tests` and `phase4-bitmap-diff-survey`.
- `Documentation/zigux/phase4-validation-matrix.md` now gives `zigux/tests/phase4_bitmap_diff_survey.zig` its own owner and rollback-owner row under `Shared Subsystems Pod`, and the same Lab And CI Matrix now names the direct local replay route `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`.
- `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` now agree with the live `Documentation/zigux/phase4-gate-evidence.md` blob on `master`, so the earlier bitmap survey packet blob-drift repair is already landed and no longer the missing same-lane step.
- `zigux/Makefile` still does not expose `phase4-bitmap-diff-survey` in its Phase 4 `PHONY` list or as a dedicated Linux-style wrapper recipe, even though the shared matrix says that wrapper exists.
- `scripts/zigux/validate-phase4.py` still omits `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` from `REQUIRED_FILES`, `REQUIRED_PHASE4_MATRIX_MARKERS`, `REQUIRED_PHASE4_BUILD_MARKERS`, and the shared packet surface it validates.
- `Documentation/zigux/review-checklist.md` still lists the shared Phase 4 packet without `zigux/tests/phase4_bitmap_diff_manifest.json` or `zigux/tests/phase4_bitmap_diff_survey.zig`, so the reviewer-facing gate definition is narrower than the current matrix and build entrypoint.

## Next Safe Step
- Add `phase4-bitmap-diff-survey` to `zigux/Makefile` so the Linux-style local replay surface matches the already-landed shared build step and the current Phase 4 lab matrix.
- Widen `scripts/zigux/validate-phase4.py` and the Phase 4 line in `Documentation/zigux/review-checklist.md` just enough to require `zigux/tests/phase4_bitmap_diff_manifest.json`, `zigux/tests/phase4_bitmap_diff_survey.zig`, and the matching build and matrix markers.

## Out Of Scope
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- Phase 4 perf-threshold approval
- bitmap helper implementation changes
- artifact-diff tooling changes
