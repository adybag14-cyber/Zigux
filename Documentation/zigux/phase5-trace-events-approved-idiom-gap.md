# Phase 5 Trace-Events Approved Idiom Gap

This note records the bounded roadmap-backed approved-idiom state for the Phase 5 `trace_events_sample` packet.

## Status

- `PHASE5_STATUS=verified-direct-packet-aligned`
- `PHASE5_SLICE=trace-events-approved-idiom-gap`
- `PHASE5_LANE_KEY=P5-L20`
- scope: roadmap-backed approved-idiom reminder for the directly readable non-runtime trace-events packet only, kept truthful against the current sample-backed review surface

## Why this note exists

The Phase 5 roadmap asks Zigux to make approved sample idioms reviewable and repeatable, and it names `samples/trace_events/trace-events-sample.c` as one of the four Linux anchors.

For this anchor, the roadmap requirement is not just "ship any tracing sample." The same non-runtime packet also needs to stay readable as a bounded ownership-and-lifetime example, because Phase 5 explicitly calls for both tracing examples and ownership-and-lifetime examples inside the shipped sample tranche.

## Current repo reality

Fresh direct readback on 2026-05-14 recovered this directly readable trace-events packet on current `master`:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
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

Treat the current evidence for this lane as a directly readable sample-backed packet with one still-missing shared build route, not as a survey-only reminder packet and not as evidence for a fifth Phase 5 sample.

## Approved idiom closure

The roadmap decision stays the same, but the current packet evidence is now direct rather than survey-only. For this Linux anchor, the non-runtime `trace_events_sample` packet remains the approved Phase 5 combined idiom for both halves of the requirement:

- tracing-example closure belongs in `runAnchorReplay()`, `formattedMessage()`, `runPayloadBoundaryReplay()`, `runStringFormattingCycleReplay()`, `runCallbackBoundaryRecoveryReplay()`, the focused event-family counts, and the explicit non-runtime boundary around tracepoint macros, scheduling, and module wiring
- ownership-and-lifetime closure belongs in the same packet through `lifecycleSummary()`, `runLifecycleBoundaryReplay()`, the registration-balance restoration cue, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and the post-`exit()` replay plus callback-registration rejection boundaries

The honest remaining gap is therefore not missing trace-events sample evidence. It is simply the still-missing shared `zigux/tests/phase5_build.zig` route plus the need to keep reminder surfaces truthful about that split.

## Contributor reminder

Lead review for this packet through the directly readable sample-backed surfaces above, with `Documentation/zigux/phase5-trace-events-sample-survey.md` and `zigux/tests/phase5_trace_events_sample_manifest.json` as the exact contract prompts.

Keep these exact review cues explicit together instead of softening them into a generic tracing summary:

- `runAnchorReplay()`, `formattedMessage()`, `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, `runLifecycleBoundaryReplay()`, and `lifecycleSummary()` remain the public sample surfaces reviewers should point to first
- the exact `checked_focus` order stays `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime`
- the selected-string plus `iter=%d` cue remains the approved bounded formatting reminder through the directly readable packet, with the full modulo-selected string cycle still reviewable across counts `0` through `4`
- `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection and the post-`exit()` replay plus callback-registration rejection remain the explicit callback-boundary and teardown guard rails for this non-runtime packet
- if `Documentation/zigux/README.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` summarises this anchor, keep the same packet split there too: do not call `zigux/tests/phase5_build.zig` current direct-readback evidence until a fresh reread proves that exact path returned

## Boundary reminders

- do not reopen this lane by treating the Phase 9 `runtime_trace_events` family as Phase 5 evidence
- do not imply `CREATE_TRACE_POINTS`, tracepoint macro parity, scheduler-backed execution, or module registration wiring from this Phase 5 note
- do not imply a standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; the selected-string plus `iter=%d` cue stays a bounded formatting reminder inside the directly readable trace-events packet, not a separate anchor

## Next bounded step

Leave this note parked unless current `master` later shows one of two same-packet changes:

- the missing `zigux/tests/phase5_build.zig` route returns to direct readback and this note needs to narrow its missing-route wording
- another directly coupled reminder surface starts implying the trace-events packet is survey-only again, uses the older helper names, or suggests a separate fifth sample
