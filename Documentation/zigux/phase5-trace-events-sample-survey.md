# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=verified-shared-surface-truthfulness`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L16`
- `PHASE5_SURVEYED_COMMIT=368dcb11d347e77c13bef6607bd99b313573e389`
- scope: keep the landed non-runtime trace-events packet reviewable through concrete sample evidence while recording which shared Phase 5 reminder surfaces are aligned today and which still need their own follow-through

## Why this slice exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the four approved Linux anchors.

The bounded same-lane job here is not to widen runtime behavior. It is to keep the current sample-backed trace-events packet honest on current `master`: record the directly readable sample, focused replay, manifest, and survey replay; keep the missing shared `zigux/tests/phase5_build.zig` route explicit; and avoid borrowing exact replay wording from shared reminder surfaces that are still lagging the landed packet.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-14 directly confirmed these trace-events packet paths on current `master`:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

That same direct readback still did not recover this older shared build path:

- `zigux/tests/phase5_build.zig`

Treat the current trace-events packet as directly readable through the sample root, focused replay, manifest, and survey replay above, while keeping the missing shared build entrypoint explicit until a fresh reread proves it returned.

The manifest-backed review packet still routes exact validation through `zig test samples/zigux/trace_events_sample.zig`, `zig test zigux/tests/phase5_trace_events_sample.zig`, and `zig test zigux/tests/phase5_trace_events_sample_survey.zig` instead of the older missing shared `phase5_build.zig` route.

## Shared reminder posture

The directly coupled trace-events packet is currently strongest in the sample-backed surfaces themselves.

Aligned reminder surfaces in this run:

- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those surfaces already keep the landed trace-events packet explicit, keep the missing shared `zigux/tests/phase5_build.zig` route explicit, keep the selected-string plus `iter=%d` replay positioned as the approved formatting idiom cue instead of a standalone Phase 5 formatting sample, keep the public `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, and `runLifecycleBoundaryReplay()` helpers plus `lifecycleSummary()` route visible in the tests-root reminder, and keep the later Phase 9 runtime trace-events family separate from this non-runtime Phase 5 packet.

No additional readable shared-surface drift remains inside this exact trace-events packet today. The current same-lane gap is the still-missing shared `zigux/tests/phase5_build.zig` route rather than a helper-name mismatch in the shared reminder set.

## Landed sample and exact checks

The current landed non-runtime sample in `samples/zigux/trace_events_sample.zig` keeps these reviewable cues explicit:

- `TraceEventsReferenceSample.descriptor()` still names `samples/trace_events/trace-events-sample.c`, keeps `requires_runtime_substrate = false`, and keeps `provides_selfcheck = true`
- `runAnchorReplay()` still formats `iter=7`, exposes main iteration `7`, exposes function-callback iteration `9`, selects `Gandalf`, exposes selected-string slot `2`, keeps the `1,2` payload prefix plus zero sentinel explicit, records six main-thread family calls plus two function-callback family calls, restores callback-registration balance to zero, and keeps the exact `checked_focus` order visible
- `runPayloadBoundaryReplay()` still keeps the bounded payload-shape, selected-string, payload-length, relative-location, vararg-payload, and formatted-message cues explicit without implying runtime thread execution
- `runCallbackBoundaryRecoveryReplay()` still keeps `FunctionCallbackNotRegistered`, unregister-underflow rejection, double-registration rejection, invalid callback-count rejection, armed-exit rejection through `OutstandingRegistration`, callback-path accounting, and restored zero registration depth explicit
- `runStringFormattingCycleReplay()` still keeps the full modulo-selected string cycle explicit across counts `0` through `4`: `Mother Goose`, `Snoopy`, `Gandalf`, `Frodo`, and `One ring to rule them all`
- `runLifecycleBoundaryReplay()` still keeps the pre-init rejection packet, callback-boundary replay, lifecycle summaries before and after exit, and post-exit replay or registration rejection explicit
- `lifecycleSummary()` still keeps stage, init, replay, exit, registration-depth, and total-event-call accounting visible without private field access

The focused tests-root packet in `zigux/tests/phase5_trace_events_sample.zig` and the survey replay in `zigux/tests/phase5_trace_events_sample_survey.zig` still keep those same exact helper names, iteration cues, callback-boundary error names, and packet edges explicit.

## Recorded gap vs roadmap

The precise current gap is no longer "Zigux lacks a trace-events reference sample." The more accurate same-lane state is:

- the roadmap-backed trace-events anchor already has a directly readable non-runtime sample plus focused tests-root evidence
- current `master` still does not directly expose the older shared `zigux/tests/phase5_build.zig` route
- the readable shared reminder packet for this sample is presently aligned around the landed helper vocabulary and the separate Phase 9 runtime boundary

So the honest same-lane follow-through is to keep this survey note anchored to the directly readable trace-events packet, leave the shared reminder packet parked while it remains aligned, and wait for either a new one-file reminder drift or the shared build route to return.

## Non-goals

This survey does not claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Leave this lane parked unless a fresh same-lane reread finds one bounded change to make:

- `zigux/tests/phase5_build.zig` returns and the survey note can narrow its missing-route wording honestly
- a new one-file shared reminder drift appears across the current trace-events packet, its sample-backed survey, or the Phase 5-versus-Phase 9 boundary

Do not widen that follow-up into runtime work or broader sample semantics.