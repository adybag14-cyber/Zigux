# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_AT=2026-05-12`
- scope: lifecycle starter, dedicated sample and diff packet, directly readable module and loader packet, adjacent shared-request binding, initialized and selftest-complete shared-request snapshot replays, shared runtime-loader facade plus allocator/init-flow contract replay, selftest summary, failed-exit retention until drain, maxactive-overflow retention until drain, and survey-manifest closure while the shared runtime substrate remains blocked
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`

## Why This Slice Exists

The live Phase 9 tree still identifies `samples/kprobes/kretprobe_example.c` as the runtime pilot anchor, and the current review packet keeps a sample-root guide, a directly readable loader scaffold, a dedicated sample and diff leg, a module test, a manifest, and shared allocator/init-flow proof on `master`.

This slice keeps the smallest honest runtime-facing note in place: a sample-backed lifecycle scaffold that makes the kretprobe handoff, tracing proof, and failure-mode evidence reviewable without claiming loadable-module parity. The current Phase 9 build packet, sample-root guidance, and dedicated survey gate keep `samples/zigux/runtime_kretprobe.zig` and `zigux/tests/runtime_kretprobe_diff.zig` explicit beside the loader and module packet, so this note can describe the landed starter family directly rather than restating those tracing legs as missing review debt.

`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in review-only study scope for the shared loader packet, so this starter may describe the bounded in-memory handoff plan, the sample-side contract, the sample-side loader scaffold, the shared loader-request binding, and the shared runtime-loader contract replay, but it must not imply scheduler parity, live runtime registration ownership, or any Architecture Council-approved status change.

## Landed Starter Surface
- module descriptor metadata and lifecycle review coverage remain directly readable through `zigux/tests/runtime_kretprobe_module.zig`
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- bounded return-probe bookkeeping for skipped kernel threads, duration tracking, missed instances, and explicit selftest summaries
- direct failed-exit replay coverage that keeps outstanding-probe state explicit until the active probe drains instead of pretending exit is already safe
- direct maxactive-overflow replay coverage that keeps pressure-induced missed-instance state explicit until the active probe drains
- a landed sample-side loader scaffold under `samples/zigux/runtime_kretprobe_loader.zig` plus a shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig`
- an initialized-stage shared-request snapshot replay that freezes the prepared handoff before later sample selftest activity and keeps that same snapshot explicit through both `waiting_on_runtime_substrate` and `released_without_substrate` review paths
- a selftest-complete shared-request snapshot replay that stays explicit even if later sample exit activity runs before the shared runtime-loader handoff
- direct shared selftest-hook evidence rejection in the shared request surface plus prepared selftest-hook drift rejection and prepared shared-plan drift rejection that keep the loader packet truthful about the currently shipped review surface
- the current Phase 9 build packet, sample-root guidance, and dedicated survey gate keep `samples/zigux/runtime_kretprobe.zig` and `zigux/tests/runtime_kretprobe_diff.zig` explicit as the dedicated sample and diff legs for bounded maxactive, missed-instance, overlapping-entry, and duration expectations drawn from `samples/kprobes/kretprobe_example.c`, so that tracing-proof slice is part of the landed starter packet instead of blocked review debt
- dedicated Phase 9 tests still include direct `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and the shared `phase9-runtime-loader-shared-tests` shard plus the workflow-backed `make -C zigux phase9` route, while the missing runtime substrate remains the next blocker to honest loadable-module parity

## Non-Goals

This slice does not yet claim:
- a kernel-loadable Zigux module
- live `register_kretprobe` or `unregister_kretprobe` execution parity
- boot-time or module-load execution
- parity or ownership for the shared runtime substrate under the freeze map boundary
- any freeze-map status change without an Architecture Council decision

## Gates
1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`
- the broader build packet keeps the direct `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, and `phase9-runtime-kretprobe-loader-tests` legs together with the kretprobe survey gate and the shared runtime-loader facade, contract, and allocator/init-flow checks, so the starter remains reviewable as one bounded family while the loadable runtime substrate is still blocked
2. run the convenience target
- `make -C zigux phase9`

## Next Bounded Step

Stay in the Phase 9 runtime kretprobe lane and keep the directly readable sample, diff, module, loader, manifest, and survey packet synchronized while the shared runtime substrate remains the next blocker to loadable-module parity.

## Footer
