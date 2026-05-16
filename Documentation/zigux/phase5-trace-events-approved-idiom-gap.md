# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` actually ships.

## Current approved cue on `master`

The directly reviewable trace-events packet remains:
- `samples/zigux/trace_events_sample.zig`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample.
Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by `samples/zigux/trace_events_sample.zig` together with the existing `formattedMessage()`, `runStringFormattingCycleReplay()`, and exact `checked_focus` packet already surfaced by the paired survey note and survey gate.

## Review boundary

Use this note only to restate that bounded formatting cue inside the landed non-runtime trace-events packet.
Do not treat this note as proof of standalone formatting-helper delivery, standalone `printf` parity, standalone `vsprintf` parity, or a fifth approved Phase 5 sample.
Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows the trace-events sample, survey note, survey gate, or shared reviewer packet drift away from the same selected-string plus `iter=%d` formatting cue.