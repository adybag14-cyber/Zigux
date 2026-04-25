# Phase 9 Runtime Atomic64 Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/atomic64_test.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- scope: survey manifest, dedicated runtime test gate, and Phase 9 build entry only
- product boundary:
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/runtime_atomic64_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/atomic64_test.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo still carried the Linux atomic64 runtime test, but it had no dedicated Phase 9 build gate, no `runtime_*` Zigux tests, and no `samples/zigux/` pilot-module scaffold. The highest-value lane-local step was to make that gap explicit and reviewable before any sample module code claims to exist.

## Survey findings

- `lib/atomic64_test.c` is present on `master` at 277 lines.
- the repo had zero `zigux/tests/runtime_*` files before this survey landed.
- the repo had no `samples/zigux/` directory before this survey landed.
- the repo had no `zigux/tests/phase9_build.zig` gate and no dedicated Phase 9 runtime note before this survey landed.

## Recorded gaps

The manifest captures three bounded follow-on gaps:

- `phase9-build-gate`
- `runtime-atomic64-survey-gate`
- `runtime-atomic64-sample-module`

The first two are `ready_next` reviewability and validation steps. The sample module itself stays blocked on the runtime module lifecycle substrate so this lane does not create a fake pilot module just to make the tree look busy.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a loadable Zigux runtime module implementation
- runtime module lifecycle parity
- selftest hook parity
- a `samples/zigux/runtime_atomic64.zig` sample

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and start the first honest runtime-facing scaffold, most likely a tiny sample-backed module lifecycle skeleton under `samples/zigux/` once the runtime substrate boundary is ready to host it.
