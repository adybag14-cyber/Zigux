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
  - omission readback for `zigux/tests/README.md`
  - `samples/zigux/bytestream_fifo.zig`
  - public-tree blob readback for `zigux/tests/phase5_bytestream_fifo.zig`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - public-tree blob readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - public-tree blob readback for `zigux/tests/phase5_build.zig`

## Why this slice exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo still exposes the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The bounded same-lane job for this note is therefore narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the roadmap gap stated honestly, and stop collapsing the broader focused replay, manifest, survey, or shared build packet into either "fully direct connector proof" or "missing from `master`" when fresh readback now splits across those two paths.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-18 confirmed these same-lane facts:

- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.
- that sample file still keeps the non-runtime ownership rule explicit through `BytestreamFifoSample.descriptor()`, `StorageBacking.embedded_fixed_buffer`, the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle, `reviewContract().focus`, and the explicit non-goal list.
- the sample-root file currently carries three in-file self-checks: the anchor replay test keeps the exact final drain ordering, the `reviewContract().focus` order, and the fixed-buffer storage backing directly visible at the sample root; a second direct check keeps preview truncation and the wrapped `{ 28, 4 }` visible-span split reviewable; and a third direct check keeps remaining-capacity transitions, the short-drain `"hel"` / `"lo"` helper boundary, and the post-exit replay rejection visible at the sample root.
- the broader exact behavior packet is still reviewable through public-tree blob readback for `zigux/tests/phase5_bytestream_fifo.zig`, which currently carries four focused replay tests for lane scoping, transfer counts, helper boundaries, queue-shape boundaries, preview behavior, and lifecycle guards.
- the manifest-backed packet remains directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`.
- the survey packet remains publicly visible through `zigux/tests/phase5_bytestream_fifo_survey.zig`, which currently carries four survey-packet checks that keep this note, the manifest, and the split-readback wording aligned.
- the shared review path still runs through `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, the directly readable manifest companion, the public-tree `zigux/tests/phase5_bytestream_fifo.zig` focused replay, the public-tree `zigux/tests/phase5_bytestream_fifo_survey.zig` survey gate, and the public-tree `zigux/tests/phase5_build.zig` route, while `zigux/tests/README.md` currently stays a tests-root omission readback rather than a bytestream-specific review surface.
- authenticated GitHub contents reads in this environment still do not recover `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig`, so reminder surfaces should describe the split readback honestly instead of calling those files absent or pretending the connector path already recovered them all.

That means the honest same-lane posture today is:

- the roadmap-backed kfifo sample idiom is still present at the sample root
- the ownership rule remains non-runtime and fixed-buffer-backed
- the sample-root file itself now exposes three direct self-checks
- the tests-root guide currently contributes only an omission readback for this packet, while the remaining cross-file replay, survey-truthfulness, and shared-build companion checks stay reviewable through the focused replay packet, the survey packet, and the public-tree Phase 5 build route
- current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so this bytestream packet must not be used to imply bitmap-side sample delivery or reopen the separate later-phase runtime bitmap family

## Approved idiom for the current bytestream sample

Until a bounded runtime substrate exists, the approved Phase 5 `kfifo` idiom should:

- model FIFO state and ordered operations entirely in memory
- keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`
- keep the Linux anchor path explicit through a descriptor or note
- keep ownership and lifetime boundaries visible through explicit initialization, replay, reset, and teardown states
- keep non-destructive preview and snapshot behavior explicit so reviewers can inspect queued state without inferring hidden mutation
- keep rollover and queue-shape cues explicit through `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()`
- keep helper-boundary behavior explicit at empty, short-drain, full, overflow, skip-at-capacity, and reset edges
- keep bitmap helper or runtime bitmap claims out of this packet; current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample
- keep procfs, user-copy, locking, and module-registration claims out of scope unless a later runtime lane lands the required substrate first

In practice, the approved idiom remains a bounded side-by-side sample, not a claim that Zigux already ships `proc_create()`, `kfifo_from_user()`, `kfifo_to_user()`, or runtime module parity.

## Exact checks verified on 2026-05-18

Fresh direct sample readback plus current public-tree replay readback on 2026-05-18 showed this exact check split on current `master`:

- `samples/zigux/bytestream_fifo.zig` currently carries three in-file self-checks, and those direct sample-root checks now prove the anchor replay sequence, the fixed-buffer storage backing, the ten-item `reviewContract().focus` order, `runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`, the wrapped `{ 28, 4 }` visible-span split, `runRemainingCapacityReplay()` with `available_after_hello = 27` and `available_after_partial_drain = 8`, the short-drain `"hel"` / `"lo"` helper boundary, and invalid post-exit replay rejection.
- `zigux/tests/phase5_bytestream_fifo.zig` currently carries four focused replay tests, which keep these exact checks explicit:
  - the lane contract stays non-runtime and keeps `requires_runtime_substrate = false`, `provides_selfcheck = true`, and the four non-goals explicit
  - `runAnchorReplay()` still keeps the Linux-style transfer counts explicit: `initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, and `requeue_count = 2`
  - the helper boundary still shows that draining `"hello"` into a three-byte buffer yields `"hel"`, leaves `"lo"` queued, and a follow-up drain on the empty queue returns `0`
  - the queue-shape and preview packet still keeps `runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`, preview prefix `{ 2, 3, 4, 5, 6, 7, 8, 9 }`, `queue_len_after_preview = 10`, and `available_after_preview = 22`, while `runWrappedPreviewReplay()` preserves the wrapped `{ 28, 4 }` visible-span split without mutating queue state
  - the lifecycle boundary still rejects replay before `init()`, records the `cold`, `initialized`, `replay_complete`, and `exited` stages explicitly, and fail-closes invalid post-exit re-entry
- `zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries four survey-packet checks, which keep this note aligned with the manifest, the split-readback wording, the strengthened sample-root self-check story, and the current exact-check snapshot.

## Ownership rule

The current ownership rule is still the bounded one this lane is supposed to protect:

- `StorageBacking.embedded_fixed_buffer` is the only declared storage backing
- `init()` and `exit()` define the lifetime edges explicitly
- `reset()` clears queue contents without turning the sample into a runtime-owned object
- no procfs, user-copy, locking, or module-registration surface is claimed

That ownership posture is still the reason this sample belongs in the Phase 5 non-runtime packet rather than a later runtime lane.