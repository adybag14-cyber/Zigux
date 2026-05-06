# Phase 9 Runtime Atomic64 Module Slice

This document tracks the first bounded Phase 9 runtime atomic64 starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L01`
- scope: lifecycle starter, selftest hook surface, guarded lifecycle parity evidence, dedicated Phase 9 test wiring, a bounded loader-handoff scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, shared request-surface proof, dedicated runtime survey gate, survey-note ownership closure, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_atomic64_module.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/runtime_atomic64_survey.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `Documentation/zigux/phase9-runtime-atomic64-survey.md`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The live Phase 9 tree had already identified `lib/atomic64_test.c` as the runtime pilot anchor, but it still stopped at a survey-only state. This slice lands the smallest honest runtime-facing follow-on step: a sample-backed lifecycle scaffold that reuses the existing atomic helper wrappers without claiming loadable-module parity.

## Landed starter surface

- module descriptor metadata naming the `lib/atomic64_test.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a selftest hook surface that keeps `runSelftest()` reviewable without requiring runtime substrate support
- a 64-bit counter path using `zigux/helpers/atomic.zig`
- a selftest summary that groups the C anchor into arithmetic, bitwise, returning, swap, and guard-operation families
- a narrow `add_unless` guard-path pilot on top of the existing atomic helpers without pretending broader runtime-substrate support
- a narrow differential gate under `zigux/tests/runtime_atomic64_diff.zig` for selected exchange, cmpxchg, and `add_unless` expectations
- a bounded `runtime_atomic64_loader` scaffold that names the planned init and exit handoff, the current atomic64 operation-family summary, the shared `toSharedLoadPlan()` plus `runtime_loader.prepareRequest()` request path, the shared request-surface proof, and the no-substrate release path while the real runtime substrate remains unavailable
- the shared `zigux/kernel/runtime_loader.zig` facade stays a review-only Phase 9 handoff packet under the freeze map's study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` boundary, so the starter keeps the shared request path explicit without implying scheduler-facing substrate closure or a freeze-map status change
- dedicated Phase 9 tests, the runtime atomic64 survey note and survey gate, the focused `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig` shard for the shared runtime-loader facade plus allocator/init-flow contract packet, and a `make -C zigux phase9` entry

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux module
- runtime module init and exit macro parity
- boot-time or module-load execution

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded init, selftest, and exit handoff plan beyond the current shared load-plan and request facade and turn this guarded evidence into real runtime module lifecycle parity.
