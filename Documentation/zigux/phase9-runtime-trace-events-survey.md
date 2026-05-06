# Phase 9 Runtime Trace-Events Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/trace_events/trace-events-sample.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-trace-events-survey`
- `PHASE9_SURVEYED_COMMIT=e59df689d080aa11773adda87f00c2d650caade8`
- scope: survey manifest, starter sample, dedicated module and survey gates, the bounded loader-handoff scaffold plus shared-request bridge and initialized-stage snapshot stability proof, the shared runtime-loader facade, allocator/init-flow contract replay, shared Phase 9 build wiring, and the lane-level review note that now tracks the landed starter plus the remaining shared runtime-substrate blocker
- product boundary:
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally had no matching trace-events survey artifact, no dedicated `runtime_*` review gate, and no Zigux starter under `samples/zigux/`. That survey note now stays in place as the lane history and review anchor after the bounded starter sample, module tests, diff gate, sample-side loader scaffold, and shared-request bridge landed, so Phase 9 can keep recording what is shipped versus what still depends on the shared runtime substrate.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` at 153 lines.
- `samples/trace_events/trace-events-sample.h` is present on `master` at 640 lines.
- the Linux ftrace selftests already reference `trace-events-sample` as a modprobe and event-enabling target in at least two places.
- the repo had zero `zigux/tests/runtime_trace_events*` files before this survey landed.
- the repo now carries `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, the survey manifest and gate, and shared `zigux/tests/phase9_build.zig` coverage for the trace-events starter lane.
- the current bounded starter now exports a stable `RuntimeTraceEventsSummary`, and the focused diff gate uses that summary to keep the concrete main-thread payload literals, function-callback payload labels, and selftest totals machine-checkable without reaching back into raw payload-only state.
- the current bounded starter still advertises `requires_runtime_substrate=true` and `provides_selftest_hook=true`, so the roadmap's selftest-hook requirement stays explicit in the sample descriptor while the pilot remains an in-memory starter.
- the current loader scaffold now records explicit tracepoint register and unregister API names, the prepared handoff-stage summary, and prepared and initialized-stage snapshots that stay stable even if later sample replay or selftest activity mutates local counters before runtime handoff.
- the live repo now also carries `zigux/kernel/runtime_loader.zig` as the shared request surface for the bounded Phase 9 loader-handoff packet, and the trace-events starter consumes that shared request lifecycle through `prepareSharedRequest`, `requestSharedRuntimeLoad`, `releaseSharedWithoutSubstrate`, and a focused shared-plan drift check before any live registration claim, including an initialized-stage request snapshot that remains explicit if the sample runs its selftest after prepare.
- the live repo also carries `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and the focused `phase9-runtime-loader-shared-tests` build step, so allocator handoff, init-flow counts, release-without-substrate behavior, and shared-request drift all stay reviewable beside the trace-events starter packet instead of hiding in the shared build alone.
- the trace-events starter still stops before a real module-loading substrate or live tracepoint registration lifecycle, so the shipped handoff remains reviewable as pre-execution request shaping, metadata-only registration labels, and release-without-substrate behavior rather than executable runtime registration parity.
- the manifest-backed ownership packet now records a four-entry `delivery_evidence_catalog` and a six-surface `ownership_map`, tying the survey note, module-slice note, dedicated survey gate, shared `phase9_build` bundle, starter sample, and loader scaffold to lane `P9-L12` while leaving shared runtime-substrate work outside this packet.

## Recorded gaps

The manifest started as a survey-only inventory and now records:

- the landed `phase9-build-gate`
- the landed `runtime-trace-events-survey-gate`
- the landed `runtime-trace-events-sample-module` starter
- the landed `runtime-trace-events-selftest-hook`
- the landed `runtime-trace-events-module-tests`
- the landed `runtime-trace-events-diff-gate`
- the landed `runtime-trace-events-loader-scaffold`
- the still-blocked shared runtime substrate handoff

This keeps the survey useful after the first starter slice lands without pretending that Zigux already has a loadable trace-events runtime module or the shared runtime loader needed to bind it live.

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 survey and starter gates
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux trace-events runtime module
- runtime trace registration or unregister parity with the Linux sample
- generated tracepoint macro parity for `trace-events-sample.h`
- full ftrace selftest execution inside Zigux

## Next bounded step

Stay in the Phase 9 runtime trace-events lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded tracepoint-registration handoff plan.
