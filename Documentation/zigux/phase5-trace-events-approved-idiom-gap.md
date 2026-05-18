# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:

- `samples/zigux/trace_events_string_formatting_sample.zig`

Fresh public-tree reread on 2026-05-18 also reconfirmed that current `master` exposes the broader non-runtime trace-events sample packet through:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.

Keep the approved formatting idiom bounded to the current landed reminder packet:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/trace_events_sample.zig`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split: the full non-runtime trace-events sample packet is again readable through the public tree, the bounded formatting companion remains directly readable through the authenticated sample-root route, and the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof.

## Review boundary

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample.

Use this note only to restate the bounded formatting cue that Phase 5 reviewers should preserve.

Do not treat this note as proof of:

- standalone formatting-helper delivery
- standalone `printf` parity
- standalone `vsprintf` parity
- standalone string-helper delivery
- a fifth approved Phase 5 sample

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still treats the returned non-runtime sample packet as absent, loses the selected-string plus `iter=%d` cue, or stops framing `zigux/tests/phase5_build.zig` as public-tree-backed companion evidence while authenticated contents reread still misses that path.