# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=blocked`
- roadmap anchor: `lib/checksum.c`
- helper anchor: `lib/checksum.zig`
- current `master` still lacks the broader checksum helper packet under `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` still keeps the direct checksum C parity scaffolding under `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`

## Review Surface
- stale shared routes that still point at the absent broader checksum helper packet: `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- the checked-in direct C parity surface is not currently runnable as a complete packet because `zigux/tests/phase6_checksum_c_parity.zig` still imports the absent `lib/checksum.zig` helper and the absent `zigux/tests/fixtures/phase6_checksum_vectors.zig` fixture module
- this slice is blocked until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state

## Next Step
Keep this lane parked unless a future checksum follow-up either restores `lib/checksum.zig` plus the checksum-owned replay and fixture files, or narrows the shared Phase 6 routes so they stop advertising the absent checksum helper packet as runnable from the committed tree.
