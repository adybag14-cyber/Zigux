# Phase 9 Runtime Trace-Events Module Slice

This document tracks the first bounded Phase 9 runtime trace-events starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=parked`
- `PHASE9_SLICE=runtime-trace-events-module-starter`
- `PHASE9_LANE_KEY=P9-L12`
- `PHASE9_SURVEYED_COMMIT=d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`
- scope: lifecycle starter, bounded event-emission and registration behavior, a machine-checkable diagnostics summary with explicit main-thread and function-thread event totals plus explicit replay run counters, direct sample-local selftest, failed-exit rollback proof, exit proof, a tiny payload-oriented diff gate, a blocked loader scaffold, dedicated Phase 9 test wiring, and lane-local survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`
  - `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had atomic64 and bitmap starters under the same Phase 9 review path, but it still had no trace-events pilot at all. This slice lands the smallest honest trace-events follow-on step: a sample-backed lifecycle scaffold that models bounded event families and callback registration without claiming kernel thread, tracepoint macro, or loadable-module parity.

This bounded starter also stays underneath the trace-core freeze-map boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/trace/ring_buffer.c` in `Study / Boundary Only`, so this slice must not imply ring-buffer parity, deep trace transport ownership, or any Architecture Council-approved status change for the frozen trace core.

The same governance packet also treats `Documentation/zigux/review-checklist.md` as the review-side owner for the trace-core freeze-boundary prompt, so the `Study / Boundary Only` posture stays explicit during review beside the module-slice note, the manifest-backed survey packet, and the freeze map instead of living in only one document.

No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 lane. This module slice now records a parked study boundary and does not reopen the trace-core freeze posture.

## Landed starter surface

- module descriptor metadata naming the `samples/trace_events/trace-events-sample.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- bounded main-thread and function-thread event emission counters for the sample's primary tracepoint families
- explicit registration-balance checks for the function-callback path
- a stable `RuntimeTraceEventsSummary` view exposing lifecycle stage, registration depth, iteration counts, explicit main-thread and function-thread event totals, explicit `foo_bar_reg` and `foo_bar_unreg` registration labels, `init_runs`, `selftest_runs`, and `exit_runs`, payload-presence flags, and the latest bounded main-thread and function-thread payload literals without requiring direct field-by-field payload inspection
- concrete main-thread payload literals for the current bounded `foo_bar`, template, conditional, template-print, and relative-location replay path, including the exported `iter=%d` format template
- the same main-thread replay now also keeps the Linux sample's `count % 5` array-shape replay explicit by recording the bounded vararg array length and its zero terminator alongside the selected random string
- the direct replay path now keeps the conditional branches count-gated by sample counts, so `emitMainIteration(7)` still leaves both conditional messages absent while the count-zero selftest path records both conditional families and the later mixed replay keeps the combined `10` main-thread, `4` function-thread, and `14` total-event summary counts explicit after direct pilot activity
- concrete function-callback payload labels for the current bounded replay path
- a paired header-side macro boundary note that keeps `samples/trace_events/trace-events-sample.h` visible as a 640-line surveyed boundary and survey-only macro surface rather than a generated tracepoint macro parity claim
- a helper-local sample proof that `selftest_complete` still permits bounded replay while preserving registration balance, per-thread event totals, and payload-summary visibility until `exit()`
- the direct sample-local continuity proof now also goes one replay round further after the shipped selftest path, raising the explicit summary to `14` main-thread, `6` function-thread, and `20` total events before `exit()`, and then preserving that stronger post-selftest summary through successful teardown once registration is unwound
- helper-local and module-gate failed-exit rollback proofs showing that `error.OutstandingRegistration` preserves the current replay summary both before selftest completion and after the shipped selftest path: the initialized-stage path keeps the current counters and payload summary intact until the registration is unwound, and the selftest-ready path preserves the explicit `10` main-thread, `4` function-thread, and `14` total-event summary plus the latest payload literals until unregister and exit complete normally
- dedicated Phase 9 module and diff tests that assert those lifecycle, registration, diagnostics-summary, explicit per-thread event-total, replay run-counter, and payload-literal expectations through the shared `zigux/tests/phase9_build.zig` gate, with the diff gate now cross-checking the stable replay summary against the concrete main-thread and function-thread payload labels plus the selftest-path `init_runs`, `selftest_runs`, and `exit_runs` counters instead of treating raw payload structs as the only machine-checkable source
- dedicated Phase 9 module, sample, diff, and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate, including `phase9-runtime-trace-events-sample-tests` for the direct selftest and failed-exit rollback proof
- the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold now exists as a blocked pre-execution handoff that keeps review-only register/unregister labels, explicit module entry and exit labels, an optional review-only command-name override with empty-name rejection, and the release-without-substrate fallback visible without claiming a shared runtime-loader binding, runtime activation control, or a trace-events loader target in the shared build packet

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux trace-events module
- treating the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold as a shared runtime-loader binding or executable substrate handoff before the blocked scheduler-facing runtime substrate exists
- generated tracepoint macro parity for `samples/trace_events/trace-events-sample.h`
- runtime task ownership or event-loop substrate parity
- polling-backed wake or dispatch behavior
- real kernel thread scheduling or timeout behavior
- parity or ownership for `kernel/trace/ring_buffer.c`
- any freeze-map status change for the trace core without an Architecture Council decision
- payload-by-payload differential parity for the full Linux sample

## Gates

1. run the focused trace-events survey replay
- `zig test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig`
- `make -C zigux phase9-trace-events-survey`
- this focused replay keeps the dedicated trace-events survey packet reviewable with the shipped sample import, and the make target wraps that same focused survey gate without implying a loader path while the trace-core freeze boundary stays study-only

2. run the shared Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- this shared build includes `phase9-runtime-trace-events-sample-tests`, `phase9-runtime-trace-events-module-tests`, `phase9-runtime-trace-events-diff-tests`, and `phase9-runtime-trace-events-survey-tests` while still carrying no trace-events loader target

3. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Keep the shipped Phase 9 runtime trace-events starter parked. Reopen this lane only for a later small runtime-substrate handoff around module entry, shared runtime-loader binding, runtime task ownership, polling and event-loop substrate, thread creation, or tracepoint-registration lifecycle wiring, while keeping the separate `kernel/trace/ring_buffer.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it.
