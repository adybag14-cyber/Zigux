# Phase 9 Runtime Atomic64 Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/atomic64_test.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- scope: survey manifest, dedicated runtime survey gate, landed sample-backed module starter, landed module gate, landed diff gate, the bounded sample-side loader scaffold, and the lane-level review note that keeps the remaining runtime-loader blocker explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/runtime_atomic64_survey.zig`
  - `zigux/tests/runtime_atomic64_module.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-atomic64-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/atomic64_test.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The survey artifacts stay anchored to the original `P9-L01` survey lane even though later neighboring runs landed the `runtime_atomic64` starter, dedicated module tests, diff gate, and now the bounded sample-side loader scaffold. That keeps the survey history honest while still recording the full live review surface.

The live repo now has a bounded `runtime_atomic64` starter, dedicated module tests, a dedicated diff gate, a bounded sample-side loader scaffold, and shared Phase 9 build coverage, so this survey note should reflect the landed pilot review surface instead of still reading like the lane stops before any loader-shaped lifecycle handoff.

## Survey findings

- `lib/atomic64_test.c` is present on `master` at 277 lines.
- the live repo now ships `samples/zigux/runtime_atomic64.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/runtime_atomic64_survey.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- the bounded starter keeps atomic exchange, compare-swap, add-unless, and selftest-hook behavior reviewable without claiming a real loadable runtime module.
- the bounded sample-side loader scaffold now records explicit init and exit symbol names, a prepared handoff summary, and the no-substrate release path without claiming that a shared runtime loader already exists.
- runtime substrate work is still missing, so the lane intentionally stops at bounded lifecycle, selftest-hook, and loader-handoff behavior rather than claiming real module registration parity.

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-atomic64-survey-gate`
- the landed `runtime-atomic64-sample-module`
- the landed `runtime-atomic64-module-tests`
- the landed `runtime-atomic64-diff-gate`
- the landed `runtime-atomic64-loader-scaffold`
- the still-blocked `runtime-atomic64-live-loader-binding`

This keeps the lane concrete without pretending that Zigux already has a live `zigux/kernel/runtime_loader.zig` binding or full runtime module lifecycle parity.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a loadable Zigux runtime atomic64 module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_atomic64.zig` module
- direct parity for the full `lib/atomic64_test.c` surface beyond the bounded starter and diff gate

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded init and exit handoff plan.
