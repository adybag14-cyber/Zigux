# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- `PHASE9_SURVEYED_COMMIT=248bfeaa7f2beddc283c3e398fc36fec3c841242`
- scope: lifecycle starter, bounded return-probe bookkeeping, a tiny differential gate, a loader-handoff scaffold, the shared runtime-loader facade and allocator/init-flow contract replay, dedicated Phase 9 test wiring, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had runtime pilot starters for atomic64, bitmap, and trace-events, but it still had no kretprobe lane foothold. This slice lands the smallest honest kretprobe follow-on step: a sample-backed lifecycle scaffold that models entry timestamps, return values, duration, missed-instance bookkeeping, and now the loader handoff plan without claiming `register_kretprobe()` or loadable-module parity.

This runtime kretprobe starter also stays outside the landed Phase 5 reference-sample packet: `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` remain the separate Phase 9 runtime kretprobe family rooted in `samples/kprobes/kretprobe_example.c`, not a second owner for the already-approved non-runtime `samples/zigux/kretprobe_example.zig` cue under `Documentation/zigux/phase5-kretprobe-sample-survey.md`.
The shared sample-root catalog at `samples/zigux/README.md` keeps the approved Phase 5 anchor explicit through `samples/zigux/kretprobe_example.zig` while listing the runtime kretprobe pair only under the separate Phase 9 runtime pilot family.

## Landed starter surface

- module descriptor metadata naming the `samples/kprobes/kretprobe_example.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a retargetable symbol-name starter that defaults to `kernel_clone`, matching the Linux sample's module parameter
- bounded entry-handler skip behavior for kernel-thread-like contexts, return-value and duration bookkeeping, and explicit `nmissed` tracking
- a dedicated `runtime_kretprobe_diff` gate that replays skip, elapsed-time, and missed-instance expectations from `samples/kprobes/kretprobe_example.c`
- a bounded `runtime_kretprobe_loader` scaffold that keeps the planned `register_kretprobe()` and `unregister_kretprobe()` labels, entry or exit symbol names, and per-instance private-data size explicit as metadata-only pre-execution handoff details while the runtime substrate remains unavailable
- the loader handoff refuses to prepare a shared request while an entry timestamp is armed or a probe instance is still active, requiring an idle registration snapshot before the shared runtime-loader boundary
- the shared `runtime_loader` facade, `runtime_loader_contract`, and `runtime_loader_allocator_init_flow` replay that keep the kernel-heap allocator handoff, init-flow counts, and release-without-substrate path reviewable across the whole shipped Phase 9 loader packet
- dedicated Phase 9 tests and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate and `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux kretprobe module
- real `register_kretprobe()` or `unregister_kretprobe()` parity
- architecture-specific register extraction parity for `regs_return_value()`

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded loader-handoff plan.
