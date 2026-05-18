# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries a reviewable family-local trace-events packet plus the adjacent shared loader-facing reminder packet, while the broader runtime substrate remains blocked.

## Roadmap anchor

Phase 9 is still the runtime pilot tranche.

- primary Linux anchors:
  - `lib/atomic64_test.c`
  - `lib/test_bitmap.c`
  - `samples/trace_events/trace-events-sample.c`
  - `samples/kprobes/kretprobe_example.c`
- required Zigux features:
  - first loadable Zigux runtime modules
  - selftest hooks
  - runtime module lifecycle parity
- recommended Zigux destinations:
  - `zigux/tests/runtime_*`
  - `samples/zigux/runtime_*`

## Live repo reality on current master

Current `master` keeps a reviewable Phase 9 trace-events packet that is wider than the stale "removed shared loader family" reminder wording:

- shared reminder surfaces:
  - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`
  - `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
- family-local trace-events packet:
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
- adjacent shared-owner surfaces:
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/Makefile`

The honest current packet is therefore a reviewable family-local starter plus the adjacent shared loader-facing reminder packet, not an absent-loader story.

What remains blocked is the live runtime substrate. That blocked boundary still includes runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior. It also still includes `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and `depmod` script, manifest, or alias publication state.

## Current shared-owner state

- `Documentation/zigux/phase9-runtime-trace-events-survey.md` is the packet-local source of truth for the returned trace-events review packet.
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md` stays focused on the bounded module-facing proof, but it should keep saying plainly that the shared Phase 9 loader-facing packet is also shipped and reviewable.
- `zigux/tests/runtime_trace_events_manifest.json` and `zigux/tests/runtime_trace_events_survey.zig` keep the returned packet and the still-blocked boundary machine-checkable.
- `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, and `zigux/Makefile` remain adjacent shared-owner surfaces rather than proof that the broader runtime substrate has landed.

## Governance rule for this lane

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when current repo reality changes
- tighten one stale reminder surface or checker at a time when it drifts back to missing-file wording
- keep the returned trace-events packet explicit through `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `zigux/tests/runtime_trace_events_survey.zig`, `zigux/tests/runtime_trace_events_manifest.json`, `zigux/tests/phase9_build.zig`, and `zigux/kernel/runtime_loader.zig`
- keep the blocked boundary explicit through runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior

This lane should not reopen new runtime behavior just because reminder notes move.

## Recommended next-step order

1. Re-read `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, `zigux/tests/runtime_trace_events_survey.zig`, `zigux/tests/phase9_build.zig`, and `zigux/kernel/runtime_loader.zig` before changing this shared reminder surface again.
2. If one of those surfaces drifts, trim only the smallest one-file reminder or checker surface that falls back to absent-loader wording or drops the blocked runtime-substrate boundary.
3. Leave broader follow-through to the separate shared runtime-substrate lanes until a real substrate step lands.
