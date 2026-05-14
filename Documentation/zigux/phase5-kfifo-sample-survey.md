# Phase 5 Kfifo Sample Survey

This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-split-readback-packet`
- `PHASE5_LANE_KEY=P5-L01`
- `PHASE5_SLICE=kfifo-reference-sample-readback`
- scope: keep the bytestream survey note truthful about the exact non-runtime packet that current `master` exposes across authenticated connector readback and public-tree blob readback
- current directly reviewed same-lane surfaces in this refresh:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`
  - `samples/zigux/bytestream_fifo.zig`
  - public-tree blob readback for `zigux/tests/phase5_bytestream_fifo.zig`
  - public-tree blob readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - public-tree blob readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - public-tree blob readback for `zigux/tests/phase5_build.zig`

## Why this slice exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo still exposes the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The bounded same-lane job for this note is therefore narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the roadmap gap stated honestly, and stop collapsing the broader focused replay, manifest, survey, or shared build packet into either "fully direct connector proof" or "missing from `master`" when fresh readback now splits across those two paths.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-14 confirmed these same-lane facts:

- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.
- that sample file still makes the non-runtime idiom explicit through `BytestreamFifoSample.descriptor()`, `StorageBacking.embedded_fixed_buffer`, `reviewContract().focus`, `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle.
- the shared Phase 5 guide in `Documentation/zigux/phase5-sample-review-guide.md` and the sample-root summary in `samples/zigux/README.md` already keep this anchor routed through the survey note and the broader bytestream packet wording instead of pretending the sample stands alone.
- authenticated GitHub contents reads in this environment still did not recover these companion paths:
  - `zigux/tests/phase5_bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - `zigux/tests/phase5_build.zig`
- current public-tree blob readback on `master` does expose those same companion paths, including the bytestream manifest's `lane_key` `P5-L01`, the survey gate's approved in-memory FIFO checks, and the shared `phase5_build.zig` route that wires `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` together.

That means the honest same-lane posture today is:

- the roadmap-backed kfifo sample idiom is still present at the sample root
- the broader focused replay, manifest-backed packet, survey replay, and shared Phase 5 build route are publicly visible on current `master`
- authenticated connector readback for those broader packet files still fails in this environment, so reminder surfaces should describe the split readback honestly instead of calling the files absent or pretending the connector path already recovered them

## Approved idiom for the current bytestream sample

Until a bounded runtime substrate exists, the approved Phase 5 `kfifo` idiom should:

