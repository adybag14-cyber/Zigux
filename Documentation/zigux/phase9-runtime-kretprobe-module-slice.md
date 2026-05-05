# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- scope: lifecycle starter, bounded return-probe bookkeeping, a tiny differential gate, a loader-handoff scaffold, dedicated Phase 9 test wiring, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had runtime pilot starters for atomic64, bitmap, and trace-events, but it still had no kretprobe lane foothold. This slice lands the smallest honest kretprobe follow-on step: a sample-backed lifecycle scaffold that models entry timestamps, return values, duration, missed-instance bookkeeping, and now the loader handoff plan without claiming `register_kretprobe()` or loadable-module parity.

## Landed starter surface

- module descriptor metadata naming the `samples/kprobes/kretprobe_example.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a retargetable symbol-name starter that defaults to `kernel_clone`, matching the Linux sample's module parameter
- bounded entry-handler skip behavior for kernel-thread-like contexts, return-value and duration bookkeeping, and explicit `nmissed` tracking
- a dedicated `runtime_kretprobe_diff` gate that replays skip, elapsed-time, and missed-instance expectations from `samples/kprobes/kretprobe_example.c`
- a bounded `runtime_kretprobe_loader` scaffold that keeps the planned `register_kretprobe()` and `unregister_kretprobe()` labels, entry or exit symbol names, and per-instance private-data size explicit as metadata-only pre-execution handoff details while the runtime substrate remains unavailable
- dedicated Phase 9 tests and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux kretprobe module
- real `register_kretprobe()` or `unregister_kretprobe()` parity
- architecture-specific register extraction parity for `regs_return_value()`

## Gates

1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded loader-handoff plan.
