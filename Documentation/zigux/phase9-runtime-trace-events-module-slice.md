# Phase 9 Runtime Trace-Events Module Slice

## Landed starter surface

- a loader-handoff scaffold
- samples/zigux/runtime_trace_events_loader.zig
- zigux/tests/runtime_trace_events_survey.zig
- zigux/tests/phase9_build.zig
- the focused `phase9-runtime-trace-events-tests` build step
- the separate shared loader lane keeps the shared runtime-loader facade, contract, allocator/init-flow replay, and `phase9-runtime-loader-shared-tests` shard
- keeping the roadmap-required selftest hook explicit through `provides_selftest_hook=true`
- runtime task ownership or event-loop substrate parity remains blocked behind that shared runtime-loader surface
- polling-backed wake or dispatch behavior remains blocked behind the same shared runtime-loader surface
- a manifest-backed ownership packet that now names the survey note, module-slice note, starter sample, loader scaffold, dedicated survey gate, and the focused `phase9-runtime-trace-events-tests` step together

## Roadmap gap vs current pilot

- metadata-only labels `tracepoint_probe_register` and `tracepoint_probe_unregister` remain reviewable through the bounded loader handoff.
- an idle registration snapshot is still required before the loader can prepare a shared request.
- the honest current state is `starter_landed_without_loadable_runtime_substrate`.
- the blocked deliverable is loadable Phase 9 runtime trace-events pilot module parity.
