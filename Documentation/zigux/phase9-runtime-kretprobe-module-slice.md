# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_AT=2026-05-11`
- scope: lifecycle starter, direct sample, module, diff, and loader shared-build wiring, adjacent loader scaffold, initialized and selftest-complete shared-request snapshot replays, shared loader-request binding, shared runtime-loader facade plus allocator/init-flow contract replay, selftest summary, failed-exit retention until drain, maxactive-overflow retention until drain, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`

## Why This Slice Exists

The live Phase 9 tree already identified `samples/kprobes/kretprobe_example.c` as the runtime pilot anchor, but the current review packet had lost the kretprobe-specific module note even though the starter, loader, and survey surfaces are already landed on `master`.

This slice restores the smallest honest runtime-facing follow-on note: a sample-backed lifecycle scaffold that keeps kretprobe selftest-hook, differential, failure-mode, and shared-request handoff evidence reviewable without claiming loadable-module parity. The adjacent shared runtime-loader facade, contract, and allocator/init-flow replay still remain review-only underneath the freeze map's study boundary.

`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in review-only study scope for the shared loader packet, so this starter may describe the bounded in-memory sample, the sample-side loader scaffold, the shared loader-request binding, and the shared runtime-loader contract replay, but it must not imply scheduler parity, live runtime registration ownership, or any Architecture Council-approved status change.

## Landed Starter Surface
- module descriptor metadata naming the `samples/kprobes/kretprobe_example.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- bounded return-probe bookkeeping for skipped kernel threads, duration tracking, missed instances, and explicit selftest summaries
- direct failed-exit replay coverage that keeps outstanding-probe state explicit until the active probe drains instead of pretending exit is already safe
- direct maxactive-overflow replay coverage that keeps pressure-induced missed-instance state explicit until the active probe drains
- a narrow differential gate under `zigux/tests/runtime_kretprobe_diff.zig` for bounded maxactive, missed-instance, overlapping-entry, and duration expectations drawn from `samples/kprobes/kretprobe_example.c`
- a landed sample-side loader scaffold under `samples/zigux/runtime_kretprobe_loader.zig` plus a shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig`
- an initialized-stage shared-request snapshot replay that freezes the prepared handoff before later sample selftest activity and keeps that same snapshot explicit through both `waiting_on_runtime_substrate` and `released_without_substrate` review paths
- a selftest-complete shared-request snapshot replay that stays explicit even if later sample exit activity runs before the shared runtime-loader handoff
- prepared selftest-hook drift rejection and prepared shared-plan drift rejection that keep the loader packet truthful about the currently shipped review surface
- dedicated Phase 9 tests, including direct `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, and `phase9-runtime-kretprobe-loader-tests` legs, plus the shared `phase9-runtime-loader-shared-tests` shard and the workflow-backed `make -C zigux phase9` route

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
- this shared build includes the direct `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, and `phase9-runtime-kretprobe-loader-tests` legs alongside the kretprobe survey gate and the shared runtime-loader facade, contract, and allocator/init-flow checks
2. run the convenience target
- `make -C zigux phase9`

## Next Bounded Step

Stay in the Phase 9 runtime kretprobe lane and keep future work narrowly aimed at the remaining shared runtime substrate handoff or runtime lifecycle parity blocker, rather than reopening already-landed starter, differential, loader-request, or prepared-snapshot scaffolds.

## Footer
