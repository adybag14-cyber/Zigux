# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- `PHASE9_SURVEYED_COMMIT=248bfeaa7f2beddc283c3e398fc36fec3c841242`
- lane: `P9-L17`
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

## Landed starter surface

- a bounded `runtime_kretprobe_loader` scaffold that keeps the planned `register_kretprobe()` and `unregister_kretprobe()` labels, entry or exit symbol naming, private-data size, idle registration snapshot, and failed-exit state retention explicit while the real runtime substrate is still unavailable.

## Roadmap gap vs current pilot

- the Phase 9 roadmap asks this family to grow into one of the first loadable Zigux runtime modules rather than stopping at sample-local evidence.
- the landed starter therefore remains `starter_landed_without_loadable_runtime_substrate`.
- the missing capability is a shared runtime substrate that can turn the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan into a real loadable module path.
- the blocked deliverable is loadable Phase 9 runtime kretprobe pilot module parity.

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux kretprobe module
- real `register_kretprobe()` or `unregister_kretprobe()` parity
- architecture-specific register extraction parity for `regs_return_value()`
