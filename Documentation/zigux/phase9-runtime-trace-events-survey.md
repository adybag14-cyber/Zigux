# Phase 9 Runtime Trace-Events Survey

This note keeps an owner-facing review surface for the Phase 9 runtime trace-events packet aligned with live `master`.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This packet is still review-first rather than loadable-runtime-complete. The goal of the current note is to describe exactly what current `master` still proves without implying that the runtime substrate blocker or the family-local trace-events starter packet is already restored.

## Current review surface

Current `master` still keeps the trace-events family visible through a small Phase 9 reminder packet:

- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/phase9_build.zig`

Those surfaces keep the trace-events lane visible inside the broader Phase 9 build and owner-map packet, and the manifest-backed ownership packet is still readable on current `master`, but direct current-`master` readback still fails for the family-local trace-events implementation and test surfaces that a fuller starter packet would need:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`

That means the honest current packet is narrower than older reminder wording suggested. Current `master` still carries the trace-events survey note, module-slice note, sequencing note, manifest-backed ownership packet, and shared Phase 9 build boundary, but it does not currently expose the family-local trace-events starter sample, loader scaffold, dedicated survey gate, or direct module and diff test packet.

## Bounded truthfulness rules

Keep this trace-events packet honest in the same way as the shared Phase 9 owner map.

1. Treat the trace-events family as a bounded pilot review packet, not as proof that live tracepoint registration parity or loadable module wiring is complete.
2. Keep the shared loader-facing packet separate from family-local trace-events wording. If the broader loader facade, contract, allocator/init-flow replay, or build-only checker drift, record that in the shared Phase 9 lane instead of pretending the trace-events packet covers it alone.
3. Do not invent a dedicated `validate-phase9.py` route, a separate trace-events-only validator, or a cleared runtime-substrate handoff on current `master`.
4. Keep the older non-owner boundaries explicit: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Active blocker posture

The immediate same-family blocker on current `master` is the still-partial family-local trace-events packet.

The survey note, module-slice note, sequencing note, manifest-backed ownership packet, and shared `zigux/tests/phase9_build.zig` surface keep the lane reviewable, but the sample, loader, direct module and diff tests, and dedicated survey gate listed above are not currently readable on `master`.

Even after those family-local surfaces are restored, the broader Phase 9 runtime substrate remains a separate blocked step before any honest claim of live runtime tracepoint registration lifecycle parity.

## Recommended next step

The next same-family follow-through should stay small and literal: restore one missing family-local trace-events evidence surface on current `master`, starting with `zigux/tests/runtime_trace_events_survey.zig` or `samples/zigux/runtime_trace_events_loader.zig`, and then rebuild outward from that packet one bounded file at a time without widening into unrelated runtime-pilot churn.
