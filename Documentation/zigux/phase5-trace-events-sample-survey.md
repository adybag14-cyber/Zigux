# Phase 5 Trace-Events Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked-readback-aligned`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L24`
- `PHASE5_SURVEYED_COMMIT=readback-restored-2026-05-13`
- scope: keep the trace-events survey note truthful against current directly readable repo evidence, the roadmap's approved Phase 5 anchor set, and the freeze-map boundary without widening into runtime work

## Why this note exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" tranche, and `samples/trace_events/trace-events-sample.c` is still one of the four approved Linux anchors that should make Zigux idioms reviewable and repeatable.

The bounded job for this note is now narrower than the older readback-gap version: say exactly what current `master` exposes today, keep the landed non-runtime trace-events packet explicit, and avoid widening the sample into runtime-substrate claims.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 found these trace-events-adjacent surfaces directly readable today:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/trace_events_sample.zig`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

That same readback closes the older missing-path caveat: current `master` now exposes the sample root, focused replay, manifest-backed packet, dedicated survey replay, and shared `phase5_build.zig` route as directly readable evidence for the non-runtime trace-events sample packet.

The directly readable shared reviewer packet is already aligned with that landed state:

- `Documentation/zigux/phase5-sample-review-guide.md` keeps `formattedMessage()`, the public `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, the exact `checked_focus` order, restored registration-balance cues, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and post-exit replay rejection explicit
- `Documentation/zigux/review-checklist.md` keeps the same callback-boundary, ownership-lifetime, and formatting cues explicit as the current landed review packet
- `samples/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` all treat the trace-events packet as part of the shipped four-sample non-runtime Phase 5 route instead of as a missing sample-root or focused-test gap

## What still remains true

Even with that restored readback, the roadmap and ledger still keep the intended Phase 5 ownership clear:

- the approved Linux anchor is still `samples/trace_events/trace-events-sample.c`
- the Phase 5 goal is still reviewable, repeatable sample-backed idioms rather than runtime-substrate closure
- `zigux/tests/phase5_build.zig`, `make -C zigux phase5-test`, and `make -C zigux phase5` remain the shared replay routes for the four-sample non-runtime packet, while `zig test samples/zigux/trace_events_sample.zig` stays the sample-local direct self-check named by the shared reviewer packet
- the later `samples/zigux/runtime_trace_events.zig` and `samples/zigux/runtime_trace_events_loader.zig` family still belongs to the separate Phase 9 runtime lane and should not be counted as extra proof for the non-runtime Phase 5 sample packet
- the trace-events Phase 5 packet still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample, so the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` remains the bounded formatting idiom cue

## Recorded gap vs roadmap

The precise current gap is now note-local rather than packet-local:

- the roadmap still calls for a reviewable Phase 5 trace-events reference-pattern anchor
- current `master` now directly exposes the landed sample root, focused replay, manifest-backed packet, dedicated survey replay, and shared build route for that anchor
- the directly readable shared reviewer packet already describes that landed state honestly
- the remaining truthfulness gap was this survey note's older missing-path wording

So the honest same-lane correction is to retire the older missing-path caveat and park the lane unless one of the directly coupled trace-events packet surfaces drifts again.

## Non-goals

This note still does not claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring

## Next bounded step

Leave this lane parked unless a fresh trace-events-local reread finds drift between this note and the directly readable sample packet under `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_build.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, or `zigux/tests/phase5_trace_events_sample_survey.zig`. If it reopens, keep the follow-up to one sample-local note, manifest, or replay-contract alignment step before widening into shared Phase 5 wording or separate runtime work.
