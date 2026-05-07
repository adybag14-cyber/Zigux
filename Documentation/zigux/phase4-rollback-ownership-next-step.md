# Phase 4 Rollback Ownership Next Step

This note records one bounded same-lane follow-up for the shared Phase 4 rollback-ownership and lab-matrix control surface.

## Status
- lane: `P4-Y08`
- phase: `Phase 4`
- date: `2026-05-07`
- evidence mode: `github_connector_readback`
- scope: `rollback_ownership_and_lab_matrix_control_surface_only`

## Current Repo Evidence
- `Documentation/zigux/phase4-validation-matrix.md` and `Documentation/zigux/phase4-gate-evidence.md` remain the shared Phase 4 rollback-ownership and lab-matrix notes on `master`.
- `zigux/tests/phase4_build.zig` already wires `zigux/tests/phase4_bitmap_diff_survey.zig` into the shared Phase 4 entrypoint as both `phase4-bitmap-diff-survey-tests` and `phase4-bitmap-diff-survey`.
- `zigux/tests/phase4_bitmap_diff_manifest.json` already records `phase4_build_uses_bitmap_diff_survey=true`, so the shipped bitmap reviewability survey is not just a draft lane idea.
- The same manifest still pins `gate_evidence_blob_sha=3832b62978802753bf89d720a36d3f23a2b264b6`, while the current `Documentation/zigux/phase4-gate-evidence.md` blob on `master` reads back as `58161e8d41ee8d86d24da722738d986f182900b5`.
- `scripts/zigux/validate-phase4.py` still treats the shared Phase 4 packet as if it ends at `zigux/tests/bitmap_diff.zig` and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; it does not currently require `zigux/tests/phase4_bitmap_diff_manifest.json` or `zigux/tests/phase4_bitmap_diff_survey.zig`.

## Next Safe Step
- First repair only the bitmap survey packet so `zigux/tests/phase4_bitmap_diff_manifest.json`, `zigux/tests/phase4_bitmap_diff_survey.zig`, and `Documentation/zigux/phase4-gate-evidence.md` agree on the live gate-evidence blob again.
- After that repair lands, the next same-lane follow-up can promote the bitmap survey into `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `scripts/zigux/validate-phase4.py` with one explicit owner/rollback-owner row plus the matching CI and local replay commands.

## Out Of Scope
- `samples/zigux/kprobe_example.zig`
- `samples/zigux/test_fsmount.zig`
- Phase 4 perf-threshold approval
- bitmap helper implementation changes
- artifact-diff tooling changes
