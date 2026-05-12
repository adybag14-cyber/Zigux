# Phase 9 Runtime Trace-Events Survey

This note keeps an owner-facing review surface for the Phase 9 runtime trace-events packet aligned with live `master`.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This packet is still review-first rather than loadable-runtime-complete. The goal of the current note is to describe exactly what current `master` still proves without implying that the runtime substrate blocker is already cleared.

## Current review surface

Current `master` now keeps the family-local trace-events packet visible again:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_manifest.json`

Current `master` also still keeps the paired review-note and shared-owner surfaces visible:

- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `zigux/tests/phase9_build.zig`

That means the honest current packet is a reviewable family-local starter plus the adjacent shared loader-facing reminder packet. The trace-events sample, loader scaffold, direct module and diff tests, dedicated survey gate, manifest-backed ownership packet, and paired notes are all visible on current `master`. The loader scaffold now also keeps prepared snapshots stable across later selftest or exit activity, rejects shared-request drift around allocator/init-flow and selftest-hook evidence before local handoff, and keeps registration-snapshot and outstanding-registration-drain proofs explicit; what remains blocked is the broader runtime-substrate step that would eventually turn that review packet into live runtime tracepoint-registration parity.

The directly coupled module-slice note already keeps `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and `zigux/Makefile` explicit as adjacent reminder surfaces. Inside this pilot packet, that means the trace-events family owns only the focused `phase9-runtime-trace-events-tests` step in `zigux/tests/phase9_build.zig`; the broader sequencing note and the shared runtime-loader routes stay outside the trace-events-owned boundary.

## Bounded truthfulness rules

Keep this trace-events packet honest in the same way as the shared Phase 9 owner map.

1. Treat the trace-events family as a bounded pilot review packet, not as proof that live tracepoint registration parity or loadable module wiring is complete.
2. Keep the shared loader-facing packet separate from family-local trace-events wording. If the broader loader facade, contract, allocator/init-flow replay, or build-only checker drift, record that in the shared Phase 9 lane instead of pretending the trace-events packet covers it alone.
3. Do not invent a dedicated `validate-phase9.py` route, a separate trace-events-only validator, or a cleared runtime-substrate handoff on current `master`.
4. Keep the older non-owner boundaries explicit: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Active blocker posture

The immediate same-family blocker on current `master` is no longer a missing trace-events packet. The family-local sample, loader, direct module and diff tests, dedicated survey gate, manifest, and paired review notes are visible again.

The remaining blocker is the broader Phase 9 runtime substrate. Until that shared substrate lands, the trace-events packet should stay described as reviewable evidence rather than as completed live runtime tracepoint registration lifecycle parity.

That still-blocked boundary includes runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior. The family-local packet should keep those surfaces explicit as blocked instead of letting them fade into generic runtime-substrate wording.

## Recommended next step

The next same-family follow-through should stay small and literal: keep the trace-events survey note, module-slice note, and manifest aligned with the visible family-local packet while leaving the shared runtime-substrate blocker explicit and the blocked runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior spelled out until the separate shared runtime-substrate lanes actually move.
