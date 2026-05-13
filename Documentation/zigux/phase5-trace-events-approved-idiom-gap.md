# Phase 5 Trace-Events Approved Idiom Gap

This note records the bounded roadmap-gap state for the Phase 5 `trace_events_sample` packet.

## Status

- `PHASE5_STATUS=parked-survey-backed-gap-aligned`
- `PHASE5_SLICE=trace-events-approved-idiom-gap`
- `PHASE5_LANE_KEY=P5-L19`
- scope: roadmap-backed approved-idiom reminder for the non-runtime trace-events packet only, kept truthful against the current survey-first readback gap

## Why this note exists

The Phase 5 roadmap asks Zigux to make approved sample idioms reviewable and repeatable, and it names `samples/trace_events/trace-events-sample.c` as one of the four Linux anchors.

For this anchor, the roadmap requirement is not just "ship any tracing sample." The same non-runtime packet also needs to stay readable as a bounded ownership-and-lifetime example, because Phase 5 explicitly calls for both tracing examples and ownership-and-lifetime examples inside the shipped sample tranche.

## Current repo reality

Fresh direct readback on 2026-05-13 recovered these trace-events reminder surfaces on current `master`:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

That same readback still did not recover the older direct packet paths:

- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Treat the current evidence for this lane as survey-backed reminder surfaces, not as a directly readable sample-root plus focused-test packet.

## Approved idiom closure

The roadmap decision does not change just because direct readback is currently narrower. For this Linux anchor, the intended non-runtime `trace_events_sample` packet remains the approved Phase 5 combined idiom for both halves of the requirement whenever the packet is directly reviewable again:

- tracing-example closure belongs in the selected-string replay, `formattedMessage()`, the public payload and conditional boundary helpers, the callback-boundary helper, the focused event-family counts, and the explicit non-runtime boundary around tracepoint macros, scheduling, and module wiring
- ownership-and-lifetime closure belongs in the same packet through `ownershipSummary()`, sample-owned `runOwnershipReplay()`, the registration-balance restoration cue, the `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and the post-exit replay plus callback-registration rejection boundaries

Until those packet files return to direct readback, shared docs should describe that combined idiom through the survey-first reminder surfaces instead of claiming the missing sample-root and focused-test files are currently readable.

The honest remaining gap is therefore reminder-surface truthfulness, not evidence for a fifth Phase 5 sample and not evidence for a separate ownership-only trace-events sample.

## Contributor reminder

While the direct packet paths remain unreadable, lead review through `Documentation/zigux/phase5-trace-events-sample-survey.md` and the shared Phase 5 review guide.

If the packet paths return, keep these exact review cues explicit together instead of softening them into a generic tracing summary:

- `formattedMessage()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, and sample-owned `runOwnershipReplay()` remain the public sample surfaces reviewers should point to first
- the exact `checked_focus` order stays `descriptor_anchor`, `selected_string_cycle`, `formatted_message_surface`, `conditional_family_markers`, `callback_balance`, and `ownership_and_lifetime`
- `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection and the post-exit replay plus callback-registration rejection remain the explicit callback-boundary and teardown guard rails for this non-runtime packet
- if `Documentation/zigux/README.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` summarises this anchor, keep the same survey-backed posture there too: do not call `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_build.zig`, or `phase5_trace_events_sample*` current direct-readback evidence until a fresh reread proves those exact paths returned

## Boundary reminders

- do not reopen this lane by treating the Phase 9 `runtime_trace_events` family as Phase 5 evidence
- do not imply `CREATE_TRACE_POINTS`, tracepoint macro parity, scheduler-backed execution, or module registration wiring from this Phase 5 note
- do not imply a standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; the selected-string plus `iter=%d` cue stays a bounded formatting reminder only when the current survey-backed gap is kept explicit too

## Next bounded step

Leave this note parked unless current `master` later shows one of two same-packet changes:

- the missing `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_build.zig`, or `phase5_trace_events_sample*` files return to direct readback and this note needs to switch back from survey-backed wording
- another directly coupled reminder surface starts implying the missing trace-events packet is readable again or that a separate fifth sample is needed
