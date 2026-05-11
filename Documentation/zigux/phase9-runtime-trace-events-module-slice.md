# Phase 9 Runtime Trace-Events Module Slice

This note keeps the owner-facing module-slice surface aligned with the live Phase 9 runtime trace-events packet.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This module-slice note stays review-first. It records what the live repository already proves, what still remains blocked, and which file family owns the next bounded follow-through.

## Current master evidence

Current `master` still exposes the shared Phase 9 loader-facing review packet:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

The shared allocator/init-flow replay still names this module-slice note as part of the trace-events delivery-evidence catalog, which makes the note an active reviewability surface rather than optional prose.

Current `master` also keeps the family-local trace-events packet visible beside that shared loader evidence:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_manifest.json`

This note therefore does not claim that the trace-events pilot family is loadable-runtime complete on current `master`. It records that the family-local packet is shipped and reviewable while the live runtime-substrate handoff remains blocked.

## What this slice owns

This module-slice note owns the narrow trace-events family statement that sits between the broad survey note and the shared loader packet.

1. Keep the Phase 9 trace-events family tied to `samples/trace_events/trace-events-sample.c` and the runtime-pilot roadmap only.
2. Keep the shared loader packet separate from family-local implementation claims. The shared loader files prove reviewable handoff behavior, not completed tracepoint-registration parity.
3. Keep the current blocker explicit: the live runtime substrate is still missing even though the family-local trace-events sample, loader, module, diff, survey gate, and manifest surfaces are now present on current `master`.
4. Do not invent `validate-phase9.py`, a trace-events-only validator, or a cleared runtime-substrate handoff.
5. Keep earlier-phase references in their own lanes: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Review posture

The honest current review posture is:

- the shared Phase 9 loader-facing packet is shipped and reviewable
- the trace-events family-local packet is also shipped and reviewable
- the packet still remains review-first because the live runtime-substrate handoff is not complete
- the remaining same-lane work should narrow one survey, manifest, module-slice, or nearby reminder drift at a time instead of widening into unrelated runtime-pilot churn

## Next bounded step

The next honest follow-through in the same `runtime-pilot` lane is to keep this shipped trace-events packet truthful one file at a time, starting with the next survey, manifest, module-slice, or adjacent reminder surface that drifts away from the live sample, loader, module, diff, and survey packet already on current `master`.
