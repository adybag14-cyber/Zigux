# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper expected by the shared packet: `lib/checksum.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`
- current `master` still lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` still keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- current routed build packet still omits checksum wiring from `zigux/tests/phase6_build.zig`, and `zigux/Makefile` still advertises `phase6-checksum-c-parity` and `phase6-checksum-perf` phony routes without corresponding target bodies

## Review Surface
- still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- blocked route note: the checked-in direct C parity scaffolding is not currently runnable as a complete packet because `zigux/tests/phase6_checksum_c_parity.zig` still imports the absent `lib/checksum.zig` helper and the absent `zigux/tests/fixtures/phase6_checksum_vectors.zig` fixture module
- make/workflow drift note: `zigux/Makefile` still names `phase6-checksum-c-parity` and `phase6-checksum-perf` as phony routes without target bodies, while `.github/workflows/zigux-bootstrap.yml` only self-tests `scripts/zigux/check-phase6-checksum-c-parity.py` instead of running a restored checksum helper packet
- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet, but current `master` only keeps the direct C parity scaffolding, and it cannot honestly claim the broader helper-local replay or slowdown gate until the missing checksum helper and fixture packet return

## Next Step
Keep this lane parked unless a future checksum follow-up closes one checksum-only route truthfulness gap. The next bounded reopen should restore `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` on `master`, then wire any returned helper packet through `zigux/tests/phase6_build.zig`, add concrete `phase6-checksum-c-parity` and `phase6-checksum-perf` target bodies in `zigux/Makefile`, and upgrade `.github/workflows/zigux-bootstrap.yml` from checker self-test only to an actual checksum packet run.
