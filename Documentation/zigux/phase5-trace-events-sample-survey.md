# Phase 5 Trace-Events Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked-doc-accuracy`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L24`
- `PHASE5_SURVEYED_COMMIT=readback-gap-2026-05-13`
- scope: keep the trace-events survey note truthful against current directly readable repo evidence, the roadmap's approved Phase 5 anchor set, the freeze-map boundary, and the remaining shared-guide truthfulness gap

## Why this note exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" tranche, and `samples/trace_events/trace-events-sample.c` is still one of the four approved Linux anchors that should make Zigux idioms reviewable and repeatable.

The bounded job for this note is no longer to imply that the full trace-events sample packet is directly readable on current `master`. It is to say exactly what this run could read back today and avoid restating older sample-root or shared-build claims that the same repo path did not surface during this inspection.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 found these trace-events-adjacent surfaces directly readable today:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `.github/workflows/zigux-bootstrap.yml`

The same readback also found these current public-tree gaps for the trace-events packet:

- `samples/zigux/trace_events_sample.zig` was not directly readable
- `zigux/tests/phase5_build.zig` was not directly readable
- `zigux/tests/phase5_trace_events_sample.zig` was not directly readable
- `zigux/tests/phase5_trace_events_sample_manifest.json` was not directly readable
- `zigux/tests/phase5_trace_events_sample_survey.zig` was not directly readable

That means this note should not claim a fresh direct `zig test samples/zigux/trace_events_sample.zig`, `zig test zigux/tests/phase5_trace_events_sample_survey.zig`, or `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay on current `master`.

This run also confirmed one remaining same-lane shared-surface drift: `Documentation/zigux/phase5-sample-review-guide.md` is directly readable, but it still describes the missing trace-events sample-root and focused-test paths above as verified landed Phase 5 packet surfaces instead of framing them as current public-tree gaps.

## What still remains true

Even with that narrower readback, the roadmap, ledger, and shared reminder surfaces still keep the intended Phase 5 ownership clear:

- the approved Linux anchor is still `samples/trace_events/trace-events-sample.c`
- the Phase 5 goal is still reviewable, repeatable sample-backed idioms rather than runtime-substrate closure
- `.github/workflows/zigux-bootstrap.yml` still names the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route in the workflow packet, so any later same-lane follow-up should keep the workflow reminder, docs, and directly readable sample packet aligned rather than inventing a fifth sample or widening into the separate Phase 9 `runtime_trace_events` family
- the shared Phase 5 reminder packet still keeps the no-standalone-format-sample boundary explicit, so the formatting cue for this lane remains bounded reviewer guidance rather than a claim that current `master` now exposes a dedicated formatting sample

## Recorded gap vs roadmap

The precise current gap is narrower than the previous version of this note claimed:

- the roadmap still calls for a reviewable Phase 5 trace-events reference-pattern anchor
- current `master` still carries shared Phase 5 reminder surfaces that talk about that anchor and its reviewer packet
- current direct readback for this run did not confirm the trace-events sample-root file, the focused Phase 5 trace-events test packet, or the shared Phase 5 build file themselves
- the remaining same-lane contributor-guidance miss is now specific: `Documentation/zigux/phase5-sample-review-guide.md` still overstates those missing trace-events paths as directly readable shipped evidence

So the honest same-lane posture is readback truthfulness plus one remaining shared-guide repair, not a fresh claim that the full landed trace-events packet is directly readable today.

## Non-goals

This note still does not claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Keep this lane parked unless a follow-up run can directly read or restore the missing trace-events sample-root and focused Phase 5 test surfaces on current `master`, or publish one bounded shared-guidance repair in `Documentation/zigux/phase5-sample-review-guide.md` so it stops listing those missing trace-events paths as directly readable shipped evidence. If the repo stays in this state, prefer that one-file guide repair before widening sample behavior or runtime work.
