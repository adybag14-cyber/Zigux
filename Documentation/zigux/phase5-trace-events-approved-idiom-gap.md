# Phase 5 Trace-Events Approved Idiom Gap

This note records the bounded roadmap-gap state for the landed Phase 5 `trace_events_sample` packet.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=trace-events-approved-idiom-gap`
- `PHASE5_LANE_KEY=P5-L19`
- scope: roadmap-backed approved idiom closure for the non-runtime `samples/zigux/trace_events_sample.zig` packet only

## Why this note exists

The Phase 5 roadmap asks Zigux to make approved sample idioms reviewable and repeatable, and it names `samples/trace_events/trace-events-sample.c` as one of the four Linux anchors.

For this anchor, the roadmap requirement is not just "ship any tracing sample." The same landed packet also needs to stay readable as a bounded ownership-and-lifetime example, because Phase 5 explicitly calls for both tracing examples and ownership-and-lifetime examples inside the shipped sample tranche.

## Current repo reality

Current `master` already carries the non-runtime trace-events packet under:

- `samples/zigux/trace_events_sample.zig`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`
- `zigux/tests/phase5_build.zig`
- `make -C zigux phase5-test`
- `make -C zigux phase5`

Those shared surfaces already describe one bounded non-runtime packet with explicit payload, formatting, callback-boundary, and ownership-lifetime review cues.

## Approved idiom closure

Treat the landed `trace_events_sample` packet as the approved Phase 5 idiom for both halves of the roadmap requirement together:

- tracing-example closure stays in the selected-string replay, `formattedMessage()`, the public payload and conditional boundary helpers, the callback-boundary helper, the focused event-family counts, and the explicit non-runtime boundary around tracepoint macros, scheduling, and module wiring
- ownership-and-lifetime closure stays in the same packet through `ownershipSummary()`, sample-owned `runOwnershipReplay()`, the registration-balance restoration cue, the `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and the post-exit replay and callback-registration rejection boundaries

The honest remaining gap is therefore not a missing fifth Phase 5 sample and not a missing separate ownership-only trace-events sample. The remaining same-lane risk is reminder-surface drift if shared docs stop naming the trace-events packet as one combined tracing-plus-ownership idiom.

## Contributor reminder

When this approved-idiom note or its directly coupled trace-events packet moves, keep these exact review cues explicit together instead of softening them into a generic tracing summary:

- `formattedMessage()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, and sample-owned `runOwnershipReplay()` remain the public sample surfaces reviewers should point to first
- the exact `checked_focus` order stays `descriptor_anchor`, `selected_string_cycle`, `formatted_message_surface`, `conditional_family_markers`, `callback_balance`, and `ownership_and_lifetime`
- `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection and the post-exit replay plus callback-registration rejection remain the explicit callback-boundary and teardown guard rails for this non-runtime packet

## Boundary reminders

- do not reopen this lane by treating the Phase 9 `runtime_trace_events` family as Phase 5 evidence
- do not imply `CREATE_TRACE_POINTS`, tracepoint macro parity, scheduler-backed execution, or module registration wiring from this Phase 5 note
- do not imply a standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` remains the bounded formatting cue for this lane

## Next bounded step

Leave this note parked unless current `master` later shows another trace-events-only reminder drift between the roadmap-backed approved-idiom wording and the already-landed survey, sample, manifest, or shared Phase 5 review packet.
