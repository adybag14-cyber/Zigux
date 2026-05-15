# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=reviewable`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated perf replay: `zigux/tests/phase6_checksum_perf.zig`
- shared fixture companion: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- direct local helper replay route: `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`
- direct local perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`

## Review Surface
- helper packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- focused parity coverage: the helper replay keeps the shared compute, seeded partial, block-add composition, pseudo-header, carry-discipline, and incremental replacement corpus aligned with the direct C parity runner
- perf posture: the dedicated perf replay keeps the documented `64B` and `1501B` slowdown cases reviewable from committed helper-owned evidence instead of leaving checksum perf thresholds as manifest-only notes
- current shared-route limit: `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the broader Phase 6 shared summaries still need a later follow-up if this lane reopens for wrapper- and inventory-level truthfulness

## Next Step
Leave this slice parked unless a future same-lane follow-up is ready to tighten one of the shared Phase 6 route surfaces. If it reopens soon, prefer the smallest truthful sync in `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, or `zigux/tests/README.md` before widening helper semantics again.
