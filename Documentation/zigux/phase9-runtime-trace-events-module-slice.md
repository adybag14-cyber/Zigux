# Phase 9 Runtime Trace-Events Module Slice

This note keeps the owner-facing module-slice surface aligned with the live Phase 9 runtime trace-events packet.

PHASE9_SURVEYED_COMMIT=ccd5361c3b193d26587c6396f029fc335c783c6e

This note keeps the manifest-backed inspected commit explicit so the module-slice review surface stays pinned to `zigux/tests/runtime_trace_events_manifest.json` while the broader runtime substrate remains blocked.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This module-slice note stays review-first. It records what the live repository already proves, what still remains blocked, and which file family owns the next bounded follow-through.

## Current master evidence

Current `master` exposes the family-local trace-events packet through the shared Phase 9 owner-map and build bundle:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_manifest.json`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`

Current `master` also still exposes the adjacent shared loader-facing packet:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

That means the honest current review surface is a landed family-local packet plus the adjacent shared loader-facing reminder surfaces. The family-local trace-events sample, loader scaffold, direct module and diff gates, dedicated survey gate, and paired report surfaces are all visible on current `master`. The loader scaffold now also keeps prepared snapshots stable across later selftest or exit activity, rejects shared-request drift around allocator/init-flow and selftest-hook evidence before local handoff, keeps registration-snapshot and outstanding-registration-drain proofs explicit, rejects non-idle registration state at the metadata-only handoff boundary, and keeps shared release failures from desynchronizing loader state; the family-local module gate owns the selftest-ready failed-exit rollback path that preserves lifecycle state until registration drain finishes, while still leaving the broader runtime-substrate handoff as a separate blocked step. That blocked handoff still stops before `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and any `depmod` script or manifest state; those alias and depmod surfaces remain review-only metadata boundaries rather than shipped trace-events-family evidence.

## What this slice owns

This module-slice note owns the narrow trace-events family statement that sits between the broad survey note and the shared loader packet.

1. Keep the Phase 9 trace-events family tied to `samples/trace_events/trace-events-sample.c` and the runtime-pilot roadmap only.
2. Keep the shared loader packet separate from family-local implementation claims. The shared loader files prove reviewable handoff behavior, not completed tracepoint-registration parity.
3. Keep the real blocker explicit: the family-local packet is reviewable on current `master`, but runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior still depend on the missing live runtime substrate. The same blocked boundary also still includes `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and `depmod` script or manifest state, which remain outside both the family-local trace-events packet and the adjacent shared loader handoff.
4. Do not invent `validate-phase9.py`, a trace-events-only validator, or a cleared runtime-substrate handoff.
5. Keep earlier-phase references in their own lanes: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Review posture

The honest current review posture is:

- the family-local trace-events sample, loader, module, diff, survey, and manifest packet is visible on current `master`
- the family-local module gate already proves that a selftest-ready failed exit preserves the current replay summary until registration drain completes
- the shared Phase 9 loader-facing packet is also shipped and reviewable
- the packet still remains review-first because runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior still depend on the missing live runtime substrate
- the remaining same-lane work should keep the packet-local notes and manifest aligned with the shipped family-local trace-events proof instead of drifting back to missing-file reminder wording

## Next bounded step

The next honest follow-through in the same `runtime-pilot` lane is to keep the packet-local survey note, module-slice note, and manifest aligned with the visible family-local trace-events packet, then leave broader follow-up to the separate shared runtime-substrate lanes until a real substrate step lands.
