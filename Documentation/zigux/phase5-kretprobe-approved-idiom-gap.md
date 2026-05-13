# Phase 5 Kretprobe Approved Idiom Gap

This note records the bounded roadmap-gap state for the Phase 5 `samples/kprobes/kretprobe_example.c` anchor while the earlier non-runtime Zigux packet is not directly readable on current `master`.

## Status

- `PHASE5_STATUS=parked-gap-confirmed`
- `PHASE5_SLICE=kretprobe-approved-idiom-gap`
- `PHASE5_LANE_KEY=P5-L18`
- scope: roadmap-backed approved idiom truthfulness for the non-runtime kretprobe anchor without widening into runtime work

## Why this note exists

The Phase 5 roadmap still asks Zigux to make approved sample idioms reviewable and repeatable, and it still names `samples/kprobes/kretprobe_example.c` as one of the four Linux anchors.

For this anchor, the roadmap requirement is not just "ship any probe sample." The same Phase 5 packet also needs to stay readable as a bounded ownership-and-lifetime example, because Phase 5 explicitly calls for both side-by-side sample ports and ownership-and-lifetime examples inside the approved sample tranche.

## Current repo reality

Fresh repo-first inspection on 2026-05-13 found these kretprobe-adjacent reminder surfaces directly readable on current `master`:

- `Documentation/zigux/phase5-kretprobe-approved-idiom-gap.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

That same direct readback did not recover the older non-runtime sample packet paths:

- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`
- `zigux/tests/phase5_build.zig`
- `make -C zigux phase5-test`
- `make -C zigux phase5`

Treat those missing sample-root, focused-replay, manifest, survey-replay, and shared-build surfaces as the current public-tree gap for this roadmap note until a fresh reread proves they returned.

## Approved idiom state

The roadmap-backed approved idiom remains the same, but current `master` cannot truthfully claim that it is presently landed through a directly readable non-runtime kretprobe sample packet.

The honest same-lane posture is therefore narrower:

- keep `samples/kprobes/kretprobe_example.c` named as the approved Linux anchor
- keep the ownership-and-lifetime expectation explicit as part of the intended Phase 5 sample packet
- keep the separate Phase 9 `runtime_kretprobe` family out of Phase 5 evidence
- do not describe sample-owned helper names, manifest prompts, or shared `phase5_build.zig` replay routes here as current directly readable proof while those paths remain absent from direct readback

The remaining roadmap gap is no longer just reminder-surface drift. The current direct-readback gap is the missing non-runtime kretprobe sample packet itself, together with any notes that still describe that packet as already landed.

## Contributor reminder

When this approved-idiom note or its directly coupled kretprobe reminder packet moves, keep these boundaries explicit:

- route current review through `Documentation/zigux/phase5-kretprobe-sample-survey.md` while the sample-root and tests-root packet remains missing from direct readback
- do not substitute `samples/zigux/runtime_kretprobe.zig` or `samples/zigux/runtime_kretprobe_loader.zig` for the missing non-runtime Phase 5 packet
- do not imply `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` or `regs_return_value()` parity, or runtime module wiring from this note
- if the missing non-runtime packet returns later, refresh this note in the same pass that restores the survey note and any shared reminder surfaces so the approved-idiom claim becomes directly readable again

## Boundary reminders

- do not reopen this lane by treating the Phase 9 `runtime_kretprobe` family as Phase 5 evidence
- do not imply standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference samples; those cues stay under their existing helper, rollback, or later runtime lanes

## Next bounded step

Leave this note parked unless current `master` later shows one of two bounded same-lane changes:

- the missing non-runtime kretprobe sample packet returns and this note needs to switch back to direct-readback approved-idiom wording
- another shared or dedicated kretprobe reminder surface still claims the missing sample-root, focused-replay, manifest, survey-replay, or shared-build packet as already landed and needs one truthfulness repair
