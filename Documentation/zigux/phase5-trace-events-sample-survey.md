# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status
- `PHASE5_STATUS=verified-mixed-readback-gap-narrowed`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L19`
- scope: keep the landed non-runtime trace-events packet reviewable through concrete sample evidence while recording the precise remaining gap against the Phase 5 roadmap on current `master`

## Why this slice exists
The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the four approved Linux anchors.

The bounded same-lane job here is not to widen runtime behavior.
It is to keep the current sample-backed trace-events packet honest on current `master`: keep the approved formatting companion explicit where direct reread still proves it, keep the broader non-runtime sample-local packet visible where current `master` now exposes it, keep the shared `zigux/tests/phase5_build.zig` route explicit as a returned shared rerun handle, and avoid collapsing a current readback split into either repo absence or full direct-proof claims.

## Current repo reality on `master`
Fresh mixed reread on 2026-05-24 still directly reconfirmed the roadmap anchor plus the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig`.

The same current reread also kept this survey note directly readable again, so it remains part of the shared reminder packet rather than part of the still-split broader sample-local set.

Current `master` now visibly carries more of the broader non-runtime trace-events packet than the older narrow wording implied:
- `samples/zigux/README.md` keeps `samples/zigux/trace_events_sample.zig` listed inside the current sample-root packet
- `zigux/tests/phase5_build.zig` now directly returns the focused `phase5-trace-events-sample-tests` and `phase5-trace-events-sample-survey-tests` routes beside the broader Phase 5 sample bundle
- current GitHub blob readback also returned `zigux/tests/phase5_trace_events_sample.zig`, whose focused replay coverage keeps payload, callback, ownership, lifetime, and review-contract cues visible on current `master`

The direct-read path in this runtime is still split, however, for the broader four-file companion packet:
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

So the honest same-lane posture is now narrower than "missing broader trace-events proof" and still stricter than "fully returned authenticated sample-local packet". The shared `zigux/tests/phase5_build.zig` route should stay framed separately as returned shared build-route evidence again rather than as companion-only support vocabulary or sample-local proof.

## Shared reminder posture
The directly coupled trace-events packet is no longer best described as formatting-only evidence.
Current `master` now keeps three distinct layers visible:
- the roadmap anchor `samples/trace_events/trace-events-sample.c`
- the directly readable bounded formatting companion `samples/zigux/trace_events_string_formatting_sample.zig`
- the broader sample-local packet that current `master` visibly wires through `zigux/tests/phase5_build.zig`, the sample-root reminder, and the focused replay `zigux/tests/phase5_trace_events_sample.zig`, even though this runtime still does not return the whole four-file companion set through one consistent authenticated contents path

Aligned reminder surfaces in this run:
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`

Those surfaces should therefore keep the selected-string plus `iter=%d` formatting cue positioned as the approved bounded formatting reminder, keep the later Phase 9 runtime trace-events family separate from this non-runtime Phase 5 packet, and keep the broader non-runtime trace-events sample-local packet framed as visible current-`master` companion evidence whose direct-read path is still split in this runtime rather than as repo absence.

The same current reminder packet also stays checker-backed in this run: `scripts/zigux/check-phase5-review-guide-surface.py` still guards the direct-proof, public-tree-backed-companion, and no-extra-sample wording across the shared Phase 5 reminder surfaces instead of leaving the approved formatting story as guide-only prose.

## Landed cue posture
Current direct evidence in this run still includes the bounded formatting companion, but the broader roadmap-backed trace-events packet is now visibly stronger than that narrow cue alone.

The current packet keeps these reviewable cues explicit:
- the roadmap anchor remains `samples/trace_events/trace-events-sample.c`
- the bounded non-runtime formatting companion remains `samples/zigux/trace_events_string_formatting_sample.zig`
- the approved formatting idiom remains the selected-string plus `iter=%d` cue described in `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- the broader focused replay packet visible through `zigux/tests/phase5_trace_events_sample.zig` now keeps payload shape, conditional event families, function-callback registration, ownership, lifetime, and the public review contract reviewable on current `master`
- the shared `zigux/tests/phase5_build.zig` route keeps that broader replay family visible as current shared rerun evidence even while the authenticated contents path still splits on parts of the broader companion set in this runtime

## Recorded gap vs roadmap
The precise current gap is not that Zigux lacks a trace-events sample packet, and it is no longer accurate to describe the roadmap gap as merely "formatting companion plus reminder prose".

The more accurate same-lane state on 2026-05-24 is:
- the roadmap-backed trace-events anchor still has a directly readable bounded formatting companion and aligned shared reminder surfaces
- current `master` also visibly carries a broader trace-events sample packet through the shared `zigux/tests/phase5_build.zig` routes, the sample-root reminder, and the focused replay `zigux/tests/phase5_trace_events_sample.zig`
- the remaining gap against the roadmap is now a proof-shape gap, not an idiom-gap: this runtime still does not return the whole broader four-file companion set through one consistent authenticated contents path, so same-lane documentation must not overstate direct proof while that split persists
- the approved formatting idiom note should stay focused on the selected-string plus `iter=%d` cue and should not be used to undercount the broader ownership-and-lifetime and tracing-example evidence already visible in the focused replay packet
- same-lane documentation should therefore keep the broader sample-local packet framed as current visible companion or shared-rerun evidence instead of calling it repo absence, while still reserving "direct authenticated proof" wording for the narrower packet this run could reconfirm through the strongest direct path

So the honest follow-through is to keep this survey note anchored to the exact packet shape current reread proved: stronger than formatting-only, still narrower than full consistent authenticated readback for every broader companion file, and still fully inside the non-runtime Phase 5 lane.

## Non-goals
This survey does not claim:
- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity
- Phase 9 runtime trace-events delivery

## Next bounded step
Leave this lane parked unless a fresh same-packet reread finds a new exact trace-events-local drift to close.

If this packet reopens soon, compare `Documentation/zigux/README.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, and only repair the next reminder surface that shows a fresh exact drift on current `master`.

The next honest same-lane upgrade would be a proof-class change only if current reread starts returning the whole broader trace-events companion set through one consistent authenticated path. Until then, keep the broader replay family framed as visible current-`master` evidence with a split direct-read path, not as repo absence and not as fully returned direct sample-local proof.
