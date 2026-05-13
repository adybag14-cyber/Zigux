# Phase 5 Kfifo Sample Survey

This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

* `PHASE5_STATUS=parked-doc-accuracy`
* `PHASE5_LANE_KEY=P5-L01`
* `PHASE5_SURVEYED_COMMIT=00655f9a038c77a0d54f216d69e2a7b5f5355a17`
* `PHASE5_SLICE=kfifo-reference-sample-starter`
* scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, and current bytestream packet truthfulness for the directly readable sample-root contract
* directly readable same-lane surfaces in this run:
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `Documentation/zigux/phase5-sample-review-guide.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`
  * `.github/workflows/zigux-bootstrap.yml`
  * `samples/zigux/bytestream_fifo.zig`
* same-lane readback gaps through the main GitHub connector path in this run:
  * `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase5_bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * `zigux/tests/phase5_bytestream_fifo_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo already ships the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The remaining same-lane job is narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the gap versus the roadmap stated honestly, and avoid treating unavailable shared replay paths as directly readable current-`master` evidence.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 confirmed these same-lane facts:

* `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
* `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.
* the sample file itself already makes the non-runtime idiom reviewable through:
  * `BytestreamFifoSample.descriptor()`
  * `StorageBacking.embedded_fixed_buffer`
  * `reviewContract().focus`
  * `previewInto()`
  * `snapshotInto()`
  * `runPreviewBoundaryReplay()`
  * `runWrappedPreviewReplay()`
  * `visibleSpanSummary()`
  * `usesWrappedStorageWindow()`
  * the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle
* the same run did not directly read back `zigux/tests/phase5_build.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, or `zigux/tests/phase5_bytestream_fifo_survey.zig` through the main GitHub connector path.

That means the honest same-lane posture is:

* the roadmap-backed kfifo sample idiom is already present at the sample-root level
* the remaining gap is shared-packet truthfulness and repeatability visibility, not a missing first sample

## Approved idiom for the landed bytestream FIFO sample

Until a bounded runtime substrate exists, the approved Phase 5 `kfifo` idiom should:

* model FIFO state and ordered operations entirely in memory
* keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`
* keep the Linux anchor path explicit through a descriptor or note
* keep ownership and lifetime boundaries visible through explicit initialization, replay, reset, and teardown states
* keep non-destructive preview and snapshot behavior explicit so reviewers can inspect queued state without inferring hidden mutation
* keep rollover and queue-shape cues explicit through `visibleSpanSummary()` and `usesWrappedStorageWindow()`
* keep helper-boundary behavior explicit at empty, short-drain, full, overflow, skip-at-capacity, and reset edges
* keep procfs, user-copy, locking, and module-registration claims out of scope unless a later runtime lane lands the required substrate first

In practice, the approved idiom is a bounded side-by-side sample, not a claim that Zigux already ships `proc_create()`, `kfifo_from_user()`, `kfifo_to_user()`, or runtime module parity.

## Sample-Visible Checks

The directly readable sample file already makes these checks and cues visible:

* enqueueing `"hello"` plus bytes `0` through `9` yields the expected queue length before draining
* the first drain returns `"hello"`
* the second drain returns bytes `0` and `1`, and those bytes are re-enqueued at the tail
* skipping removes `2`, and peeking then observes `3` without draining it
* the fill loop advances from `20` through `42` and stops at the bounded capacity
* `previewInto()` keeps preview truncation explicit and non-destructive
* `snapshotInto()` captures the full queued anchor sequence before the final drain without mutating queue state
* the final drain preserves the expected Linux-style bytestream order
* empty peek and skip return `null`
* empty enqueue copies `0` bytes
* a short drain of `"hello"` yields `"hel"` and leaves `"lo"` queued in order
* overflow at full capacity is rejected
* `skipByte()` at full capacity returns `0`, reopens one slot, and keeps the later wrap cue reviewable instead of leaving that helper boundary implicit
* a full-capacity preview is non-truncating
* `runPreviewBoundaryReplay()` and `runWrappedPreviewReplay()` keep bounded queue-shape and rollover evidence explicit
* `reset()` clears queue contents without rewinding lifecycle bookkeeping
* the sample stays inside the explicit `cold -> initialized -> replay_complete -> exited` lifecycle

Because the shared bytestream replay packet was not directly readable through the main connector path in this run, this note should keep those exact checks grounded in the sample file that is actually visible today instead of attributing them to absent shared paths.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig`, keep these prompts explicit:

* does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
* does the sample still keep `StorageBacking.embedded_fixed_buffer` explicit so the roadmap-backed idiom remains a bounded fixed-buffer ring instead of an implied allocation-backed runtime queue?
* does `reviewContract().focus` still keep the cue order explicit for `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`?
* do `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()` still keep preview, rollover, and queue-shape evidence visible from the sample file itself?
* does the lifecycle stay explicit through `init()`, `runAnchorReplay()`, `reset()`, and `exit()` instead of leaving ownership review to outside surfaces?
* do helper-boundary checks still keep empty, short-drain, skip-at-capacity, overflow, full-preview, and reset behavior visible from the sample packet?
* if shared Phase 5 docs or tests later mention the bytestream replay packet again, are those references limited to paths that are directly readable on current `master` instead of older or inferred route claims?
* do the docs still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

## Recorded Gap Vs Roadmap

The roadmap gap here is no longer "Zigux still needs a kfifo reference sample." The more precise gap is:

* the roadmap-backed `kfifo` anchor already has a directly readable sample-root implementation
* the approved idiom is reviewable today from the sample file itself
* the broader shared bytestream replay packet was not directly readable through the main connector path in this run, so this survey should not overstate that packet as visible shipped evidence
* Phase 5 still needs its reference-sample wording kept separate from later runtime-family work instead of letting sample language drift toward runtime-substrate claims

So the honest same-lane follow-through is a truthfulness repair: keep the survey aligned with the directly readable sample-root idiom now, and only restate broader shared replay coverage when those paths are directly readable again.

## Latest verification snapshot

This note was refreshed on 2026-05-13 through repo-first current-`master` inspection.

* direct GitHub connector readback confirmed `samples/zigux/bytestream_fifo.zig` and the shared Phase 5 reminder surfaces named above
* the same connector path did not read back `zigux/tests/phase5_build.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, or `zigux/tests/phase5_bytestream_fifo_survey.zig` in this run
* no new local `zig` replay was run for this note-only truthfulness refresh
* validation for this update therefore stays on current-`master` repo inspection and roadmap-aligned wording rather than claiming a fresh end-to-end replay of the broader bytestream packet

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example

* `rg -n "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=00655f9a038c77a0d54f216d69e2a7b5f5355a17|Phase 5" Documentation/zigux samples zigux/tests`

2. confirm the current sample-root surface for this slice

* `find samples/zigux -maxdepth 1 -type f | sort`

3. run the direct sample-local replay when a runnable checkout is available

* `zig test samples/zigux/bytestream_fifo.zig`

## Non-goals

This survey does not yet claim:

* procfs parity
* `kfifo_from_user()` or `kfifo_to_user()` parity
* loadable-module wiring or runtime registration support
* lock-contention or blocking semantics

## Next bounded step

Stay in the Phase 5 samples-and-reference-patterns lane and tighten this survey only if fresh repo inspection changes one of two bounded facts:

* the directly readable sample-root idiom in `samples/zigux/bytestream_fifo.zig`
* the readback availability of the broader bytestream test packet through the main repo path

If the broader bytestream replay packet becomes directly readable again, reintroduce those shared replay references from current evidence rather than from older wording.