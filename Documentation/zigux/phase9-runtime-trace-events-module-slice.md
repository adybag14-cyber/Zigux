# Phase 9 Runtime Trace-Events Module Slice

This document tracks the first bounded Phase 9 runtime trace-events starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-trace-events-module-starter`
- scope: lifecycle starter, bounded event-emission and registration behavior, a machine-checkable diagnostics summary with explicit main-thread and function-thread event totals, direct sample-local selftest, failed-exit rollback proof, and exit proof, a tiny payload-oriented diff gate, dedicated Phase 9 test wiring, and lane-local survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_trace_events.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had atomic64 and bitmap starters under the same Phase 9 review path, but it still had no trace-events pilot at all. This slice lands the smallest honest trace-events follow-on step: a sample-backed lifecycle scaffold that models bounded event families and callback registration without claiming kernel thread, tracepoint macro, or loadable-module parity.

This bounded starter also stays underneath the trace-core freeze-map boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/trace/ring_buffer.c` in `Study / Boundary Only`, so this slice must not imply ring-buffer parity, deep trace transport ownership, or any Architecture Council-approved status change for the frozen trace core.

No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 lane. This module slice only records the active study boundary and does not reopen the trace-core freeze posture.

## Landed starter surface

- module descriptor metadata naming the `samples/trace_events/trace-events-sample.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- bounded main-thread and function-thread event emission counters for the sample's primary tracepoint families
- explicit registration-balance checks for the function-callback path
- a stable `RuntimeTraceEventsSummary` view exposing lifecycle stage, registration depth, iteration counts, explicit main-thread and function-thread event totals, payload-presence flags, and the latest bounded main-thread and function-thread payload literals without requiring direct field-by-field payload inspection
- concrete main-thread payload literals for the current bounded `foo_bar`, template, conditional, template-print, and relative-location replay path, including the exported `iter=%d` format template
- concrete function-callback payload labels for the current bounded replay path
- a helper-local sample proof that `selftest_complete` still permits bounded replay while preserving registration balance, per-thread event totals, and payload-summary visibility until `exit()`
- a helper-local failed-exit rollback proof showing that `error.OutstandingRegistration` leaves the module in the initialized stage with its current counters and payload summary intact until the registration is unwound and the normal selftest-to-exit path resumes
- dedicated Phase 9 module and diff tests that assert those lifecycle, registration, diagnostics-summary, explicit per-thread event-total, and payload-literal expectations through the shared `zigux/tests/phase9_build.zig` gate, with the diff gate now cross-checking the stable replay summary against the concrete main-thread and function-thread payload labels instead of treating raw payload structs as the only machine-checkable source
- dedicated Phase 9 module, sample, diff, and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate, including `phase9-runtime-trace-events-sample-tests` for the direct selftest and failed-exit rollback proof
- no `samples/zigux/runtime_trace_events_loader.zig` handoff exists yet, and the shared `zigux/tests/phase9_build.zig` bundle intentionally carries no trace-events loader target while scheduler-facing runtime substrate work stays blocked

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux trace-events module
- a partial or placeholder `samples/zigux/runtime_trace_events_loader.zig` handoff before the blocked scheduler-facing runtime substrate exists
- `CREATE_TRACE_POINTS` or tracepoint macro parity
- runtime task ownership or event-loop substrate parity
- polling-backed wake or dispatch behavior
- real kernel thread scheduling or timeout behavior
- parity or ownership for `kernel/trace/ring_buffer.c`
- any freeze-map status change for the trace core without an Architecture Council decision
- payload-by-payload differential parity for the full Linux sample

## Gates

1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime trace-events lane and keep broader work blocked until there is a small honest substrate handoff for module entry, runtime task ownership, polling and event-loop substrate, thread creation, and tracepoint-registration lifecycle wiring, while keeping the separate `kernel/trace/ring_buffer.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it.
