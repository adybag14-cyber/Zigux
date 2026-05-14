# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper anchor: `lib/checksum.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`
- current public `master` now keeps `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current public `master` also keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- current routed build packet still omits checksum wiring from `zigux/tests/phase6_build.zig`, and `zigux/Makefile` still advertises `phase6-checksum-c-parity` and `phase6-checksum-perf` phony routes without corresponding target bodies

## Review Surface
- helper surface: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- perf gate runner: `zigux/tests/phase6_checksum_perf.zig`
- compact fixture companion: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- blocked route note: the helper, focused replay, perf runner, and fixture companion are present on current public `master`, but the routed Phase 6 build packet still does not add the checksum module or checksum test/perf steps in `zigux/tests/phase6_build.zig`, so the helper packet is not yet wired into the same direct `zig build ... --build-file zigux/tests/phase6_build.zig` route shape used by the other Phase 6 leaf helpers
- make/workflow drift note: `zigux/Makefile` still names `phase6-checksum-c-parity` and `phase6-checksum-perf` as phony routes without target bodies, while `.github/workflows/zigux-bootstrap.yml` only self-tests `scripts/zigux/check-phase6-checksum-c-parity.py` instead of running the current checksum helper packet itself
- current review posture: blocked; the checksum helper packet has returned to the tree, but current `master` still needs the routed checksum build/perf packet brought back into alignment before it can claim the same runnable review posture as the other landed Phase 6 helpers

## Next Step
Keep this lane parked unless a future checksum follow-up closes one checksum-only route truthfulness gap. The next bounded reopen should wire `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` through `zigux/tests/phase6_build.zig`, add concrete `phase6-checksum-c-parity` and `phase6-checksum-perf` target bodies in `zigux/Makefile`, and then upgrade `.github/workflows/zigux-bootstrap.yml` from checker self-test only to an actual checksum packet run.