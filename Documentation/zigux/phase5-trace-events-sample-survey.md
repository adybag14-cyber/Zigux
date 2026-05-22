# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status
- `PHASE5_STATUS=verified-public-fallback-companion-truthfulness`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L22`
- `PHASE5_SURVEYED_COMMIT=51b8f2766be46cf0791ea33ca453d849777ecfba`
- scope: keep the landed non-runtime trace-events packet reviewable through concrete sample evidence while recording which shared Phase 5 reminder surfaces are aligned on current `master` after the latest mixed reread

## Why this slice exists
The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the four approved Linux anchors.

The bounded same-lane job here is not to widen runtime behavior.
It is to keep the current sample-backed trace-events packet honest on current `master`: keep the bounded formatting companion explicit where direct reread still proves it, keep the broader non-runtime sample-local companions visible as public-tree-backed companion evidence while the contents route still misses them, keep the shared `zigux/tests/phase5_build.zig` route explicit as a returned shared rerun handle now that direct reread serves it again, and avoid borrowing exact replay wording from sample-local files that this run could not re-read directly.

## Current repo reality on `master`
Fresh mixed reread on 2026-05-20 still directly reconfirmed the roadmap anchor plus the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` through authenticated sample-root readback.

A fresh 2026-05-22 authenticated reread in this lane also returned this survey note directly again, so it no longer belongs in the still-missing authenticated sample-local companion set.

That same 2026-05-22 reread still kept the broader non-runtime trace-events sample-local companions out of the directly readable packet in this runtime:
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Authenticated contents readback still returned `404` for the four sample-local companion paths above on 2026-05-22.
That same 2026-05-22 authenticated reread also returned `zigux/tests/phase5_build.zig` directly again, including the focused `phase5-trace-events-sample-tests` and `phase5-trace-events-sample-survey-tests` routes beside the broader Phase 5 sample bundle.
Fresh public current-`master` reread in this run also surfaced those four broader sample-local companion paths again through their live GitHub blob pages:
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

This note should therefore keep the broader sample-local packet framed as current public-tree-backed companion or historical-support evidence rather than collapsing it into repo absence. The shared `zigux/tests/phase5_build.zig` route should stay framed separately as returned shared build-route evidence again rather than as companion-only support vocabulary.

The bounded formatting companion is therefore the strongest direct sample-root trace-events evidence this run could reconfirm.
Treat the focused `zig test` routes for the broader sample-local packet as current public-tree-backed support vocabulary until a fresh reread returns those files directly again. Treat `zig build test --build-file zigux/tests/phase5_build.zig --summary all` as a returned shared rerun handle again, not as the only proof of the broader sample-local replay family.

## Shared reminder posture
The directly coupled trace-events packet is currently strongest in the bounded formatting companion and the shared reminder surfaces that keep its limits explicit.

Aligned reminder surfaces in this run:
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`

Those surfaces already keep the landed trace-events packet explicit, keep the selected-string plus `iter=%d` formatting cue positioned as the approved bounded formatting reminder instead of a standalone Phase 5 formatting sample, and keep the later Phase 9 runtime trace-events family separate from this non-runtime Phase 5 packet.
They also should keep the broader non-runtime trace-events companions framed as current public-tree-backed companion or shared reminder vocabulary until the contents route actually returns those files again.
The same current reminder packet also stays checker-backed in this run: `scripts/zigux/check-phase5-review-guide-surface.py` still guards the direct-proof, public-tree-backed-companion, and no-extra-sample wording across `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` instead of leaving the approved formatting story as guide-only prose.

A fresh 2026-05-20 sample-root reread in this run confirms the shared sample-root reminder is still aligned on the narrow direct packet:
- `samples/zigux/README.md` keeps the bounded formatting companion as the direct authenticated proof and keeps the broader non-runtime trace-events companions framed as shared-reminder, historical-support, or current public-tree-backed companion surfaces until a fresh reread proves they returned directly on current `master`

The tests-root shared reminder is only inventory-aligned in this run:
- `zigux/tests/README.md` still names `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`
- it also keeps the current shared-build split explicit through `zigux/tests/phase5_build.zig`, which this run could directly reread again even though the four broader sample-local companions still remained off the authenticated path
- it does not restate helper-level trace-events cues such as `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, `runLifecycleBoundaryReplay()`, `lifecycleSummary()`, the selected-string plus `iter=%d` formatting cue, or `OutstandingRegistration`; those cues remain explicit in the bounded formatting companion and the shared reminder packet, not in any broader sample-local file that this run could directly re-read

Treat the tests-root reminder as packet-inventory support material on current `master`, with the returned shared build route explicit again, not as proof that the broader sample-local trace-events replay files have returned through the same current read path.

## Landed cue posture
Current direct evidence in this run is limited to the bounded formatting companion and the shared reminder packet that names it.
That direct packet still keeps these reviewable cues explicit:
- the roadmap anchor remains `samples/trace_events/trace-events-sample.c`
- the bounded non-runtime companion remains `samples/zigux/trace_events_string_formatting_sample.zig`
- the approved formatting idiom remains the selected-string plus `iter=%d` cue described in `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- bounded destination behavior remains part of the approved idiom reminder: `formatIterationMessageInto(12, [5]u8)` stays a no-space boundary, while `formatIterationMessageInto(12, [7]u8)` stays the success-sized `iter=12` case without turning this packet into a standalone formatting-helper sample

Broader helper-level trace-events cues from the older sample-local replay packet should stay framed as current public-tree-backed or historical-support vocabulary until `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, and `zigux/tests/phase5_trace_events_sample_survey.zig` return through the same current direct authenticated read path again.

## Recorded gap vs roadmap
The precise current gap is not that Zigux lacks every trace-events reminder surface.
The more accurate same-lane state on 2026-05-22 is:
- the roadmap-backed trace-events anchor still has a directly readable bounded formatting companion and aligned shared reminder surfaces
- the broader non-runtime sample-local packet is not currently re-readable through the authenticated contents route used in this run, but a fresh public current-`master` reread did surface `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` again through their live GitHub blob pages
- the shared `zigux/tests/phase5_build.zig` route now returns directly again and should stay explicit as the shared rerun handle for the broader Phase 5 sample bundle instead of companion-only evidence
- same-lane documentation should therefore keep the broader sample-local packet framed as current public-tree-backed companion or historical-support references instead of calling it repo absence or directly readable proof, while keeping the returned shared build route classified separately from that still-missing authenticated sample-local set

So the honest follow-through is to keep this survey note anchored to the narrow direct packet that current reread actually proved, while leaving the broader sample-local replay family parked in current public-tree-backed companion status until a future reread returns those files directly again.

## Non-goals
This survey does not claim:
- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step
Leave this lane parked unless a fresh same-packet reread finds a new exact trace-events-local drift to close.

Current public `master` already shows the previously suggested `checked_focus` follow-through in `zigux/tests/phase5_trace_events_sample.zig`, so there is no outstanding focused-tests replay repair to schedule from this note.

If this packet reopens, keep the next step to one same-packet survey note, manifest, focused replay, or shared reminder alignment that reflects the already-landed `checked_focus` contract without widening into shared Phase 5 guide work, the formatting-only companion lane, or the separate Phase 9 runtime trace-events family.
