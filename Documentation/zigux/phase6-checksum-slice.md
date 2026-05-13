# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper anchor: `lib/checksum.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`
- current `master` still lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` still keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`

## Review Surface
- still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- blocked route note: the checked-in direct C parity scaffolding is not currently runnable as a complete packet because `zigux/tests/phase6_checksum_c_parity.zig` still imports the absent `lib/checksum.zig` helper and the absent `zigux/tests/fixtures/phase6_checksum_vectors.zig` fixture module
- direct local C parity checker route once the helper packet is restored: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `27` direct C parity cases and preserves the last blocked slowdown packet as `64B` at `iterations = 200000` and `1501B` at `iterations = 12000`, both with `max_slowdown_pct = 150`
- stale shared route surfaces that still point at the absent broader checksum helper packet: `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet, but current `master` only keeps the direct C parity scaffolding, and it cannot honestly claim the broader helper-local replay or slowdown gate until the missing checksum helper and fixture packet return

## Next Step
Keep this lane parked unless a future checksum follow-up either restores `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, or narrows the checksum-owned shared route surfaces so they stop advertising the absent helper packet as runnable from the committed tree.
