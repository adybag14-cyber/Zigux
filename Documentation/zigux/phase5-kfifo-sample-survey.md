# Phase 5 Kfifo Sample Survey

This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-direct-sample-and-tests-packet`
- `PHASE5_LANE_KEY=P5-L01`
- `PHASE5_SLICE=kfifo-reference-sample-readback`
- scope: keep the bytestream survey note truthful about the exact non-runtime packet that current `master` exposes through authenticated connector readback while keeping the shared build route framed as public-tree-backed companion evidence
- current directly reviewed same-lane surfaces in this refresh:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/check-phase5-review-guide-surface.py`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/bytestream_fifo.zig`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo.zig`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - public-tree blob readback for `zigux/tests/phase5_build.zig`

## Why this slice exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo still exposes the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The bounded same-lane job for this note is therefore narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the roadmap gap stated honestly, and stop collapsing the broader focused replay, manifest, survey, or shared build packet into either "fully missing from `master`" or an over-narrow sample-only story when fresh authenticated readback now restores the direct sample-plus-tests packet while the shared build route still sits on the public-tree-backed side.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-19 confirmed these same-lane facts:

- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.
- that sample file still keeps the non-runtime ownership rule explicit through `BytestreamFifoSample.descriptor()`, `StorageBacking.embedded_fixed_buffer`, the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle, `reviewContract().focus`, and the explicit non-goal list.
- the sample-root file currently carries three in-file self-checks: the anchor replay test keeps the exact final drain ordering, the `reviewContract().focus` order, and the fixed-buffer storage backing directly visible at the sample root; a second direct check keeps preview truncation and the wrapped `{ 28, 4 }` visible-span split reviewable; and a third direct check keeps remaining-capacity transitions, the short-drain `"hel"` / `"lo"` helper boundary, and the post-exit replay rejection visible at the sample root.
- the broader exact behavior packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo.zig`, which currently carries four focused replay tests for lane scoping, transfer counts, helper boundaries, queue-shape boundaries, preview behavior, and lifecycle guards.
- the manifest-backed packet remains directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`.
- the survey packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`, which currently carries four survey-packet checks that keep this note, the manifest, and the direct sample-plus-tests wording aligned.
- the shared review path still runs through `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, the directly readable manifest companion, the directly readable focused replay packet, the directly readable survey gate, and the public-tree `zigux/tests/phase5_build.zig` route.
- authenticated GitHub contents reads in this environment still do not recover `zigux/tests/phase5_build.zig`, so reminder surfaces should keep that shared build path framed as public-tree-backed companion evidence instead of calling it directly readable or collapsing it into a missing-packet story.

That means the honest same-lane posture today is:

- the roadmap-backed kfifo sample idiom is still present at the sample root
- the ownership rule remains non-runtime and fixed-buffer-backed
- the sample-root file itself now exposes three direct self-checks
- the directly readable focused replay packet, manifest companion, survey gate, shipped review-guide checker, scripts-root reminder, and tests-root guide now keep the broader bytestream review packet explicit while the shared build companion stays on the public-tree-backed side
- current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so this bytestream packet must not be used to imply bitmap-side sample delivery or reopen the separate later-phase runtime bitmap family

## Approved idiom for the current bytestream sample

Until a bounded runtime substrate exists, the approved Phase 5 `kfifo` idiom should:

- model FIFO state and ordered operations entirely in memory
- keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`
- keep the Linux anchor path explicit through a descriptor or note
- keep ownership and lifetime boundaries visible through explicit initialization, replay, reset, and teardown states
- keep non-destructive preview and snapshot behavior explicit so reviewers can inspect queued state without inferring hidden mutation
- keep remaining-capacity, rollover, occupancy, and queue-shape cues explicit through `runRemainingCapacityReplay()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()`
- keep helper-boundary behavior explicit at empty, short-drain, full, overflow, skip-at-capacity, and reset edges
- keep bitmap helper or runtime bitmap claims out of this packet; current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample
- keep procfs, user-copy, locking, and module-registration claims out of scope unless a later runtime lane lands the required substrate first

In practice, the approved idiom remains a bounded side-by-side sample, not a claim that Zigux already ships `proc_create()`, `kfifo_from_user()`, `kfifo_to_user()`, or runtime module parity.

## Exact checks verified on 2026-05-19

Fresh direct sample and tests readback on 2026-05-19 showed this exact packet on current `master`:

- `samples/zigux/bytestream_fifo.zig` currently carries three in-file self-checks, and those direct sample-root checks now prove the anchor replay sequence, the fixed-buffer storage backing, the ten-item `reviewContract().focus` order, `runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`, the wrapped `{ 28, 4 }` visible-span split, `runRemainingCapacityReplay()` with `available_after_hello = 27` and `available_after_partial_drain = 8`, the short-drain `"hel"` / `"lo"` helper boundary, and invalid post-exit replay rejection.
- `zigux/tests/phase5_bytestream_fifo.zig` currently carries four focused replay tests, which keep these exact checks explicit:
  - the lane contract stays non-runtime and keeps `requires_runtime_substrate = false`, `provides_selfcheck = true`, and the four non-goals explicit
  - `runAnchorReplay()` still keeps the Linux-style transfer counts explicit: `initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, and `requeue_count = 2`
  - the helper boundary still shows that draining `"hello"` into a three-byte buffer yields `"hel"`, leaves `"lo"` queued, and a follow-up drain on the empty queue returns `0`
  - the queue-shape and preview packet still keeps `runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`, preview prefix `{ 2, 3, 4, 5, 6, 7, 8, 9 }`, `queue_len_after_preview = 10`, and `available_after_preview = 22`, while `occupancySummary()` keeps that preview state explicit at `queue_len = 10`, `available = 22`, and `wrapped = false`, `writableSpanSummary()` keeps the same preview boundary explicit at `tail_index = 17`, `writable_count = 22`, `first_window_len = 15`, `second_window_len = 7`, and `wraps = true`, `runWrappedPreviewReplay()` preserves the wrapped `{ 28, 4 }` visible-span split without mutating queue state, and the wrapped-full plus partial-drain follow-through keeps `occupancySummary()` explicit at `queue_len = 32`, `available = 0`, `wrapped = true` and then `queue_len = 24`, `available = 8`, `wrapped = true` while `writableSpanSummary()` moves to `tail_index = 4`, `writable_count = 0`, `first_window_len = 0`, `second_window_len = 0`, `wraps = false` at wrapped-full and then `tail_index = 1`, `writable_count = 8`, `first_window_len = 8`, `second_window_len = 0`, `wraps = false` after the partial drain
  - the lifecycle boundary still rejects replay before `init()`, records the `cold`, `initialized`, `replay_complete`, and `exited` stages explicitly, and fail-closes invalid post-exit re-entry
- `zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries four survey-packet checks, which keep this note aligned with the manifest, the restored direct sample-plus-tests wording, the strengthened sample-root self-check story, and the current exact-check snapshot.
- `zigux/tests/phase5_build.zig` remains useful shared build-route support material, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.

## Ownership rule

The current ownership rule is still the bounded one this lane is supposed to protect:

- `StorageBacking.embedded_fixed_buffer` is the only declared storage backing
- `init()` and `exit()` define the lifetime edges explicitly
- `reset()` clears queue contents without turning the sample into a runtime-owned object
- no procfs, user-copy, locking, or module-registration surface is claimed

That ownership posture is still the reason this sample belongs in the Phase 5 non-runtime packet rather than a later runtime lane.