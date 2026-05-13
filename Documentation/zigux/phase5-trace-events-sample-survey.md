# Phase 5 Trace-Events Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked-readback-gap-aligned`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L16`
- `PHASE5_SURVEYED_COMMIT=readback-gap-confirmed-2026-05-13`
- scope: keep the trace-events survey note truthful against current directly readable repo evidence, the roadmap's approved Phase 5 anchor set, and the freeze-map boundary without widening into runtime work

## Why this note exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" tranche, and `samples/trace_events/trace-events-sample.c` is still one of the four approved Linux anchors that should make Zigux idioms reviewable and repeatable.

The bounded job for this note is now to record the current public-tree gap honestly and keep shared reminder surfaces from overstating a restored packet that direct readback no longer returns.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 still found these trace-events-adjacent surfaces directly readable today:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

That same direct readback did not recover the older restored trace-events packet paths:

- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Treat those paths as the current public-tree gap for this lane until a fresh reread proves they returned.

## What still remains true

Even with that missing readback, the roadmap and ledger still keep the intended Phase 5 ownership clear:

- the approved Linux anchor is still `samples/trace_events/trace-events-sample.c`
- the Phase 5 goal is still reviewable, repeatable sample-backed idioms rather than runtime-substrate closure
- the separate `samples/zigux/runtime_trace_events.zig` and `samples/zigux/runtime_trace_events_loader.zig` family still belongs to the later Phase 9 runtime lane and should not be counted as extra proof for the non-runtime Phase 5 packet
- there is still no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, so shared formatting guidance should stay bounded to the selected-string plus `iter=%d` cue only when the current readback gap is kept explicit too

## Recorded gap vs roadmap

The precise current gap is packet-local again:

- the roadmap still calls for a reviewable Phase 5 trace-events reference-pattern anchor
- current `master` does not directly expose the non-runtime sample root, focused replay, manifest-backed packet, dedicated survey replay, or shared `phase5_build.zig` route for that anchor
- several shared reminder surfaces were still phrased as though that restored packet were directly readable

So the honest same-lane correction is to keep the missing-path caveat active again, trim stale restored-readback wording, and leave the lane parked until the trace-events packet either returns or the remaining shared reminder surfaces are fully aligned to the current gap.

## Non-goals

This note still does not claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring

## Next bounded step

Keep this lane parked unless a fresh trace-events-local reread finds one of two bounded changes to make:

- the missing trace-events sample packet paths return and the shared reminder surfaces need to be switched back to restored-readback wording
- another shared reminder surface still claims the missing `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_build.zig`, or `phase5_trace_events_sample*` packet as directly readable and needs one lane-local truthfulness repair

Do not widen that follow-up into runtime work.