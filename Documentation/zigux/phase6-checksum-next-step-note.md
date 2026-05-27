# Phase 6 Checksum Next-Step Note

This note turns the current `master` readback for the Phase 6 checksum helper into one bounded follow-through instruction.

## Current readback

A targeted authenticated current-master reread on 2026-05-27 directly reconfirmed the checksum-local packet through:

- `lib/checksum.zig`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase6_checksum_perf.zig`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `Documentation/zigux/phase6-checksum-slice.md`
- `Documentation/zigux/phase6-helper-evidence-catalog.md`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `zigux/tests/phase6_helper_evidence_manifest.json`
- `zigux/tests/phase6_helper_parity_manifest.json`
- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`

That current repo evidence shows the checksum helper is already landed, wired into the shared Phase 6 build routes, covered by a direct C parity hook, and guarded by both payload and IPv4 fast-path perf matrices.

## Bounded next step

Leave the checksum helper parked unless fresh repo inspection finds checksum-local drift in one of these areas only:

- helper semantics in `lib/checksum.zig`
- focused correctness replay in `zigux/tests/phase6_checksum.zig`
- payload or IPv4 fast-path perf thresholds in `zigux/tests/phase6_checksum_perf.zig`
- committed checksum fixtures in `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct C parity glue in `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, or `scripts/zigux/check-phase6-checksum-c-parity.py`

If the helper reopens, start with the checksum-local rerun packet below before touching any shared Phase 6 note or another helper family:

- `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`
- `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`
- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`

## Lane boundary

This note is checksum-only. It is not evidence to reopen `base64`, `bsearch`, `hexdump`, or the broader shared Phase 6 reminder packet.
