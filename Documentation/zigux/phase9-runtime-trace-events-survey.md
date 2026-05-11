# Phase 9 Runtime Trace-Events Survey

This note keeps an owner-facing review surface for the Phase 9 runtime trace-events packet aligned with live `master`.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This packet is still review-first rather than loadable-runtime-complete. The goal of the current note is to keep the shipped trace-events handoff surfaces explicit without implying that the runtime substrate blocker is cleared.

## Current review surface

Current `master` already keeps the trace-events pilot family wired into the shared Phase 9 build packet through `zigux/tests/phase9_build.zig`.

That shared build route names these trace-events-facing surfaces together:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- the focused `phase9-runtime-trace-events-tests` step in `zigux/tests/phase9_build.zig`

The broader shared loader packet also remains part of the same bounded Phase 9 review surface:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `make -C zigux phase9`

## Bounded truthfulness rules

Keep this trace-events packet honest in the same way as the shared Phase 9 owner map.

1. Treat the trace-events family as a bounded pilot handoff, not as proof that live tracepoint registration parity or loadable module wiring is complete.
2. Keep the shared loader-facing packet separate from family-local trace-events wording. If the loader facade, contract, allocator/init-flow replay, or build-only checker drift, record that in the shared Phase 9 lane instead of pretending the trace-events packet covers it alone.
3. Do not invent a dedicated `validate-phase9.py` route, a separate trace-events-only validator, or a cleared runtime-substrate handoff on current `master`.
4. Keep the older non-owner boundaries explicit: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Active blocker posture

The current blocker is still the runtime substrate itself.

The trace-events packet is reviewable through the shared build, the family-local sample plus loader-facing files named by that build, and the shared allocator/init-flow replay, but it is not yet a claim of full runtime tracepoint registration lifecycle parity on current `master`.

## Recommended next step

The next same-family follow-through should stay small and literal: inspect the paired trace-events module-slice note, the manifest-backed owner map, or the nearby shared reminder packet for the next one-file truthfulness drift before widening into new runtime behavior claims.
