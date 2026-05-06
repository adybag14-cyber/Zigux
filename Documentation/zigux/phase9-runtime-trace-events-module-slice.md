# Phase 9 Runtime Trace-Events Module Slice

This document tracks the first bounded Phase 9 runtime trace-events starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-trace-events-module-starter`
- `PHASE9_SURVEYED_COMMIT=e59df689d080aa11773adda87f00c2d650caade8`
- scope: lifecycle starter, bounded event-emission and registration behavior, a tiny payload-oriented diff gate, a loader-handoff scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, dedicated Phase 9 test wiring, and lane-local survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had atomic64 and bitmap starters under the same Phase 9 review path, but it still had no trace-events pilot at all. This slice lands the smallest honest trace-events follow-on step: a sample-backed lifecycle scaffold that models bounded event families and callback registration without claiming kernel thread, tracepoint macro, or loadable-module parity.

## Landed starter surface

- module descriptor metadata naming the `samples/trace_events/trace-events-sample.c` anchor and keeping the roadmap-required selftest hook explicit through `provides_selftest_hook=true`
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- bounded main-thread and function-thread event emission counters for the sample's primary tracepoint families
- explicit registration-balance checks for the function-callback path
- concrete main-thread payload literals for the current bounded `foo_bar`, template, conditional, template-print, and relative-location replay path, including the exported `iter=%d` format template
- concrete function-callback payload labels for the current bounded replay path
- a bounded `runtime_trace_events_loader` scaffold that names the planned entry and exit hooks, the tracepoint register and unregister handoff, the current event-family summary, the prepared snapshot that stays stable even if the sample mutates again before runtime handoff, and the no-substrate release path while the shared runtime-loader surface remains unavailable
- dedicated Phase 9 sample, module, and diff tests that assert the sample-local lifecycle, registration, and payload-literal expectations through the shared `zigux/tests/phase9_build.zig` gate
- dedicated Phase 9 loader, survey, and manifest coverage plus the focused `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig` shard for the shared runtime-loader facade, contract, and allocator/init-flow packet wired into the shared `zigux/tests/phase9_build.zig` gate and `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux trace-events module
- `CREATE_TRACE_POINTS` or tracepoint macro parity
- real kernel thread scheduling or timeout behavior
- payload-by-payload differential parity for the full Linux sample

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime trace-events lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded loader-handoff plan for module entry, registration, and release.
