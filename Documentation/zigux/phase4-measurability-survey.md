# Phase 4 Measurability Survey

This note records the remaining Phase 4 measurability gaps between the roadmap and the live repo.

## Status

- `PHASE4_STATUS=active`
- `PHASE4_SLICE=phase4-measurability-survey`
- scope: bounded survey manifest, dedicated survey gate, and the Phase 4 note that now records what is landed versus what still lacks rollback ownership, lab and CI matrices, and perf thresholds
- product boundary:
  - `zigux/tests/phase4_measurability_manifest.json`
  - `zigux/tests/phase4_measurability_survey.zig`
  - `zigux/tests/phase4_build.zig`
  - `Documentation/zigux/phase4-measurability-survey.md`

## Why this slice exists

The roadmap says Phase 4 should make every future Zigux port measurable and reversible. The live repo already has bounded atomic64 and bitmap diff gates, but it does not yet carry an explicit record of rollback ownership or the missing lab and CI matrices beside those gates.

This survey keeps that gap explicit without widening into new sample ports or pretending that the missing matrix and threshold work is already solved.

## Survey findings

- the live Phase 4 validation surface already includes `zigux/tests/phase4_build.zig` and `scripts/zigux/validate-phase4.py`
- the live repo already carries two landed rollback-readiness diff gates: `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig`
- the recommended Phase 4 sample destinations `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` are still absent from the live repo
- the documentation root mentions the Phase 4 validator, but there was no dedicated Phase 4 survey note, no explicit rollback ownership table, and no lab matrix note before this slice
- the bootstrap workflow runs a single shared Phase 4 build entrypoint, but there is still no named Phase 4 CI matrix and no committed perf threshold note

## Recorded gaps

The manifest now records:

- the landed shared Phase 4 build gate
- the landed Phase 4 validator gate
- the landed survey note, manifest, and survey test
- the next explicit rollback ownership record
- the next lab and CI matrices note
- the next perf threshold note
- the still-blocked reference-sample surface, because the current sample paths are still missing

## Rollback ownership audit

- shared Phase 4 build gate:
  - runnable through `make -C zigux phase4`
  - still missing an explicit rollback owner
- bounded atomic64 and bitmap diff files:
  - reversible through the shared Phase 4 gate
  - still missing an explicit rollback owner for narrowing or reverting a drifting expectation
- Phase 4 reference sample paths:
  - no honest rollback owner yet because the files are still missing

## Lab matrix audit

- current bootstrap coverage:
  - one shared Phase 4 entrypoint in `.github/workflows/zigux-bootstrap.yml`
- missing lab and CI matrices:
  - no named CI matrix for Phase 4 targets or configurations
  - no committed lab matrix note for the four roadmap anchors
- missing perf thresholds:
  - no committed baseline or threshold note for Phase 4 yet

## Gates

1. Run the Phase 4 validator
- `python3 scripts/zigux/validate-phase4.py`

2. Run the shared Phase 4 build gate
- `zig build test --build-file zigux/tests/phase4_build.zig`

3. Run the convenience target
- `make -C zigux phase4`

## Non-goals

This survey slice does not claim:

- that rollback ownership is already assigned
- that a Phase 4 lab matrix or CI matrix already exists
- that perf thresholds are already committed
- that the missing `samples/zigux/` Phase 4 paths are real reference ports

## Next bounded step

Stay in the same Phase 4 measurability lane and add one explicit rollback ownership table plus one minimal lab-matrix record next, but only after fresh repo inspection confirms those notes can stay tied to the current diff-gate surface instead of widening into Phase 5 sample work.