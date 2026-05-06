# Phase 9 Runtime Atomic64 Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/atomic64_test.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L02`
- `PHASE9_SURVEYED_COMMIT=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: survey manifest, dedicated runtime survey gate, landed sample-backed module starter, landed module gate, landed diff gate, the bounded sample-side loader scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, and the lane-level review note that keeps the still-unlanded shared runtime-loader substrate explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/runtime_atomic64_survey.zig`
  - `zigux/tests/runtime_atomic64_module.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase9-runtime-atomic64-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/atomic64_test.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The survey artifacts now advance to `P9-L02` because the bounded sample-side loader scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, and the shared request-surface proof are landed and reviewable on `master`. That keeps the survey history honest while also making the active packet metadata match the current runtime atomic64 review surface.

The live repo now has a bounded `runtime_atomic64` starter, dedicated module tests, a dedicated diff gate, a bounded sample-side loader scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, and shared Phase 9 build coverage, so this survey note should reflect the landed pilot review surface instead of still reading like the lane stops before any loader-shaped lifecycle handoff.

## Survey findings

- `lib/atomic64_test.c` is present on `master` at 277 lines.
- the live repo now ships `samples/zigux/runtime_atomic64.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/runtime_atomic64_survey.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane, including the focused `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig` shard for the shared runtime-loader facade, contract, and allocator/init-flow packet.
- the bounded starter keeps atomic exchange, compare-swap, add-unless, and selftest-hook behavior reviewable without claiming a real loadable runtime module.
- the roadmap's selftest-hook requirement is already landed through the sample descriptor and `runSelftest()` contract in `samples/zigux/runtime_atomic64.zig`.
- the bounded sample-side loader scaffold now records explicit init and exit symbol names, a prepared handoff summary, and the no-substrate release path without claiming that a shared runtime loader already exists.
- guarded init, selftest, and exit transitions plus the bounded loader handoff make lifecycle evidence reviewable, but full runtime module lifecycle parity still depends on the shared runtime substrate.
- the live repo now also carries `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and `zigux/Makefile`, and the atomic64 loader packet now makes its shared request-surface proof explicit through `toSharedLoadPlan()` plus `runtime_loader.prepareRequest()` while keeping the allocator handoff, init-flow counts, release-without-substrate path, and Linux-style `make -C zigux phase9` replay route reviewable without claiming a real module-loading substrate.
- the shared `zigux/kernel/runtime_loader.zig` facade remains a review-only Phase 9 packet under the freeze map's study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` boundary, so this lane keeps the handoff proof explicit without claiming scheduler-facing substrate closure or a freeze-map status change.
- runtime substrate work is still missing, so the lane intentionally stops at bounded lifecycle, selftest-hook, and loader-handoff behavior rather than claiming real module registration parity.

## Direct Sample Checks

The current direct atomic64 sample contract is verified through these exact checks:

- descriptor contract: the sample still advertises `name=runtime_atomic64`, `anchor=lib/atomic64_test.c`, `requires_runtime_substrate=true`, and `provides_selftest_hook=true`
- lifecycle and counter path: the sample still starts cold, rejects selftest before init, records one init run, swaps the seeded `0x1111_1111_2222_2222` counter down to `-9`, proves both compare-swap store and mismatch visibility, drives the blocked and changed `add_unless` branches, and finishes the bitwise path at counter `19`
- selftest closure: `runSelftest()` still reports the ordered operation families `arithmetic`, `bitwise`, `returning_ops`, `swap_ops`, and `guard_ops`, keeps the counter stable at `19`, records one selftest run, and leaves later swap or second-selftest attempts blocked after exit
- loader snapshot stability: after `prepare()` captures the selftest-complete handoff with counter snapshot `17`, later sample mutation still leaves the pending loader handoff at snapshot `17` even while the live sample moves through swap, compare-swap, `add_unless`, `and`, and `xor` to the visible counter `15` before `requestRuntimeLoad()`
- shared loader-request binding: `toSharedLoadPlan()` and `runtime_loader.prepareRequest()` still preserve the caller-provided allocator handoff, the bounded init-flow counts, the `waiting_on_runtime_substrate` transition, and the exact prepared snapshot without claiming a real loadable runtime substrate on `master`

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-atomic64-survey-gate`
- the landed `runtime-atomic64-sample-module`
- the landed `runtime-atomic64-selftest-hook`
- the landed `runtime-atomic64-module-tests`
- the landed `runtime-atomic64-diff-gate`
- the landed `runtime-atomic64-loader-scaffold`
- the still-blocked `runtime-atomic64-live-loader-binding`

This keeps the roadmap's selftest-hook requirement explicitly landed while still parking full runtime module lifecycle parity under the shared runtime-loader blocker.

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a loadable Zigux runtime atomic64 module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_atomic64.zig` module
- direct parity for the full `lib/atomic64_test.c` surface beyond the bounded starter and diff gate

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and keep broader work blocked until a shared runtime-loader substrate actually lands on `master` and can consume the bounded init, selftest, and exit handoff plan.
