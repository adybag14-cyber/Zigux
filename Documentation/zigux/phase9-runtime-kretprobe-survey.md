# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- scope: survey manifest, dedicated survey and diff gates, the bounded loader-handoff scaffold, the landed shared loader-request binding, shared Phase 9 build wiring, and the lane-level note that now records the remaining broader runtime-control blocker
- product boundary:
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`

## Why this slice exists

The roadmap names `samples/kprobes/kretprobe_example.c` twice: first as a Phase 5 sample-reference anchor and later as a Phase 9 runtime pilot anchor. This lane stays strictly inside the Phase 9 reading of that roadmap entry.

The survey artifacts stay anchored to the original `P9-L13` survey lane even though later neighboring runs landed the `runtime_kretprobe` starter, dedicated module tests, diff gate, loader-handoff scaffold, and the shared runtime-loader request binding. That keeps the survey history honest while still recording the full live review surface.

The live repo now has a bounded `runtime_kretprobe` starter, dedicated module tests, a dedicated diff gate, a bounded loader-handoff scaffold, a shared loader-request binding under `zigux/kernel/runtime_loader.zig`, and shared Phase 9 build coverage, so this survey note should reflect the landed pilot review surface instead of still reading like the lane is waiting on missing substrate scaffolding that already exists.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the Linux sample is module-oriented, centered on `register_kretprobe`, `unregister_kretprobe`, `entry_handler`, `ret_handler`, `maxactive`, and `nmissed`.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, a shared loader-request binding in `zigux/kernel/runtime_loader.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- broader shared runtime-loader controls are still missing, so the starter intentionally stops at bounded lifecycle, bookkeeping, loader-handoff behavior, and a machine-checkable shared request shape rather than claiming real module registration parity.

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-kretprobe-survey-gate`
- the landed `runtime-kretprobe-sample-module`
- the landed `runtime-kretprobe-module-tests`
- the landed `runtime-kretprobe-diff-gate`
- the landed `runtime-kretprobe-loader-scaffold`
- the landed `runtime-kretprobe-live-loader-binding`
- the still-blocked `runtime-kretprobe-shared-loader-controls`

This keeps the lane concrete without pretending that Zigux already has real `register_kretprobe()` substrate support or the broader shared runtime-loader controls needed for execution.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a side-by-side Phase 5 `samples/zigux/kretprobe_example.zig` reference port
- architecture-specific `pt_regs` handling or real return-value extraction parity
- loadable-module init and exit parity for kretprobes inside Zigux

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until the shared runtime-loader control surface grows a real owner for command-name, argv-policy, or environment-derived activation handling.
