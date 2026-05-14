# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=partially_blocked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper expected by the shared packet: `lib/checksum.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`
- current `master` keeps `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` also keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- current routed build packet still omits checksum wiring from `zigux/tests/phase6_build.zig`, and `zigux/Makefile` still advertises `phase6-checksum-c-parity` and `phase6-checksum-perf` phony routes without corresponding target bodies

## Review Surface
- restored helper-owned packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- blocked route note: the helper, focused replay, perf runner, and fixture companion are present on current `master`, but `zigux/tests/phase6_build.zig` still does not add a checksum module or checksum test/perf step, so the checksum packet is not yet wired through the same direct `zig build ... --build-file zigux/tests/phase6_build.zig` route shape used by the other landed Phase 6 helpers
- make/workflow drift note: `zigux/Makefile` still names `phase6-checksum-c-parity` and `phase6-checksum-perf` as phony routes without target bodies, while `.github/workflows/zigux-bootstrap.yml` only self-tests `scripts/zigux/check-phase6-checksum-c-parity.py` instead of running the restored checksum helper packet
- current review posture: partially blocked; current `master` now keeps the checksum helper, focused replay, dedicated perf runner, fixture companion, and direct C parity scaffolding, but the routed checksum build/perf packet still lags the restored helper-owned surface so the checksum leg cannot yet claim the same runnable shared-route posture as the landed base64, bsearch, and hexdump evidence

## Next Step
Keep this lane parked unless a future checksum follow-up closes one checksum-only route truthfulness gap. The next bounded reopen should wire the restored helper packet through `zigux/tests/phase6_build.zig`, add concrete `phase6-checksum-c-parity` and `phase6-checksum-perf` target bodies in `zigux/Makefile`, and upgrade `.github/workflows/zigux-bootstrap.yml` from checker self-test only to an actual checksum packet run.
