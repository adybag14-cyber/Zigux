# Phase 5 Bytestream Review-Contract Gap

This note records the bounded closure-note state for the landed Phase 5 bytestream FIFO packet.

## Status

- `PHASE5_STATUS=active-gap`
- `PHASE5_SLICE=bytestream-review-contract-gap`
- `PHASE5_LANE_KEY=P5-Y11`
- scope: one bytestream-local closure-note or contributor-prompt truthfulness gap only

## Why this note exists

The Phase 5 roadmap asks Zigux to make approved sample idioms reviewable and repeatable, and it names `samples/kfifo/bytestream-example.c` as one of the four Linux anchors.

For the landed `samples/zigux/bytestream_fifo.zig` packet, current `master` already has the bounded sample, its paired survey note, and the shared sample-root guide. The remaining same-lane job is not sample delivery and not a new fifth sample. It is to keep the bytestream packet's contributor-facing review-contract wording honest now that the live sample packet carries a broader focus set than one survey prompt still advertises.

## Current repo reality

Current `master` already carries the bytestream packet under:

- `samples/zigux/bytestream_fifo.zig`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `samples/zigux/README.md`
- `zigux/tests/phase5_build.zig`

Those surfaces already show that the landed bytestream sample is more than a seven-cue queue-order replay.

The live sample exports a ten-item review-contract focus packet through `sample_review_focus`:

- `bounded_fifo_order`
- `wraparound_requeue`
- `peek_and_skip`
- `non_destructive_snapshot`
- `preview_truncation`
- `remaining_capacity`
- `queue_shape_boundaries`
- `helper_boundaries`
- `reset_and_replay`
- `ownership_and_lifetime`

The shared sample-root guide already reflects that broader packet by naming the embedded fixed-buffer ring cue together with remaining-capacity visibility, short-drain and empty-preview helper boundaries, overflow rejection, reset bookkeeping, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` ownership path.

The remaining drift is narrower: the bytestream survey note still includes a contributor refresh prompt that abbreviates the review-contract order down to the older shorter cue list and therefore understates the shipped Phase 5 packet.

## Approved closure

Treat the landed bytestream FIFO packet as a ten-cue Phase 5 review contract, not a seven-cue packet.

The honest same-lane follow-through is therefore:

- keep the survey-note contributor prompt aligned with the full ten-item `sample_review_focus` order already exported by `samples/zigux/bytestream_fifo.zig`
- keep any same-packet focused bytestream review-contract check aligned to that same ten-item order if current `master` still mirrors the older shorter list
- avoid reopening sample semantics, the broader shared Phase 5 guide, or unrelated Phase 5 sample families unless that one bytestream-local truthfulness repair proves impossible without them

## Boundary reminders

- do not treat this note as evidence of a missing fifth Phase 5 sample
- do not reopen Phase 9 runtime FIFO, loader, or substrate work from this bytestream-local note
- do not widen into kobject, kretprobe, trace-events, or shared multi-sample governance unless a fresh repo reread shows the same exact wording drift there too

## Next bounded step

Update the contributor-facing review-contract wording in `Documentation/zigux/phase5-kfifo-sample-survey.md` so it names the full ten-item bytestream focus packet in the same order as `samples/zigux/bytestream_fifo.zig`, then keep any directly coupled bytestream review-contract check aligned to that same order if current `master` still abbreviates it.
