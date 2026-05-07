# Phase 4 Artifact-Diff Validator Next Step

This note records one bounded Phase 4 scripts-only mismatch on `master` so the next same-lane follow-up can repair it without widening beyond the shared host-side diff tooling packet.

## Scope
- lane family: `P4-Y06`
- scope: `scripts/zigux` diff tooling only
- roadmap phase: `Phase 4: Differential Validation and Rollback`
- excluded surfaces: `zigux/tests/bitmap_diff.zig`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, sample-gap notes, perf-threshold approval work, and broader Phase 4 matrix rewrites

## Current Readback
- `scripts/zigux/artifact_diff.py` blob: `d78e7a2c976d2c8d1d90904e36e3349dcfe9499c`
- `scripts/zigux/check-artifact-diff-contract.py` blob: `4007f376d422f2d38ef3d14b6f2a9cb28281d722`
- `scripts/zigux/validate-phase4.py` blob: `60dd5759e0c149f70802e4474b2e22513ceabcab`
- `Documentation/zigux/artifact-diff.md` blob: `f63b23c4f68cf75ae16bf254a509d754f5eaae49`

## Exact Mismatch
- The published contract checker in `scripts/zigux/check-artifact-diff-contract.py` includes `cli_invalid_mode` in `EXPECTED_CONTRACT_CASES` and also executes that parser-failure case in the live contract replay.
- The shared Phase 4 validator in `scripts/zigux/validate-phase4.py` still defines `EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES` without `cli_invalid_mode`.
- Because `validate-phase4.py` exact-checks the `ARTIFACT_DIFF_CONTRACT_CASES=` line emitted by `scripts/zigux/check-artifact-diff-contract.py`, the validator-side expected catalog has drifted behind the live checker-side catalog.
- `Documentation/zigux/artifact-diff.md` still accurately describes invalid-mode contract coverage at the review-note level, so the concrete mismatch is validator expectations rather than helper intent or review-note scope.

## Next Safe Step
- Keep the follow-up bounded to `scripts/zigux/validate-phase4.py`.
- Add `cli_invalid_mode` to `EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES` in the same position already used by `scripts/zigux/check-artifact-diff-contract.py`.
- Re-run the narrowest honest checks available for this packet only: the validator's contract-summary expectation path and the validator self-test path.
- Do not widen that follow-up into bitmap, atomic64, sample-gap, or perf-threshold work.

## Why This Note Exists
- This lane run used GitHub connector readback only; there was no local Zigux checkout or Devbox-backed validation path available for a direct script edit plus replay.
- Recording the exact mismatch, file set, and bounded repair step is safer than widening into unrelated Phase 4 surfaces or guessing at a broader fix without a stronger local execution path.
