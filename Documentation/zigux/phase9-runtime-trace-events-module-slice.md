# Phase 9 Runtime Trace-Events Module Slice

This note restores the missing owner-facing module-slice surface for the Phase 9 runtime trace-events packet.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This module-slice note stays review-first. It records what the live repository still proves, what it still lacks, and which file family owns the next bounded follow-through.

## Current master evidence

Current `master` still exposes the shared Phase 9 loader-facing review packet:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

The shared allocator/init-flow replay still names this module-slice note as part of the trace-events delivery-evidence catalog, which makes the missing note a real reviewability gap rather than optional prose.

At the same time, direct current-`master` readback still fails for the family-local trace-events surfaces that a fuller packet would normally carry:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_manifest.json`

This note therefore does not claim that the trace-events pilot family is implementation-complete on current `master`. It records that the shared loader packet already exists, while the family-local trace-events slice is still blocked on those missing files.

## What this slice owns

This module-slice note owns the narrow trace-events family statement that sits between the broad survey note and the shared loader packet.

1. Keep the Phase 9 trace-events family tied to `samples/trace_events/trace-events-sample.c` and the runtime-pilot roadmap only.
2. Keep the shared loader packet separate from family-local implementation claims. The shared loader files prove reviewable handoff behavior, not completed tracepoint-registration parity.
3. Keep the current blocker explicit: the family-local trace-events sample, loader, module, diff, survey gate, and manifest surfaces listed above are still absent on current `master`.
4. Do not invent `validate-phase9.py`, a trace-events-only validator, or a cleared runtime-substrate handoff.
5. Keep earlier-phase references in their own lanes: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Review posture

The honest current review posture is:

- the shared Phase 9 loader-facing packet is shipped and reviewable
- the trace-events family-local packet is still partial
- this note exists so the trace-events survey and the shared allocator/init-flow evidence no longer point at a missing owner surface
- the remaining same-lane work should restore missing trace-events family files one bounded surface at a time instead of widening into unrelated runtime-pilot churn

## Next bounded step

The next honest follow-through in the same `runtime-pilot` lane is to restore one missing family-local trace-events evidence surface on current `master`, starting with `zigux/tests/runtime_trace_events_manifest.json` or `zigux/tests/runtime_trace_events_survey.zig`, because those are the smallest concrete packet pieces now missing beside this restored owner note.
