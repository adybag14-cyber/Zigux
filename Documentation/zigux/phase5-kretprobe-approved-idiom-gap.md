# Phase 5 Kretprobe Approved Idiom Gap

This note records the bounded roadmap-gap state for the landed Phase 5 `kretprobe_example` packet.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=kretprobe-approved-idiom-gap`
- `PHASE5_LANE_KEY=P5-L13`
- scope: roadmap-backed approved idiom closure for the non-runtime `samples/zigux/kretprobe_example.zig` packet only

## Why this note exists

The Phase 5 roadmap asks Zigux to make approved sample idioms reviewable and repeatable, and it names `samples/kprobes/kretprobe_example.c` as one of the four Linux anchors.

For this anchor, the roadmap requirement is not just "ship any probe sample." The same landed packet also needs to stay readable as a bounded ownership-and-lifetime example, because Phase 5 explicitly calls for both side-by-side sample ports and ownership-and-lifetime examples inside the shipped sample tranche.

## Current repo reality

Current `master` already carries the non-runtime kretprobe packet under:

- `samples/zigux/kretprobe_example.zig`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`
- `zigux/tests/phase5_build.zig`
- `make -C zigux phase5-test`
- `make -C zigux phase5`

Those shared and sample-local surfaces already describe one bounded non-runtime packet with explicit symbol-selection, handler-boundary, teardown, and ownership-lifetime review cues.

## Approved idiom closure

Treat the landed `kretprobe_example` packet as the approved Phase 5 idiom for both halves of the roadmap requirement together:

- probe-lifecycle closure stays in the sample-owned `runRetargetReplay()`, `runRecoveryReplay()`, `runLifecycleGuardReplay()`, the direct `runAnchorReplay()` path, the fixed `maxactiveBudget()` cue at `20`, the one-missed-instance summary, the explicit private-data shape as one entry-timestamp word, and the timestamp-order rejection plus recovery path
- ownership-and-lifetime closure stays in the same packet through `ownershipSummary()`, sample-owned `runOwnershipReplay()`, the explicit `cold`, `initialized`, `armed`, `replay_complete`, and `exited` snapshots, the outstanding-instance exit rejection while armed, and the post-exit handler and missed-instance rejection boundaries

The honest remaining gap is therefore not a missing fifth Phase 5 sample and not a missing separate ownership-only probe sample. The remaining same-lane risk is reminder-surface drift if shared docs stop naming the kretprobe packet as one combined probe-lifecycle-plus-ownership idiom.

## Contributor reminder

When this approved-idiom note or its directly coupled kretprobe packet moves, keep these exact review cues explicit together instead of softening them into a generic probe summary:

- `runRetargetReplay()`, `runRecoveryReplay()`, `runOwnershipReplay()`, and `runLifecycleGuardReplay()` remain the public sample surfaces reviewers should point to first, with `runAnchorReplay()` still carrying the sample-local self-check path
- the exact review focus order stays `symbol_selection`, `entry_timestamp`, `private_data_shape`, `return_duration`, `missed_summary`, and `ownership_and_lifetime`
- pre-init retargeting, the fixed `maxactiveBudget()` cue at `20`, the one-missed-instance summary, outstanding-instance rejection, invalid timestamp rejection followed by recovered duration, and post-exit handler rejection remain the explicit handler-boundary and teardown guard rails for this non-runtime packet

## Boundary reminders

- do not reopen this lane by treating the Phase 9 `runtime_kretprobe` family as Phase 5 evidence
- do not imply `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` or `regs_return_value()` parity, or runtime module wiring from this Phase 5 note
- do not imply standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference samples; those cues stay under their existing helper, rollback, or later runtime lanes

## Next bounded step

Leave this note parked unless current `master` later shows another kretprobe-only reminder drift between the roadmap-backed approved-idiom wording and the already-landed survey, sample, manifest, or shared Phase 5 review packet.
