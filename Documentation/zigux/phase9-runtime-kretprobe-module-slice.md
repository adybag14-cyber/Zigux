# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- `PHASE9_SURVEYED_COMMIT=248bfeaa7f2beddc283c3e398fc36fec3c841242`
- lane: `P9-L17`
- scope: lifecycle starter, bounded return-probe bookkeeping, a tiny differential gate, a loader-handoff scaffold, the shared runtime-loader facade and allocator/init-flow contract replay, dedicated Phase 9 test wiring, and survey-note plus survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already carries the bounded runtime kretprobe starter, but this Phase 9 runtime pair stays separate from the already-approved non-runtime Phase 5 reference-sample packet: `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` remain the separate runtime family rooted in `samples/kprobes/kretprobe_example.c`, not a second owner for the approved non-runtime `samples/zigux/kretprobe_example.zig` cue under `Documentation/zigux/phase5-kretprobe-sample-survey.md`.
The shared sample-root catalog at `samples/zigux/README.md` keeps the approved Phase 5 anchor explicit through `samples/zigux/kretprobe_example.zig` while listing the runtime kretprobe pair only under the separate Phase 9 runtime pilot family.

## Landed starter surface

- a bounded `runtime_kretprobe_loader` scaffold that keeps the planned `register_kretprobe()` and `unregister_kretprobe()` labels, entry or exit symbol naming, private-data size, idle registration snapshot, and failed-exit state retention explicit while the real runtime substrate is still unavailable.
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` now stays inside this slice's shipped product boundary too, so the kretprobe starter keeps the pilot-family owner split explicit instead of leaving the shared loader lane versus pilot-local packet implicit.

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

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the focused runtime kretprobe lane step
- `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig`

3. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

4. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan.
