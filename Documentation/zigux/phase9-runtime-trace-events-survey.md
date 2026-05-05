# Phase 9 Runtime Trace-Events Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/trace_events/trace-events-sample.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-trace-events-survey`
- scope: survey manifest, starter sample, dedicated module and survey gates, the bounded loader-handoff scaffold, shared Phase 9 build wiring for the starter lane, and the lane-level review note that now tracks the landed starter plus the remaining shared runtime-substrate blocker
- product boundary:
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally had no matching trace-events survey artifact, no dedicated `runtime_*` review gate, and no Zigux starter under `samples/zigux/`. That survey note now stays in place as the lane history and review anchor after the bounded starter sample, module tests, diff gate, and sample-side loader scaffold landed, so Phase 9 can keep recording what is shipped versus what still depends on the shared runtime substrate.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` at 153 lines.
- `samples/trace_events/trace-events-sample.h` is present on `master` at 640 lines.
- the Linux ftrace selftests already reference `trace-events-sample` as a modprobe and event-enabling target in at least two places.
- the repo had zero `zigux/tests/runtime_trace_events*` files before this survey landed.
- the repo now carries `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, the survey manifest and gate, and shared `zigux/tests/phase9_build.zig` coverage for the trace-events starter lane.
- the current bounded starter now records concrete main-thread payload literals for `foo_bar`, template, conditional, template-print, and relative-location replay paths, plus explicit function-callback payload labels and the exported `iter=%d` format template.
- the current loader scaffold now records explicit tracepoint register and unregister API names, the prepared handoff-stage summary, and the no-substrate release path without claiming a real shared runtime loader already exists.

## Recorded gaps

The manifest started as a survey-only inventory and now records:

- the landed `phase9-build-gate`
- the landed `runtime-trace-events-survey-gate`
- the landed `runtime-trace-events-sample-module` starter
- the landed `runtime-trace-events-module-tests`
- the landed `runtime-trace-events-diff-gate`
- the landed `runtime-trace-events-loader-scaffold`
- the still-blocked shared runtime substrate handoff

This keeps the survey useful after the first starter slice lands without pretending that Zigux already has a loadable trace-events runtime module or the shared runtime loader needed to bind it live.

## Gates

1. run the dedicated Phase 9 survey and starter gates
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux trace-events runtime module
- runtime trace registration or unregister parity with the Linux sample
- generated tracepoint macro parity for `trace-events-sample.h`
- full ftrace selftest execution inside Zigux

## Next bounded step

Stay in the Phase 9 runtime trace-events lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded tracepoint-registration handoff plan.
