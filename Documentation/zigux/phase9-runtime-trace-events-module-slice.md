# Phase 9 Runtime Trace-Events Module Slice

This note keeps the owner-facing module-slice surface aligned with the returned Phase 9 trace-events packet still visible on current `master`.

PHASE9_SURVEYED_COMMIT=3c6c7d3fc8e721e8c50e84b512876cee6ad4e015

This note keeps the last reviewed packet checkpoint explicit while staying focused on the bounded module-facing proof. The shared Phase 9 loader-facing packet is also shipped and reviewable, but the broader runtime-substrate handoff remains a separate blocked step and the live runtime substrate is still missing.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

## Current master evidence

Current `master` keeps the family-local trace-events module packet reviewable through:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_manifest.json`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/Makefile`

The family-local module gate owns the selftest-ready failed-exit rollback path that preserves lifecycle state until registration drain finishes, while still leaving the broader runtime-substrate handoff as a separate blocked step.
The family-local module gate also keeps rejected re-selftest rollback explicit, so invalid repeat selftest attempts leave both the selftest-complete and exited summaries stable while the broader runtime-substrate handoff stays blocked.
The sample-side loader scaffold keeps prepared shared-request snapshots explicit, rejects non-idle registration state at the metadata-only handoff boundary, and keeps shared release failures from desynchronizing loader state.

## Blocked boundary

The shared Phase 9 loader-facing packet is also shipped and reviewable, but the broader runtime-substrate handoff remains blocked. That blocked boundary still includes runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior. It also still includes `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and any `depmod` script, manifest, or alias publication state.
This reminder keeps saying in lower-case too that the shared Phase 9 loader-facing packet is also shipped and reviewable, so the note cannot silently slip back into missing-file wording.

Because that broader boundary is still blocked, those alias and depmod surfaces remain review-only metadata boundaries rather than shipped trace-events-family evidence.

Do not invent `validate-phase9.py`, a trace-events-only validator, or a cleared runtime-substrate handoff.

## Review posture

- keep the bounded module-facing proof anchored in `samples/zigux/runtime_trace_events.zig` and `zigux/tests/runtime_trace_events_diff.zig`
- keep the returned loader scaffold, loader-substrate-drift replay, survey gate, manifest, shared build bundle, and shared runtime-loader surface explicit as shipped review packet companions
- keep the remaining same-lane work should keep the packet-local notes and manifest aligned with the shipped family-local trace-events proof instead of drifting back to missing-file reminder wording
- keep the blocked runtime-substrate boundary explicit instead of letting scheduler, polling, or event-loop wording fade into vague backlog language

## Next bounded step

The next honest follow-through in the same `runtime-pilot` lane is to keep the packet-local survey note, module-slice note, and manifest aligned with the visible family-local trace-events packet, keep the bounded pilot-module contract explicit, and then leave broader follow-up to the separate shared runtime-substrate lanes until a real substrate step lands.
