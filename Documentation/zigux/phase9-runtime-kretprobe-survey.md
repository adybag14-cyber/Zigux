# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_SURVEYED_COMMIT=248bfeaa7f2beddc283c3e398fc36fec3c841242`
- lane: `P9-L17`
- scope: survey manifest, starter sample, dedicated module, survey, and diff gates, the bounded loader-handoff scaffold, the shared runtime-loader facade, allocator/init-flow contract replay, and shared-request bridge with landed selftest-hook parity, shared Phase 9 build wiring, and the lane-level note that now records the landed runtime starter plus the remaining substrate blocker
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- the landed loader scaffold keeps `register_kretprobe` and `unregister_kretprobe` explicit as metadata-only labels inside a pre-execution handoff plan.
- the loader handoff now refuses to prepare a shared request while an entry timestamp is still armed or a probe instance is still active, keeping the metadata-only registration snapshot idle before the shared runtime-loader request begins.
- the bounded runtime kretprobe sample and dedicated module tests now also keep failed-exit state explicit: if `exit()` is attempted while an active probe is still armed, the initialized or selftest-complete stage stays intact until the active probe drains instead of silently widening into a partial teardown.
- the shared `zigux/kernel/runtime_loader.zig` facade remains a review-only Phase 9 packet under the freeze map's study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` boundary, so this lane keeps the kretprobe handoff reviewable without claiming scheduler-facing substrate closure or a freeze-map status change.
- runtime substrate work is still missing, so the starter intentionally stops at bounded lifecycle, bookkeeping, metadata-only registration labels, idle registration snapshot checks, failed-exit state retention until the active probe drains, and loader-handoff behavior rather than claiming real module registration parity.

## Roadmap gap vs current pilot

- the Phase 9 roadmap asks for first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.
- the landed kretprobe packet satisfies the bounded selftest-hook and lifecycle-evidence part of that roadmap, but it does not yet satisfy the loadable-module part.
- the honest current state is `starter_landed_without_loadable_runtime_substrate`.
- the missing capability is a shared runtime substrate that can turn the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan into a real loadable module path.
- the blocked deliverable is loadable Phase 9 runtime kretprobe pilot module parity.

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-kretprobe-survey-gate`
- the landed `runtime-kretprobe-sample-module`
- the landed `runtime-kretprobe-module-tests`
- the landed `runtime-kretprobe-diff-gate`
- the landed `runtime-kretprobe-loader-plan`
- the landed `runtime-kretprobe-loader-contract`
- the landed `runtime-kretprobe-loader-init-flow`
- the still-blocked shared runtime substrate handoff

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan.

## Gates

1. run the convenience target
- `make -C zigux phase9`
