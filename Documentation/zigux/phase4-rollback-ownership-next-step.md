# Phase 4 Rollback Ownership Next Step

This note records one bounded same-lane verification pass for the shared Phase 4 rollback-ownership, lab-matrix, and reversible-delivery evidence surfaces.

## Status
- lane: `P4-L23`
- phase: `Phase 4`
- date: `2026-05-07`
- evidence mode: `github_connector_readback`
- scope: `rollback_ownership_and_lab_matrix_tighten_reversible_delivery_evidence_for_existing_work`

## Current Repo Evidence
- `Documentation/zigux/phase4-validation-matrix.md` and `Documentation/zigux/phase4-gate-evidence.md` remain the shared Phase 4 rollback-ownership and lab-matrix notes on `master`.
- `zigux/tests/phase4_build.zig` already wires `zigux/tests/phase4_bitmap_diff_survey.zig` into the shared Phase 4 entrypoint as both `phase4-bitmap-diff-survey-tests` and `phase4-bitmap-diff-survey`.
- `Documentation/zigux/phase4-validation-matrix.md` now gives `zigux/tests/phase4_bitmap_diff_survey.zig` its own owner and rollback-owner row under `Shared Subsystems Pod`, and the same Lab And CI Matrix now names the direct local replay route `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`.
- `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` now agree with the live `Documentation/zigux/phase4-gate-evidence.md` blob on `master`, so the earlier bitmap survey packet blob-drift repair is already landed and no longer the missing same-lane step.
- `zigux/Makefile` now exposes `phase4-bitmap-diff-survey` in the Phase 4 `PHONY` list and as a dedicated Linux-style wrapper recipe, so the local replay surface has already caught up with the shared matrix and build entrypoint.
- The remaining shared-surface drift is now narrower than the older note claimed: `scripts/zigux/validate-phase4.py` still omits `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` from `REQUIRED_FILES`, the shared Phase 4 root-summary marker lists, `REQUIRED_REVIEW_CHECKLIST_MARKERS`, `REQUIRED_PHASE4_MATRIX_MARKERS`, and `REQUIRED_PHASE4_BUILD_MARKERS`, so the shared validator still under-names the already-landed bitmap survey packet.
- The reviewer-facing and root-summary surfaces still trail the live matrix and build route in the same way: `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still describe the shared Phase 4 packet without explicitly naming `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` beside the existing bitmap rollback gate and helper-backed replay surfaces.

## Next Safe Step
- Widen `scripts/zigux/validate-phase4.py` just enough to require `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` across `REQUIRED_FILES`, the shared Phase 4 summary markers, the reviewer-checklist markers, the matrix markers, and the Phase 4 build markers.
- Refresh `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` just enough to name that already-landed bitmap survey packet beside the current bitmap rollback gate and helper-backed replay, so the shared reversible-delivery evidence matches the live matrix, gate-evidence note, Makefile wrapper, and build entrypoint.

## Out Of Scope
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- Phase 4 perf-threshold approval
- bitmap helper implementation changes
- artifact-diff tooling changes
