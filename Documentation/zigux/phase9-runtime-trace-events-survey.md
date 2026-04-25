# Phase 9 Runtime Trace-Events Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/trace_events/trace-events-sample.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-trace-events-survey`
- scope: survey manifest, dedicated runtime survey gate, Phase 9 build wiring, and the lane-level review note that keeps the trace-events starter gap explicit without fabricating a runtime module
- product boundary:
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had Phase 9 starter slices for atomic64 and bitmap, but it still had no matching trace-events survey artifact, no dedicated `runtime_*` review gate, and no lane note for the trace-events family. This survey slice closes that reviewability gap first so the eventual trace-events starter can stay bounded around the real sample and selftest expectations instead of widening into generic tracing work.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` at 153 lines.
- `samples/trace_events/trace-events-sample.h` is present on `master` at 640 lines.
- the Linux ftrace selftests already reference `trace-events-sample` as a modprobe and event-enabling target in at least two places.
- the repo had zero `zigux/tests/runtime_trace_events*` files before this survey landed.
- the repo already had `samples/zigux/` and `zigux/tests/phase9_build.zig` from the atomic64 and bitmap lanes, but no dedicated trace-events Phase 9 note.

## Recorded gaps

The manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-trace-events-survey-gate`
- the next `runtime-trace-events-sample-module`
- the next `runtime-trace-events-module-tests`
- the next `runtime-trace-events-event-catalog`
- the still-blocked runtime substrate handoff

This keeps the trace-events lane reviewable now without pretending that Zigux already ships a loadable trace-events module.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a loadable Zigux trace-events module implementation
- runtime trace registration or unregister parity
- generated tracepoint macros or direct macro parity for `trace-events-sample.h`
- full ftrace selftest execution inside Zigux

## Next bounded step

Stay in the Phase 9 runtime trace-events lane and add the first narrow `samples/zigux/runtime_trace_events.zig` starter plus `zigux/tests/runtime_trace_events_module.zig` coverage around descriptor metadata, lifecycle states, and a tiny named event catalog before attempting any runtime substrate work.
