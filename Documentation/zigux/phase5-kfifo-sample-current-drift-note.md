# Phase 5 Kfifo Sample Current Drift Note

This note records one bounded repo-first follow-through for the Phase 5 `samples/kfifo/bytestream-example.c` sample lane.

## Lane

* `lane_key`: `P5-Y02`
* `phase`: `Phase 5`
* `scope`: `samples/zigux/bytestream_fifo.zig` and the directly coupled bytestream sample packet only
* `checked_on`: `2026-05-12`

## Current repo evidence on `master`

Repo-first inspection on 2026-05-12 shows that `samples/zigux/bytestream_fifo.zig` currently lands a smaller sample contract than the broader bytestream packet wording around it.

Current sample-owned cues that are directly readable in `samples/zigux/bytestream_fifo.zig` are:

* `StorageBacking.embedded_fixed_buffer`
* `previewInto()`
* `snapshotInto()`
* `reset()`
* `count()`
* `init()` -> `runAnchorReplay()` -> `exit()`
* `reviewContract().focus` with `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `reset_and_replay`, and `ownership_and_lifetime`

The broader bytestream packet wording currently goes further than that landed sample file. `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, and `zigux/tests/phase5_bytestream_fifo_manifest.json` all currently speak as if the bytestream sample already exposes a larger helper-and-queue-shape packet including:

* `runPreviewBoundaryReplay()`
* `runWrappedPreviewReplay()`
* `visibleSpanSummary()`
* `available()`
* `usesWrappedStorageWindow()`
* review-focus cues such as `remaining_capacity`, `queue_shape_boundaries`, and `helper_boundaries`

Treat that broader wording as current drift, not as proof that the larger helper packet is already landed in `samples/zigux/bytestream_fifo.zig`.

## Why this note is the next safe step

The sample file is the tightest source of truth for this lane.

Changing the sample implementation here without replaying the full bytestream packet would risk inventing behavior. Rewriting every shared Phase 5 surface in one pass would widen beyond this lane.

This note keeps the current repo evidence honest while preserving a small next step inside the same sample family.

## Next bounded step

Pick one direction and keep it inside the bytestream sample packet only:

1. land the broader helper-and-queue-shape cues in `samples/zigux/bytestream_fifo.zig` so the sample matches the survey, guide, README, and manifest wording already on `master`, or
2. trim the bytestream-specific wording in `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, and `zigux/tests/phase5_bytestream_fifo_manifest.json` back to the smaller contract that the current sample file actually lands

Do not widen into the other Phase 5 samples or the separate Phase 9 runtime family while making that follow-through.

## Non-goals

This note does not reopen:

* `kobject`, `kretprobe`, or `trace_events` Phase 5 packets
* any `samples/zigux/runtime_*` Phase 9 family
* procfs, user-copy, locking, or module-registration claims for the bytestream sample
