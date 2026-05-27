# Phase 5 Kfifo Sample Survey

This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-direct-sample-and-tests-packet`
- `PHASE5_LANE_KEY=P5-L01`
- `PHASE5_SLICE=kfifo-reference-sample-readback`
- scope: keep the bytestream survey note truthful about the exact non-runtime packet that current `master` exposes through authenticated connector readback while keeping the shared build route framed truthfully as a directly readable shared companion inside the same bounded packet
- current directly reviewed same-lane surfaces in this refresh:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/check-phase5-review-guide-surface.py`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/bytestream_fifo.zig`
  - `samples/zigux/bytestream_fifo_window_contract.zig`
  - `samples/zigux/bytestream_fifo_transfer_contract.zig`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo.zig`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - authenticated contents readback for `zigux/tests/phase5_build.zig`

## Why this slice exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo still exposes the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The bounded same-lane job for this note is therefore narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the roadmap gap stated honestly, and stop collapsing the broader focused replay, transfer companion, manifest, survey, or shared build packet into either "fully missing from `master`" or an over-narrow sample-only story when fresh authenticated readback now restores the direct sample-plus-tests packet, the direct transfer-contract companion, the focused transfer replay, and the shared build route instead of leaving any of them stranded in stale companion-only wording.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-25 confirmed these same-lane facts:

- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.
- that sample file still keeps the non-runtime ownership rule explicit through `BytestreamFifoSample.descriptor()`, `StorageBacking.embedded_fixed_buffer`, the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle, `reviewContract().focus`, and the explicit non-goal list.
- the sample-root file currently carries four in-file self-checks: the anchor replay test keeps the exact final drain ordering, the `reviewContract().focus` order, and the fixed-buffer storage backing directly visible at the sample root; a second direct check now keeps both `runPreviewBoundaryReplay()` and `runWrappedPreviewReplay()` explicit together with preview truncation and the wrapped `{ 28, 4 }` visible-span split; a third direct check keeps reinit, second replay, and post-second-exit rejection visible at the sample root through `runReinitBoundaryReplay()` and its `init_runs` / `exit_runs` accounting; and a fourth direct check keeps `runRemainingCapacityReplay()` plus `runPartialEnqueueBoundaryReplay()`, `occupancySummary()`, `writableSpanSummary()`, `lifecycleSummary()`, the short-drain `\"hel\"` / `\"lo\"` helper boundary, and the partial `enqueueSlice()` truncation boundary with only two slots left visible at the sample root.
- the shipped sample-root companion `samples/zigux/bytestream_fifo_window_contract.zig` is directly readable on current `master`, and its three in-file checks keep the stable two-window visible-span and writable-span reference pattern explicit, then add named checkpoint lookups through `checkpointName()`, `visibleWindowForCheckpoint()`, and `writableWindowForCheckpoint()` so later focused replays do not have to rely on positional array indexes alone.
- the shipped sample-root companion `samples/zigux/bytestream_fifo_transfer_contract.zig` is directly readable on current `master`, and its three in-file checks keep the Linux-style transfer counts, preview prefix, short-drain helper boundary, partial `enqueueSlice()` truncation, fixed-buffer backing, and non-runtime posture explicit beside the sample root rather than leaving that transfer packet implicit in broader queue-shape wording alone.
- the broader exact behavior packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo.zig`, which currently carries five focused replay tests for lane scoping, transfer counts, helper boundaries, queue-shape boundaries, preview behavior, lifecycle guards, explicit reinit-after-exit reuse, and partial `enqueueSlice()` truncation at the last two slots.
- the focused transfer replay is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig`, which currently keeps the Linux-style transfer packet, the short-drain helper boundary, and the bounded enqueue truncation cues explicit outside the sample-owned companion.
- the manifest-backed packet remains directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`.
- the survey packet is now directly readable through authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`, which currently carries five survey-packet checks that keep this note, the manifest, and the direct sample-plus-tests wording aligned.
- the shared review path still runs through `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, the directly readable manifest companion, the directly readable focused replay packet, the directly readable focused transfer replay, the directly readable survey gate, and the directly readable `zigux/tests/phase5_build.zig` route. That shared build route now reruns the sample-owned self-check suite, the window-contract companion, the transfer-contract companion, the focused replay packet, the focused transfer replay, and the survey gate together instead of stopping short of the sample-owned transfer cues.
- authenticated GitHub contents reads in this environment now recover `zigux/tests/phase5_build.zig` directly again, so reminder surfaces should keep that shared build path framed as current direct packet evidence instead of demoting it back to companion-only wording or collapsing it into a missing-packet story.

That means the honest same-lane posture today is:

- the roadmap-backed kfifo sample idiom is still present at the sample root
- the ownership rule remains non-runtime and fixed-buffer-backed
- the sample-root file itself now exposes four direct self-checks
- the sample-root window-contract companion now keeps the stable two-window visible and writable reference pattern explicit and adds named checkpoint lookups for those same bounded windows
- the sample-root transfer-contract companion now keeps the Linux-style transfer packet, helper boundary, bounded enqueue truncation, fixed-buffer backing, and non-runtime posture explicit at the sample root
- the directly readable focused replay packet, focused transfer replay, manifest companion, survey gate, shared build companion, shipped review-guide checker, scripts-root reminder, and tests-root guide now keep the broader bytestream review packet explicit together on the direct-readback side
- current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so this bytestream packet must not be used to imply bitmap-side sample delivery or reopen the separate later-phase runtime bitmap family

## Approved idiom for the current bytestream sample

Until a bounded runtime substrate exists, the approved Phase 5 `kfifo` idiom should:

- model FIFO state and ordered operations entirely in memory
- keep storage backing explicit as a fixed embedded ring through `StorageBacking.embedded_fixed_buffer`
- keep the Linux anchor path explicit through a descriptor or note
- keep ownership and lifetime boundaries visible through explicit initialization, replay, reset, and teardown states
- keep non-destructive preview and snapshot behavior explicit so reviewers can inspect queued state without inferring hidden mutation
- keep remaining-capacity, rollover, occupancy, and queue-shape cues explicit through `runRemainingCapacityReplay()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()`
- keep the shipped two-window contract cues explicit through `samples/zigux/bytestream_fifo_window_contract.zig`
- keep the shipped queue-window companion addressable by name through `checkpointName()`, `visibleWindowForCheckpoint()`, and `writableWindowForCheckpoint()` so later focused replays can point at the preview, wrapped-full, and partial-drain checkpoints directly instead of only by array slot
- keep the shipped transfer-contract cues explicit through `samples/zigux/bytestream_fifo_transfer_contract.zig`, `referencePattern()`, the Linux-style transfer counts, the preview prefix, the short-drain helper boundary, the bounded `enqueueSlice()` truncation summary, fixed-buffer backing, and the non-runtime posture instead of leaving those transfer cues implicit in the broader sample root alone
- keep the direct `available()` helper explicit as the first remaining-capacity cue at cold, initialized, preview, wrapped, full, replay-complete, reset, and exited boundaries instead of leaving free-space review to derived queue-length math alone
- keep helper-boundary behavior explicit at empty, short-drain, partial-`enqueueSlice()`-truncation, full, overflow, skip-at-capacity, reset, and reinit-after-exit edges
- keep bitmap helper or runtime bitmap claims out of this packet; current `master` still has no standalone `samples/zigux/*bitmap*` Phase 5 reference sample
- keep procfs, user-copy, locking, and module-registration claims out of scope unless a later runtime lane lands the required substrate first

In practice, the approved idiom remains a bounded side-by-side sample, not a claim that Zigux already ships `proc_create()`, `kfifo_from_user()`, `kfifo_to_user()`, or runtime module parity.

## Exact checks verified on 2026-05-25

Fresh direct sample and tests readback on 2026-05-25 showed this exact packet on current `master`:

- `samples/zigux/bytestream_fifo.zig` currently carries four in-file self-checks, and those direct sample-root checks now prove the anchor replay sequence, the fixed-buffer storage backing, the ten-item `reviewContract().focus` order, `runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`, the wrapped `{ 28, 4 }` visible-span split, the reinit path through `runReinitBoundaryReplay()` with `init_runs_after_reinit = 2` and `exit_runs_after_second_exit = 2`, `runRemainingCapacityReplay()` with `available_after_hello = 27` and `available_after_partial_drain = 8`, `runPartialEnqueueBoundaryReplay()` with `requested_extra_len = 4`, `copied_extra_len = 2`, and `dropped_extra_len = 2`, the short-drain `\"hel\"` / `\"lo\"` helper boundary, and invalid post-exit replay rejection.
- `samples/zigux/bytestream_fifo_window_contract.zig` currently carries three direct companion checks, which keep `referencePattern().visible_windows`, `referencePattern().writable_windows`, `preview_is_non_destructive`, `wrapped_preview_is_non_destructive`, `rollover_refill_required_for_wrap`, `visible_windows_never_exceed_two`, and `writable_windows_never_exceed_two` explicit at the sample root while also proving `checkpointName()`, `visibleWindowForCheckpoint()`, and `writableWindowForCheckpoint()` still line up with the same preview, wrapped-full, and partial-drain checkpoints.
- `samples/zigux/bytestream_fifo_transfer_contract.zig` currently carries three direct companion checks, which keep `referencePattern().initial_string_copy_count`, `len_after_initial_fill`, `first_drain`, `second_drain`, `requeue_count`, `preview_prefix`, `short_drain_prefix`, `short_drain_remainder`, `partial_enqueue_requested_len`, `partial_enqueue_copied_len`, `partial_enqueue_dropped_len`, `full_queue_rejects_overflow`, `sample_remains_non_runtime`, `sample_provides_selfcheck`, and `fixed_buffer_storage` explicit at the sample root while also proving those transfer cues still align with the shipped `BytestreamFifoSample` anchor replay and bounded partial-enqueue replay.
- `zigux/tests/phase5_bytestream_fifo.zig` currently carries five focused replay tests, which keep these exact checks explicit:
  - the lane contract stays non-runtime and keeps `requires_runtime_substrate = false`, `provides_selfcheck = true`, and the four non-goals explicit
  - `runAnchorReplay()` still keeps the Linux-style transfer counts explicit: `initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, and `requeue_count = 2`
  - the helper boundary still shows that draining `\"hello\"` into a three-byte buffer yields `\"hel\"`, leaves `\"lo\"` queued, and a follow-up drain on the empty queue returns `0`, while `runPartialEnqueueBoundaryReplay()` keeps partial `enqueueSlice()` truncation explicit by proving a four-byte request at the last two slots copies exactly `{ 30, 31 }`, drops the trailing two requested bytes, and leaves the queue full without wrapping
  - the queue-shape and preview packet still keeps `runPreviewBoundaryReplay()` at snapshot prefix `{ 2, 3, 4, 5 }`, preview prefix `{ 2, 3, 4, 5, 6, 7, 8, 9 }`, `queue_len_after_preview = 10`, and `available_after_preview = 22`, while `occupancySummary()` keeps that preview state explicit at `queue_len = 10`, `available = 22`, and `wrapped = false`, `writableSpanSummary()` keeps the same preview boundary explicit at `tail_index = 17`, `writable_count = 22`, `first_window_len = 15`, `second_window_len = 7`, and `wraps = true`, `runWrappedPreviewReplay()` preserves the wrapped `{ 28, 4 }` visible-span split without mutating queue state, and the wrapped-full plus partial-drain follow-through keeps `occupancySummary()` explicit at `queue_len = 32`, `available = 0`, `wrapped = true` and then `queue_len = 24`, `available = 8`, `wrapped = true` while `writableSpanSummary()` moves to `tail_index = 4`, `writable_count = 0`, `first_window_len = 0`, `second_window_len = 0`, and then `tail_index = 1`, `writable_count = 8`, `first_window_len = 8`, `second_window_len = 0` after the partial drain
  - the lifecycle boundary still rejects replay before `init()`, records the `cold`, `initialized`, `replay_complete`, and `exited` stages explicitly, and fail-closes invalid post-exit re-entry
  - the reinit boundary still proves `runReinitBoundaryReplay()` can exit the first replay, restore an empty queue at full availability, replay the exact final drain sequence a second time, and finish with `init_runs = 2` and `exit_runs = 2`
- `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig` currently carries two focused replay tests, which keep the Linux-style transfer packet, the preview prefix, the short-drain helper boundary, partial `enqueueSlice()` truncation, fixed-buffer backing, and the non-runtime posture explicit outside the sample-owned companion alone.
- `zigux/tests/phase5_bytestream_fifo_survey.zig` currently carries five survey-packet checks, which keep this note aligned with the manifest, the restored direct sample-plus-tests wording, the strengthened sample-root self-check story, the named checkpoint companion step, the transfer-contract companion, the focused transfer replay, and the current exact-check snapshot.
- `zigux/tests/phase5_build.zig` is directly readable through authenticated contents readback again and now reruns the sample-owned self-check route, the window-contract companion, the transfer-contract companion, the focused replay packet, the focused transfer replay, and the survey gate together, so keep it framed as the current direct shared build-route companion instead of understating it as sample-selfcheck plus focused-replay-only wiring.

## Ownership rule

The current ownership rule is still the bounded one this lane is supposed to protect:

- `StorageBacking.embedded_fixed_buffer` is the only declared storage backing
- `init()` and `exit()` define the lifetime edges explicitly
- `reset()` clears queue contents without turning the sample into a runtime-owned object
- `runReinitBoundaryReplay()` keeps repeatable reuse explicit without promoting the sample into a runtime-owned registration surface
- no procfs, user-copy, locking, or module-registration surface is claimed

That ownership posture is still the reason this sample belongs in the Phase 5 non-runtime packet rather than a later runtime lane.

## Contributor checklist

When a contributor updates `samples/zigux/bytestream_fifo.zig` or one of its directly coupled reminder surfaces, keep these packet-local prompts explicit here instead of relying on the broader shared guides alone:

- does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c`, keep `requires_runtime_substrate = false`, keep `provides_selfcheck = true`, and keep `StorageBacking.embedded_fixed_buffer` as the only storage backing so the packet stays in the non-runtime Phase 5 lane?
- do `runAnchorReplay()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `runRemainingCapacityReplay()`, `runPartialEnqueueBoundaryReplay()`, `runReinitBoundaryReplay()`, `samples/zigux/bytestream_fifo_window_contract.zig`, `samples/zigux/bytestream_fifo_transfer_contract.zig`, and `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig` still describe the same bounded packet across the sample root, focused replay files, manifest-backed contract, dedicated survey gate, and shared reminder surfaces?
- do the named queue-window companion helpers still stay aligned too, so `checkpointName()`, `visibleWindowForCheckpoint()`, and `writableWindowForCheckpoint()` continue to point at the same preview, wrapped-full, and partial-drain checkpoints already fixed in `referencePattern()`?
- do the transfer-contract cues still stay aligned too, so `referencePattern()`, the Linux-style transfer counts, the preview prefix, the short-drain helper boundary, partial `enqueueSlice()` truncation, fixed-buffer backing, and the non-runtime posture continue to match the sample-owned anchor replay and bounded partial-enqueue replay already fixed in the companion and focused transfer replay?
- do the direct validation routes stay explicit too: `zig test samples/zigux/bytestream_fifo.zig` should stay visible as the sample-owned self-check route, `zig test samples/zigux/bytestream_fifo_window_contract.zig` should stay visible as the queue-window companion route, `zig test samples/zigux/bytestream_fifo_transfer_contract.zig` should stay visible as the transfer-contract companion route, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig` should stay visible as the equivalent direct focused replay route, `zig test --dep bytestream_fifo_transfer_contract -Mroot=zigux/tests/phase5_bytestream_fifo_transfer_contract.zig -Mbytestream_fifo_transfer_contract=samples/zigux/bytestream_fifo_transfer_contract.zig` should stay visible as the focused transfer replay route, `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` should stay visible as the survey-packet guard, and the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` line should stay visible as the current direct shared build route that reruns the sample-owned self-check route, the window-contract companion, the transfer-contract companion, the focused replay packet, the focused transfer replay, and the survey guard together rather than being demoted back to companion-only wording?
- if a shared reminder surface mentions the bytestream packet, does it keep `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/bytestream_fifo.zig`, `samples/zigux/bytestream_fifo_window_contract.zig`, `samples/zigux/bytestream_fifo_transfer_contract.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit while keeping `zigux/tests/phase5_build.zig` framed as current direct shared build evidence?
- do the docs still keep runtime bitmap or other helper-family claims out of this bytestream packet instead of treating it as proof of standalone `*bitmap*`, `*printf*`, `*vsprintf*`, `*cmdline*`, `*argv*`, `*rbtree*`, or runtime-owned sample delivery?

## Next bounded step

Leave the direct bytestream sample-plus-tests packet parked unless a future reread finds a new one-file same-lane reminder drift:

- if a shared README, guide, checklist, or dedicated guide-surface checker later stops naming the restored direct bytestream packet, its transfer-contract companion, its focused transfer replay, or underdescribes the sample-root preview, window-contract, helper-boundary replays, or the named queue-window companion step, repair only that one file
- if a shared reminder surface later understates the now-direct `zigux/tests/phase5_build.zig` route again, refresh only that one same-lane reminder so the shared build evidence stays truthful without widening sample behavior
- otherwise leave the bytestream packet parked while the sample root, transfer-contract companion, focused replay files, manifest-backed contract, survey gate, and shared reminder surfaces stay aligned