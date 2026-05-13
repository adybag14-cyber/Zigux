# Phase 5 Kfifo Sample Survey

This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

* `PHASE5_STATUS=verified-sample-packet`
* `PHASE5_LANE_KEY=P5-L01`
* `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`
* `PHASE5_SLICE=kfifo-reference-sample-starter`
* scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, and current bytestream packet truthfulness for the directly readable shared review packet
* directly reviewed same-lane surfaces in this refresh:
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `samples/zigux/bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * `zigux/tests/phase5_bytestream_fifo_survey.zig`
  * `zigux/tests/phase5_build.zig`
* review gate marker:
  * `samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea|Phase 5`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo already ships the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The remaining same-lane job is narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the gap versus the roadmap stated honestly, and keep the shared manifest-backed review packet aligned with the landed bytestream sample instead of leaving stale note drift behind.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 confirmed these same-lane facts:

* `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
* `samples/zigux/bytestream_fifo.zig` is directly reviewable on current `master`.
* the shared bytestream packet is also reviewable through `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig`.
* the sample file itself still makes the non-runtime idiom explicit through `BytestreamFifoSample.descriptor()`, `StorageBacking.embedded_fixed_buffer`, `reviewContract().focus`, `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle.
* the focused replay `zigux/tests/phase5_bytestream_fifo.zig` still keeps the replay-visible transfer counts, preview markers, queue-shape helpers, short-drain boundary, and ownership-and-lifetime packet explicit beside the sample-root self-check.
* the shared docs-root, sample-root, scripts-root, and tests-root contributor packet still points at this exact bytestream FIFO slice so the landed review surface does not collapse back to the sample file and survey note alone.

That means the honest same-lane posture is:

* the roadmap-backed kfifo sample idiom is already present at the sample-root level
* the manifest-backed survey packet and focused replay are part of the shipped Phase 5 review surface
* the remaining gap is to keep note wording synchronized with the current sample, focused replay, and survey gate instead of letting an older readback-limited snapshot drift forward

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

## Sample-visible checks

The directly readable sample and shared packet already make these checks and cues visible:

* enqueueing `"hello"` plus bytes `0` through `9` yields the expected queue length before draining
* the first drain returns `"hello"`
* the second drain returns bytes `0` and `1`, and those same bytes are re-enqueued at the tail
* initial string copy count is `5`, first drain count is `5`, second drain count is `2`, and requeue count is `2`
* skipping removes `2`, and peeking then observes `3` without draining it
* the fill loop advances from `20` through `42` and stops at the bounded capacity
* `previewInto()` keeps preview truncation explicit and non-destructive
* `snapshotInto()` captures the full queued anchor sequence before the final drain without mutating queue state
* the final drain preserves the expected Linux-style bytestream order
* the approved in-memory FIFO idiom still keeps queue-shape evidence explicit so `available()` and `usesWrappedStorageWindow()` stay aligned with the `visibleSpanSummary()` split cues across the same cold, full, and rollover boundaries that reviewers expect from a bounded ring sample
* sample-behavior changes update the manifest-backed replay contract instead of leaving reviewers to infer it from code alone
* docs and tests still keep procfs, user-copy, locking, and runtime registration out of scope for this Phase 5 sample

## Helper-boundary contract

The helper-facing sample packet still keeps the boundary behavior reviewable instead of leaving it implicit:

* empty-queue peek and skip return `null`
* empty enqueue copies `0` bytes
* skip-at-capacity returns `0`
* `pop-after-reset` returning `null` stays explicit after reset clears queue contents
* draining a three-byte destination from the queued string `\"hello\"` yields `\"hel\"`
* leaves the remaining prefix `\"lo\"` queued in order
* follow-up drain on the now-empty queue returns `0`
* does that same helper-facing packet still keep the bounded helper contract explicit after each note refresh and survey-gate change

## Preview and queue-shape boundaries

The note and survey packet keep preview and rollover evidence explicit:

* `runPreviewBoundaryReplay()` keeps preview truncation stay non-destructive and makes the preview truncation boundary directly reviewable
* truncated preview stays non-destructive
* `snapshotInto()` still begins with `[2,3,4,5]`
* `previewInto()` copies `[2,3,4,5,6,7,8,9]`
* reports `10` visible bytes
* leaves the queued data intact
* the preview-boundary replay also held with `snapshot_prefix = {2, 3, 4, 5}`, `preview_prefix = {2, 3, 4, 5, 6, 7, 8, 9}`, `preview_total_visible = 10`, and `queue_len_after_preview = 10`

The queue-shape packet also stays explicit:

