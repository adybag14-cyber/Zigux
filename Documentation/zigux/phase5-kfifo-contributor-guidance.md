# Phase 5 Kfifo Contributor Guidance

This note keeps the landed Phase 5 bytestream FIFO sample reviewable without widening the non-runtime packet into procfs, user-copy, locking, or module-registration claims.

## Status

* `PHASE5_STATUS=landed-contributor-guidance`
* `PHASE5_LANE_KEY=P5-L05`
* `PHASE5_SAMPLE=samples/zigux/bytestream_fifo.zig`
* scope: bytestream-only contributor prompts for the existing non-runtime sample packet
* directly readable surfaces in this run:
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `Documentation/zigux/phase5-sample-review-guide.md`
  * `samples/zigux/bytestream_fifo.zig`
* same-lane readback caveat for this run:
  * `zigux/tests/phase5_bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * `zigux/tests/phase5_bytestream_fifo_survey.zig`

Those paired test paths remained inconsistent through one GitHub contents route in this run, so the prompts below stay grounded in the directly readable sample-root contract and the already-landed survey wording.

## Why this note exists

Current `master` already ships the bytestream FIFO sample and survey note. The remaining bytestream-only gap was contributor readability inside the current Phase 5 reminder packet: queue-shape and reset-and-replay cues had grown beyond the older shorter summary, which made reviewers reconstruct part of the packet from the sample body instead of from one dedicated reminder.

## Keep these cues explicit

When a change touches `samples/zigux/bytestream_fifo.zig` or its directly coupled survey wording, keep all of the following visible together:

* `BytestreamFifoSample.descriptor()` still names `samples/kfifo/bytestream-example.c` and keeps `requires_runtime_substrate = false`, `provides_selfcheck = true`, and `StorageBacking.embedded_fixed_buffer` explicit
* `reviewContract().focus` keeps the current ten-item order: `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`
* `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, and `runWrappedPreviewReplay()` stay paired with the replay-visible markers `preview_len`, `preview_total_visible`, and `preview_truncated` so preview behavior and truncation stay reviewable without mutating queue state
* `visibleSpanSummary()` keeps `head_index`, `tail_index`, `first_window_len`, `second_window_len`, and `wraps` explicit, and `usesWrappedStorageWindow()` continues to make the rollover boundary visible instead of leaving wrapped-window state implicit in ring arithmetic
* helper-boundary coverage stays visible at empty peek/skip, empty enqueue, short drain of `"hel"` with queued `"lo"`, full-capacity preview, overflow rejection, and skip-at-capacity reopening one slot before wrapped requeue
* `reset()` keeps queue clearing separate from lifecycle bookkeeping so contributors can review queue reuse without accidentally rewinding `stage_state`, `init_runs`, or `exit_runs`
* the ownership path remains the bounded non-runtime `init()` -> `runAnchorReplay()` -> `exit()` packet rather than drifting toward procfs, user-copy, locking, or module-registration claims

## Review posture

This note does not reopen the broader blocked `P5-L04` sample-root README cleanup and it does not claim fresh runtime or loader coverage. Its job is narrower: keep the already-landed bytestream sample and survey easy to review from directly readable current-head evidence.

## Verification

This note was prepared from direct current-`master` readback of `samples/zigux/bytestream_fifo.zig`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, and `Documentation/zigux/phase5-sample-review-guide.md`.

No new local `zig test` replay was run in this doc-only pass.

## Next bounded step

Leave this note parked unless the bytestream sample or survey packet changes again. If it reopens, keep the next follow-through to one directly coupled bytestream guide, survey, or sample-root truthfulness repair only.