# Phase 4 Rollback Ownership Next Step

This note records one bounded same-lane follow-up for the shared Phase 4 rollback-ownership and lab-matrix control surface.

## Status
- lane: `P4-L20`
- phase: `Phase 4`
- date: `2026-05-07`
- evidence mode: `github_connector_readback`
- scope: `rollback_ownership_and_lab_matrix_control_surface_only`

## Current Repo Evidence
- `Documentation/zigux/phase4-validation-matrix.md` and `Documentation/zigux/phase4-gate-evidence.md` remain the shared Phase 4 rollback-ownership and lab-matrix notes on `master`.
- `zigux/tests/phase4_build.zig` already wires `zigux/tests/phase4_bitmap_diff_survey.zig` into the shared Phase 4 entrypoint as both `phase4-bitmap-diff-survey-tests` and `phase4-bitmap-diff-survey`.
- `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig` now agree with the live `Documentation/zigux/phase4-gate-evidence.md` blob on `master`, so the earlier bitmap survey packet repair is already landed and no longer the missing same-lane step.
- The shared matrix still does not give `zigux/tests/phase4_bitmap_diff_survey.zig` its own owner plus rollback-owner row or its own explicit Lab And CI Matrix route.
- `scripts/zigux/validate-phase4.py` still treats the shared Phase 4 packet as if it ends at `zigux/tests/bitmap_diff.zig` and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; it does not currently require `zigux/tests/phase4_bitmap_diff_manifest.json` or `zigux/tests/phase4_bitmap_diff_survey.zig`.

## Next Safe Step
- Promote the already-shipped bitmap survey packet into `Documentation/zigux/phase4-validation-matrix.md` with one explicit owner and rollback-owner row plus the matching bootstrap-CI and local lab replay commands.
- After that matrix row lands, widen `scripts/zigux/validate-phase4.py` just enough to require `zigux/tests/phase4_bitmap_diff_manifest.json`, `zigux/tests/phase4_bitmap_diff_survey.zig`, and the corresponding shared build markers.

## Out Of Scope
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- Phase 4 perf-threshold approval
- bitmap helper implementation changes
- artifact-diff tooling changes
