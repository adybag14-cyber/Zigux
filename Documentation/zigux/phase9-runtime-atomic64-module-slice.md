# Phase 9 Runtime Atomic64 Module Slice

This document tracks the first bounded Phase 9 runtime atomic64 starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`
- scope: lifecycle starter, direct sample, module, diff, and loader shared-build wiring, adjacent loader scaffold, prepared loader-summary snapshot replay, shared loader-request binding, selftest summary, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `zigux/tests/runtime_atomic64_module.zig`
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`

## Why this slice exists

The live Phase 9 tree had already identified `lib/atomic64_test.c` as the runtime pilot anchor, but it still stopped at a survey-only state. This slice lands the smallest honest runtime-facing follow-on step: a sample-backed lifecycle scaffold that reuses the existing atomic helper wrappers without claiming loadable-module parity.

The adjacent shared runtime-loader blocker also remains underneath the freeze map's study boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this starter may describe the bounded in-memory sample, the sample-side loader scaffold, and the shared loader-request binding, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

No parity scorecard entry or Architecture Council status-change request is attached to this runtime atomic64 starter packet. The reviewable evidence here remains limited to the shipped starter, its direct sample, module, diff, and loader build legs, the shared loader-request binding, and the still-blocked shared loader-control posture that keeps the packet pre-execution.

The current module-slice packet is pinned to `master` commit `d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`.
This keeps later starter-surface or governance edits from silently drifting past this note.

## Landed starter surface

- module descriptor metadata naming the `lib/atomic64_test.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a 64-bit counter path using `zigux/helpers/atomic.zig`
- a selftest summary that groups the C anchor into arithmetic, bitwise, returning, swap, and guard-operation families
- a direct post-selftest mutation replay proof that `selftest_complete` still permits bounded counter replay and keeps `RuntimeAtomic64Summary` explicit until exit
- the bounded guard-return trio from `lib/atomic64_test.c`: `add_unless`, `inc_not_zero`, and `dec_if_positive`
- a narrow differential gate under `zigux/tests/runtime_atomic64_diff.zig` for bounded add, sub, bitwise, swap, compare-swap, and guard-return expectations drawn from `lib/atomic64_test.c`
- a landed sample-side loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` plus a shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig`
- a prepared loader-summary snapshot replay that freezes the four-field `RuntimeAtomic64Summary` handoff before later sample mutation and keeps that same snapshot explicit through both `waiting_on_runtime_substrate` and `released_without_substrate` review paths
- a bounded shared `command_name` preservation check in `samples/zigux/runtime_atomic64_loader.zig` that keeps a synthetic non-null loader request reviewable through both `waiting_on_runtime_substrate` and `released_without_substrate` without claiming live argv policy or runtime execution
- dedicated Phase 9 tests, including direct `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-diff-tests`, and `phase9-runtime-atomic64-loader-tests` legs, plus a `make -C zigux phase9` entry

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux module
- runtime module init and exit macro parity
- boot-time or module-load execution
- parity or ownership for `kernel/workqueue.c`
- any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision

## Gates

1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`
- this shared build includes the direct `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-diff-tests`, and `phase9-runtime-atomic64-loader-tests` legs alongside the atomic64 module, diff, survey, loader, and shared runtime-loader checks

2. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and keep future work narrowly aimed at the remaining runtime substrate handoff or broader shared loader-control blocker, rather than reopening already-landed starter, loader-request, or differential scaffolds.
