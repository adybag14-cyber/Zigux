# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

But `samples/zigux/README.md` now says current `master` directly exposes only the separate Phase 9 runtime sample-root files, not a direct non-runtime `samples/zigux/trace_events_sample.zig` sample-root port.

Keep the approved formatting idiom bounded to the shared reminder packet:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`

That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest that the current proof is reminder-surface guidance rather than direct sample-root evidence.

## Review boundary

Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample.

Use this note only to restate the bounded formatting cue that Phase 5 reviewers should preserve.

Do not treat this note as proof of:

- standalone formatting-helper delivery
- standalone `printf` parity
- standalone `vsprintf` parity
- a fifth approved Phase 5 sample
- direct proof that `samples/zigux/trace_events_sample.zig` is currently present on `master`

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows that the shared trace-events reminder packet drifted away from the same selected-string plus `iter=%d` cue or the sample root once again directly exposes the non-runtime trace-events sample port.