- model FIFO state and ordered operations entirely in memory
- keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`
- keep the Linux anchor path explicit through a descriptor or note
- keep ownership and lifetime boundaries visible through explicit initialization, replay, reset, and teardown states
- keep non-destructive preview and snapshot behavior explicit so reviewers can inspect queued state without inferring hidden mutation
- keep rollover and queue-shape cues explicit through `visibleSpanSummary()` and `usesWrappedStorageWindow()`
- keep helper-boundary behavior explicit at empty, short-drain, full, overflow, skip-at-capacity, and reset edges
- keep procfs, user-copy, locking, and module-registration claims out of scope unless a later runtime lane lands the required substrate first

In practice, the approved idiom remains a bounded side-by-side sample, not a claim that Zigux already ships `proc_create()`, `kfifo_from_user()`, `kfifo_to_user()`, or runtime module parity.

## Sample-visible cues

The directly readable sample still keeps these cues visible on current `master`:

- ordered enqueue, drain, and refill behavior stays explicit through `runAnchorReplay()`
- non-destructive preview behavior stays explicit through `previewInto()`
- full queued-state capture stays explicit through `snapshotInto()`
- rollover and split-window behavior stay explicit through `runWrappedPreviewReplay()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()`
- helper-boundary behavior stays explicit at empty, short-drain, full-capacity, skip-at-capacity, and reset edges
- ownership and lifetime stay explicit through the `cold`, `initialized`, `replay_complete`, and `exited` stages
- docs should keep procfs, user-copy, locking, and runtime registration out of scope for this Phase 5 sample

## Exact checks verified on 2026-05-14

A focused `zig test samples/zigux/bytestream_fifo.zig` replay against the current `master` sample file passed all six in-file checks. The exact verified checks were:

- descriptor, Linux anchor, and review packet markers stay aligned: `bytestream_fifo`, `samples/kfifo/bytestream-example.c`, `requires_runtime_substrate = false`, `provides_selfcheck = true`, `StorageBacking.embedded_fixed_buffer`, the ten-item `reviewContract().focus` order, and the four non-goals all match the current sample packet
- `runAnchorReplay()` still proves the bounded FIFO replay body exactly: `"hello"` drains first, `{ 0, 1 }` is requeued, `skipByte()` removes `2`, `peekByte()` then sees `3`, `previewInto()` reports `copied = 8`, `total_visible = 32`, and `truncated = true`, `snapshotInto()` captures the full 32-byte queue, the fill range remains `20` through `42`, and the final drained sequence is `[3, 4, 5, 6, 7, 8, 9, 0, 1, 20..42]`
- helper-boundary checks stay explicit at empty and short-drain edges: empty `peekByte()` and `skipByte()` return `null`, empty `enqueueSlice(&.{})` copies `0`, empty preview leaves the destination bytes unchanged, draining `"hello"` into a three-byte buffer leaves `"lo"` queued, and draining an empty queue returns `0`
- full-capacity and wraparound edges stay explicit: a fully packed queue rejects `pushByte(255)`, skipping one byte opens a single slot, the refill push succeeds, and the queue-shape helpers flip from a single visible span to `first_window_len = 31`, `second_window_len = 1`, and `usesWrappedStorageWindow() = true`
- queue-shape replay helpers remain truthful: `runPreviewBoundaryReplay()` still yields snapshot prefix `{ 2, 3, 4, 5 }`, preview prefix `{ 2, 3, 4, 5, 6, 7, 8, 9 }`, `head_index = 7`, `tail_index = 17`, `total_visible = 10`, `first_window_len = 10`, `second_window_len = 0`, and `wraps = false`, while `runWrappedPreviewReplay()` still yields drained prefix `"hell"`, refill values `{ 200, 201, 202, 203 }`, snapshot prefix `{ 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }`, preview prefix `{ 'o', 0, 1, 2, 3, 4, 5, 6 }`, `head_index = 4`, `tail_index = 4`, `total_visible = 32`, `first_window_len = 28`, `second_window_len = 4`, and `wraps = true`
- occupancy helper checks still hold across lifecycle states: `occupancySummary()` reports `(used=0, available=32, empty=true, full=false, wrapped_window=false)` when cold, `(used=5, available=27)` after enqueuing `"hello"`, full-and-not-wrapped at capacity before a skip, wrapped-and-full after the skip-plus-refill case, and empty again after reset and exit
- ownership and lifetime guards remain explicit: replay helpers reject `.cold`, `init()` rejects a second call, queue-shape replays reject the `.replay_complete` stage, `exit()` clears the queue and moves to `.exited`, post-exit replay attempts still fail closed, and `reset()` clears queue contents without rewinding stage or the `init_runs` and `exit_runs` bookkeeping counters
- does that same helper-facing packet still keep the bounded helper contract explicit: empty-queue peek and skip return `null`, empty enqueue copies `0` bytes, skip-at-capacity returns `0`, `pop-after-reset` returning `null`, draining a three-byte destination from the queued string `"hello"` yields `"hel"`, leaves the remaining prefix `"lo"` queued in order, and follow-up drain on the now-empty queue returns `0`
- `runPreviewBoundaryReplay()` keeps preview truncation stay non-destructive: truncated preview stays non-destructive, `snapshotInto()` still begins with `[2,3,4,5]`, `previewInto()` copies `[2,3,4,5,6,7,8,9]`, reports `10` visible bytes, leaves the queued data intact, and the preview truncation boundary plus preview-boundary replay also held with `snapshot_prefix = {2, 3, 4, 5}`, `preview_prefix = {2, 3, 4, 5, 6, 7, 8, 9}`, `preview_total_visible = 10`, and `queue_len_after_preview = 10`
- `available()` reports `32` at cold, initialized, replay-complete, reset, and exited boundaries, `27` after enqueueing `"hello"`, `22` after the preview-boundary setup, `0` at full capacity`, and `1` immediately after skip-at-capacity`
- `usesWrappedStorageWindow()` stays `false` at cold, initialized, reset, preview-boundary, replay-complete, and full-capacity states, flips `true` only after the skip-at-capacity plus refill rollover cue, and `visibleSpanSummary()` keeps the same bounded split cues reviewers expect from the ring window: `{ first_span_len = 0, second_span_len = 0 }` at cold, initialized, replay-complete, reset, and exited boundaries, `{ 5, 0 }` after enqueueing `"hello"`, `{ 32, 0 }` at full capacity, `{ 31, 0 }` immediately after skip-at-capacity, `{ 31, 1 }` once refill makes the bounded window wrap, the queue-shape replay also held, `usesWrappedStorageWindow()` stayed `false` until the refill-after-skip rollover flipped it `true`, and `runWrappedPreviewReplay()` keeps that same wrapped-window boundary reviewable without mutation too by draining `"hell"`, refilling `{200,201,202,203}`, keeping `previewInto()` at `['o',0,1,2,3,4,5,6]`, holding `available_after_preview` at `0`, and preserving the wrapped `{28,4}` split cue

## Latest verification snapshot

The latest full-packet replay snapshot still preserved in the coupled survey gate remains useful as a compatibility record even though the current direct sample-local replay above now covers six in-file checks.

- `0.17.0-dev.87+9b177a7d2`
- `zig test samples/zigux/bytestream_fifo.zig`
- passed `5/5` sample self-checks
- shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet without relying on a brittle aggregate build-step or test count
- passed `5/5` build steps and `8/8` tests
- `len_after_initial_fill = 15`
- `first_out = "hello"`
- `second_out = {0, 1}`
- `skipped_byte = 2`
- `peek_value = 3`
- `fill_start = 20`
- `fill_end = 42`
- `snapshot_len = 32`
- `snapshot_sequence stayed [3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- `final_len = 32`
- `peek and skip returned null`
- `empty enqueue copied 0 bytes`
- `overflow push was rejected at the 32-byte capacity`
- `skip-at-capacity returned 0`
- `pop-after-reset returned null`
- `cold -> initialized -> replay_complete -> exited`

## Historical packet markers kept for the coupled survey gate

Keep these legacy packet markers visible until `zigux/tests/phase5_bytestream_fifo_survey.zig` is refreshed to the current wording:

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=kfifo-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L01`
- `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`
- `samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea|Phase 5`
- `runtime_atomic64.zig`
- `runtime_atomic64_loader.zig`
- `runtime_bitmap.zig`
- `runtime_bitmap_loader.zig`
- `runtime_kretprobe.zig`
- `runtime_kretprobe_loader.zig`
- `runtime_trace_events.zig`
- `runtime_trace_events_loader.zig`
- `loader-side follow-ons`

## Historical verification snapshot

An older commit-pinned replay snapshot for this bytestream packet remains recorded in prior survey wording, but it should no longer be presented as the only broader current proof now that public-tree readback exposes the companion files again.

Treat earlier references to `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig` as public-tree-backed current packet evidence plus an authenticated-contents-readback gap until a fresh reread proves those exact paths return cleanly through both readback routes.

## Contributor refresh prompts for the current packet

When a contributor updates `samples/zigux/bytestream_fifo.zig` or one of its directly coupled reminder surfaces, keep these prompts explicit:

- does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- does the sample still keep `StorageBacking.embedded_fixed_buffer` explicit so the roadmap-backed idiom remains a bounded fixed-buffer ring instead of an implied allocation-backed runtime queue?
- does `reviewContract().focus` still keep the cue order explicit for `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`?
- do `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()` still keep preview, rollover, and queue-shape evidence visible from the sample file itself?
- if a shared Phase 5 doc, README, or checklist mentions `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig`, did a fresh reread confirm whether that mention is grounded in authenticated connector readback, public-tree blob readback, or both?
- do the docs still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The roadmap gap here is no longer "Zigux still needs a kfifo reference sample." The more precise same-lane gap is:

- the roadmap-backed `kfifo` anchor already has a directly readable sample-root implementation
- current `master` publicly exposes the focused replay, manifest-backed packet, survey replay, and shared `phase5_build.zig` route for that anchor, but authenticated contents readback for those files still fails in this environment
- Phase 5 reminder surfaces therefore need to keep the approved idiom explicit without collapsing that split into either a missing-packet claim or a fully recovered connector-proof claim

So the honest same-lane follow-through is a truthfulness repair: keep this survey aligned with the sample-root file, the public-tree bytestream packet, and the current shared guide surfaces now, and only simplify the wording again if both readback routes converge.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example

- `rg -n "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|Phase 5" Documentation/zigux samples`

2. confirm the direct sample-local surface

- `zig test samples/zigux/bytestream_fifo.zig`

3. confirm broader replay or build-path wording with both authenticated connector readback and public-tree blob readback before claiming the routes are fully recovered

## Non-goals

This survey does not yet claim:

- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- loadable-module wiring or runtime registration support
- lock-contention or blocking semantics

## Next bounded step

Leave the bytestream survey packet parked unless a fresh bytestream-local reread changes one of two bounded facts:

- authenticated connector readback for `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig` starts returning again, so the survey note can collapse back to fully direct wording
- the split between public-tree blob readback and authenticated connector readback stays live and one more bytestream-local truthfulness repair is needed, starting with `zigux/tests/phase5_bytestream_fifo_manifest.json` because its public `surveyed_commit` marker still predates the current survey wording

Do not widen that follow-up into runtime work or broader sample behavior unless the sample-root file itself changes.