* `available()` reports `32` at cold, initialized, replay-complete, reset, and exited boundaries
* `27` after enqueueing `"hello"`
* `22` after the preview-boundary setup
* `0` at full capacity
* `1` immediately after skip-at-capacity
* `usesWrappedStorageWindow()` stays `false` at cold, initialized, reset, preview-boundary, replay-complete, and full-capacity states
* flips `true` only after the skip-at-capacity plus refill rollover cue
* `visibleSpanSummary()` keeps the same bounded split cues reviewers expect from the ring window
* `{ first_span_len = 0, second_span_len = 0 }` at cold, initialized, replay-complete, reset, and exited boundaries
* `{ 5, 0 }` after enqueueing `"hello"`
* `{ 32, 0 }` at full capacity
* `{ 31, 0 }` immediately after skip-at-capacity
* `{ 31, 1 }` once refill makes the bounded window wrap
* the queue-shape replay also held
* `usesWrappedStorageWindow()` stayed `false` until the refill-after-skip rollover flipped it `true`
* `runWrappedPreviewReplay()` keeps that same wrapped-window boundary reviewable without mutation too
* draining `"hell"`, refilling `{200,201,202,203}`
* keeping `previewInto()` at `['o',0,1,2,3,4,5,6]`
* `available_after_preview` at `0`
* preserving the wrapped `{28,4}` split cue

## Latest verification snapshot

A focused replay for the recorded `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea` packet was re-run on 2026-05-05 using Zig `0.17.0-dev.87+9b177a7d2`.

This snapshot is commit-pinned to `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`; newer unrelated `master` commits should not be read as automatically re-verified unless this note, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` move together.

Verification recorded for that replay packet:

* `zig test samples/zigux/bytestream_fifo.zig` passed `5/5` sample self-checks
* `zigux/tests/phase5_bytestream_fifo.zig` remains the focused replay surface paired with that sample-root self-check and the shared `zigux/tests/phase5_build.zig` route
* the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet still exists through the Phase 5 build, Makefile, and workflow wiring without relying on a brittle aggregate build-step or test count
* `len_after_initial_fill = 15`
* `first_out = "hello"`
* `second_out = {0, 1}`
* `skipped_byte = 2`
* `peek_value = 3`
* `fill_start = 20`
* `fill_end = 42`
* `snapshot_len = 32`
* `snapshot_sequence stayed [3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
* `final_len = 32`
* `peek and skip returned null`
* `peek and skip returned `null``
* `empty enqueue copied 0 bytes`
* `empty enqueue copied `0` bytes`
* `overflow push was rejected at the 32-byte capacity`
* `skip-at-capacity returned `0``
* `pop-after-reset returned `null``
* the lifecycle stayed `cold -> initialized -> replay_complete -> exited`
* `visibleSpanSummary()` stayed `{ 0, 0 }` at cold, initialized, replay-complete, reset, and exited boundaries
* moved to `{ 5, 0 }` after `"hello"`
* `{ 32, 0 }` at full capacity
* `{ 31, 0 }` after skip-at-capacity
* `{ 31, 1 }` after the refill rollover
* `usesWrappedStorageWindow()` stayed `false` until the refill-after-skip rollover flipped it `true`
* the wrapped-preview replay also held
* `runWrappedPreviewReplay()` drained `"hell"`
* kept `previewInto()` at `['o', 0, 1, 2, 3, 4, 5, 6]`
* preserved the wrapped `{ 28, 4 }` split without mutating queue state

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig`, keep these prompts explicit:

* does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
* does the sample still keep `StorageBacking.embedded_fixed_buffer` explicit so the roadmap-backed idiom remains a bounded fixed-buffer ring instead of an implied allocation-backed runtime queue?
* does `reviewContract().focus` still keep the cue order explicit for `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`?
* do `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()` still keep preview, rollover, and queue-shape evidence visible from the sample file itself?
* does `zigux/tests/phase5_bytestream_fifo.zig` still keep the focused replay packet explicit beside the sample-root self-check and the shared `zigux/tests/phase5_build.zig` route?
* does the lifecycle stay explicit through `init()`, `runAnchorReplay()`, `reset()`, and `exit()` instead of leaving ownership review to outside surfaces?
* do helper-boundary checks still keep empty, short-drain, skip-at-capacity, overflow, full-preview, and reset behavior visible from the sample packet?
* if shared Phase 5 docs or tests later mention the bytestream replay packet again, do they stay commit-pinned and current instead of falling back to older connector-gap wording?
* do the docs still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The roadmap gap here is no longer "Zigux still needs a kfifo reference sample." The more precise gap is:

* the roadmap-backed `kfifo` anchor already has a directly readable sample-root implementation
* the approved idiom is reviewable today from the sample file plus the shared manifest-backed survey packet and focused replay surface
* Phase 5 still needs its reference-sample wording kept separate from later runtime-family work instead of letting sample language drift toward runtime-substrate claims

So the honest same-lane follow-through is a truthfulness repair: keep the survey aligned with the sample-root and shared replay packet now, and only widen if a new bytestream sample change lands first.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example

* `rg -n "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea|Phase 5" Documentation/zigux samples zigux/tests`

2. confirm the direct sample-local replay

* `zig test samples/zigux/bytestream_fifo.zig`

3. confirm the shared Phase 5 route remains wired

* `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

* procfs parity
* `kfifo_from_user()` or `kfifo_to_user()` parity
* loadable-module wiring or runtime registration support
* lock-contention or blocking semantics

## Next bounded step

Leave the bytestream survey packet parked unless `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or this note drifts again. If it reopens, compare those five surfaces first and only then decide whether the next honest move is another note-only refresh or a separate manifest or survey-gate tighten.