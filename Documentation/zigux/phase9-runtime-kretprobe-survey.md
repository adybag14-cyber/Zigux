# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 9 build wiring, and the lane-level note that now records the landed runtime starter plus the remaining diff-gate and substrate blocker
- product boundary:
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`

## Why this slice exists

The roadmap names `samples/kprobes/kretprobe_example.c` twice: first as a Phase 5 sample-reference anchor and later as a Phase 9 runtime pilot anchor. This lane stays strictly inside the Phase 9 reading of that roadmap entry.

The live repo now has a bounded `runtime_kretprobe` starter, dedicated module tests, and shared Phase 9 build coverage, so this survey note should reflect the landed starter instead of still reading like the lane is sample-free.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the Linux sample is module-oriented, centered on `register_kretprobe`, `unregister_kretprobe`, `entry_handler`, `ret_handler`, `maxactive`, and `nmissed`.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- runtime substrate work is still missing, so the starter intentionally stops at bounded lifecycle and bookkeeping behavior rather than claiming real module registration parity.

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-kretprobe-survey-gate`
- the landed `runtime-kretprobe-sample-module`
- the landed `runtime-kretprobe-module-tests`
- the next `runtime-kretprobe-diff-gate`
- the still-blocked runtime substrate handoff

This keeps the lane concrete without pretending that Zigux already has real `register_kretprobe()` substrate support.

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
- a C-vs-Zig differential gate for specific kretprobe example timelines

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and add `zigux/tests/runtime_kretprobe_diff.zig` so the repo can review entry-handler skip, elapsed-time bookkeeping, and missed-instance counters against a few Linux-sample expectations before attempting any runtime substrate handoff.