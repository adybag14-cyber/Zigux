# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status
- `PHASE5_STATUS=verified-shared-surface-truthfulness`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L16`
- `PHASE5_SURVEYED_COMMIT=51b8f2766be46cf0791ea33ca453d849777ecfba`
- scope: keep the landed non-runtime trace-events packet reviewable through concrete sample evidence while recording which shared Phase 5 reminder surfaces are aligned on current `master` after the latest mixed reread

## Why this slice exists
The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the four approved Linux anchors.

The bounded same-lane job here is not to widen runtime behavior.
It is to keep the current sample-backed trace-events packet honest on current `master`: keep the broader non-runtime sample-local companions in split-readback status while the authenticated contents route still misses them, keep the older shared `zigux/tests/phase5_build.zig` route visible only as current public-tree-backed support material, and avoid borrowing exact replay wording from shared reminder surfaces that are still lagging or broader than the landed packet.

## Current repo reality on `master`
Fresh mixed reread on 2026-05-19 directly reconfirmed the roadmap anchor plus the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` through authenticated sample-root readback.

That same reread kept the broader non-runtime trace-events sample-local companions in split-readback status rather than a fully returned authenticated state:
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Those paths are again carried by the live trace-events reminder packet and current public-tree-backed reread surfaces, but the authenticated contents route used for this lane still did not return them directly on 2026-05-19.

The focused `zig test` routes remain the most sample-local replays, while `zig build test --build-file zigux/tests/phase5_build.zig --summary all` stays recorded as current public-tree-backed shared support material rather than returned authenticated-contents proof.

The manifest-backed review packet still routes exact validation through `zig test samples/zigux/trace_events_sample.zig`, `zig test zigux/tests/phase5_trace_events_sample.zig`, and `zig test zigux/tests/phase5_trace_events_sample_survey.zig`, and it keeps the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route explicit as public-tree-backed split-readback support material rather than returned authenticated proof.

## Shared reminder posture
The directly coupled trace-events packet is currently strongest in the bounded formatting companion, the manifest-backed prompts, and the current public-tree-backed reread of the broader sample-local companions.

Aligned reminder surfaces in this run:
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`

Those surfaces already keep the landed trace-events packet explicit, keep the selected-string plus `iter=%d` formatting cue positioned as the approved bounded formatting reminder instead of a standalone Phase 5 formatting sample, and keep the later Phase 9 runtime trace-events family separate from this non-runtime Phase 5 packet.
They also keep the broader non-runtime trace-events companions in split-readback status instead of promoting them back to returned authenticated proof before the contents route actually does so.

A fresh 2026-05-19 sample-root reread in this run confirms the shared sample-root reminder is aligned too:
- `samples/zigux/README.md` keeps the bounded formatting companion as the direct authenticated proof and keeps the broader non-runtime trace-events companions framed as shared-reminder or repo-reality-gap surfaces until a fresh reread proves they returned directly on current `master`

The tests-root shared reminder is only inventory-aligned in this run:
- `zigux/tests/README.md` names `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`
- it also keeps the current shared-build split explicit through `zigux/tests/phase5_build.zig`
- it does not restate helper-level trace-events cues such as `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, `runLifecycleBoundaryReplay()`, `lifecycleSummary()`, the selected-string plus `iter=%d` formatting cue, or `OutstandingRegistration`; those cues remain explicit in this survey note, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, and the current public-tree-backed reread of `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, and `zigux/tests/phase5_trace_events_sample_survey.zig`

Treat the tests-root reminder as packet-inventory support material on current `master`, not as the place where the helper-level trace-events cue list is spelled out.

## Landed sample and exact checks
Current public-tree-backed reread of the landed non-runtime packet keeps these reviewable cues explicit:
- `TraceEventsReferenceSample.descriptor()` still names `samples/trace_events/trace-events-sample.c`, keeps `requires_runtime_substrate = false`, and keeps `provides_selfcheck = true`
- `runAnchorReplay()` still formats `iter=7`, exposes main iteration `7`, exposes function-callback iteration `9`, selects `Gandalf`, exposes selected-string slot `2`, keeps the `1,2` payload prefix plus zero sentinel explicit, records six main-thread family calls plus two function-callback family calls, restores callback-registration balance to zero, and keeps the exact `checked_focus` order visible
- `runPayloadBoundaryReplay()` still keeps the bounded payload-shape, selected-string, payload-length, relative-location, vararg-payload, and formatted-message cues explicit without implying runtime thread execution
- `runCallbackBoundaryRecoveryReplay()` still keeps `FunctionCallbackNotRegistered`, unregister-underflow rejection, double-registration rejection, invalid callback-count rejection, armed-exit rejection through `OutstandingRegistration`, callback-path accounting, and restored zero registration depth explicit
- `runStringFormattingCycleReplay()` still keeps the full modulo-selected string cycle explicit across counts `0` through `4`: `Mother Goose`, `Snoopy`, `Gandalf`, `Frodo`, and `One ring to rule them all`
- `runLifecycleBoundaryReplay()` still keeps the pre-init rejection packet, callback-boundary replay, lifecycle summaries before and after exit, and post-exit replay or registration rejection explicit
- `lifecycleSummary()` still keeps stage, init, replay, exit, registration-depth, and total-event-call accounting visible without private field access

The focused tests-root packet in `zigux/tests/phase5_trace_events_sample.zig` and the survey replay in `zigux/tests/phase5_trace_events_sample_survey.zig` still keep those same exact helper names, selected-string slot `2`, main iteration `7`, function-callback iteration `9`, callback-boundary error names, and packet edges explicit through current public-tree-backed reread.

## Recorded gap vs roadmap
The precise current gap is no longer "Zigux lacks a trace-events reference sample."
The more accurate same-lane state is:
- the roadmap-backed trace-events anchor already has a landed non-runtime packet with reminder, manifest, focused replay, and survey replay surfaces visible on current `master`
- the broader sample-local packet is again reviewable through public-tree-backed reread, but the authenticated contents route used for this lane still does not return those broader companions directly, so this note should keep the split explicit instead of calling them absent or claiming fully returned authenticated proof
- the shared `zigux/tests/phase5_build.zig` route still is not directly readable through the current authenticated reread, but the current public tree keeps that shared build route visible, so this lane should keep it framed as public-tree-backed support material rather than as returned authenticated proof
- the directly coupled shared docs-root, approved-idiom, sample-root, scripts-root, and tests-root surfaces already keep the landed packet and the still-explicit shared-build split honest today

So the honest same-lane follow-through is to keep this survey note anchored to the mixed-readback trace-events packet, keep the broader sample-local companions and the shared build route framed with the same split-readback posture carried by the fresher reminder surfaces, and leave the lane parked unless a fresh reread exposes a new one-file shared-surface drift.

## Non-goals
This survey does not claim:
- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step
Leave this lane parked unless a fresh same-lane reread finds a new exact shared-surface truthfulness repair to make for the landed Phase 5 sample packet.

The best next bounded follow-up is the next smallest one-file shared reminder drift that current `master` actually shows after rereading `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and the direct trace-events packet together.
