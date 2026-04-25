# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 9 build wiring, and the lane-level note that records the still-missing runtime starter and module coverage
- product boundary:
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`

## Why this slice exists

The roadmap names `samples/kprobes/kretprobe_example.c` twice: first as a Phase 5 sample-reference anchor and later as a Phase 9 runtime pilot anchor. This lane stays strictly inside the Phase 9 reading of that roadmap entry.

The live repo already had runtime pilot slices for `atomic64`, `bitmap`, and `trace-events`, but it still had no matching `runtime_kretprobe_*` survey artifact, no dedicated build hook, and no lane-local note explaining the gap between the Linux sample and any future Zigux starter.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 106 lines.
- the Linux sample is module-oriented, centered on `register_kretprobe`, `unregister_kretprobe`, `entry_handler`, `ret_handler`, `maxactive`, and `nmissed`.
- the live repo currently has zero preexisting `zigux/tests/runtime_kretprobe*` files and no `samples/zigux/runtime_kretprobe.zig` starter.
- `zigux/tests/phase9_build.zig` already existed as the shared runtime review gate, so widening that build is the smallest honest place to surface this missing lane.

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-kretprobe-survey-gate`
- the next `runtime-kretprobe-sample-module`
- the next `runtime-kretprobe-module-tests`
- the next `runtime-kretprobe-diff-gate`
- the still-blocked runtime substrate handoff

This keeps the lane concrete without pretending that Zigux already has a bounded kretprobe starter or real kernel registration substrate.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a side-by-side Phase 5 `samples/zigux/kretprobe_example.zig` reference port
- a Phase 9 `samples/zigux/runtime_kretprobe.zig` starter
- `pt_regs` handling or real return-value extraction parity
- loadable-module init and exit parity for kretprobes inside Zigux

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and add `samples/zigux/runtime_kretprobe.zig` plus `zigux/tests/runtime_kretprobe_module.zig` so the repo can review descriptor metadata, registration lifecycle, elapsed-time bookkeeping, and missed-instance counters before attempting any runtime substrate handoff.
