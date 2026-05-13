# Phase 5 Kfifo Sample Survey

This note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-narrower-readback-packet`
- `PHASE5_LANE_KEY=P5-L01`
- `PHASE5_SLICE=kfifo-reference-sample-readback`
- scope: keep the bytestream survey note truthful about the exact non-runtime packet that direct readback still exposes on `master`
- current directly reviewed same-lane surfaces in this refresh:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`
  - `samples/zigux/bytestream_fifo.zig`

## Why this slice exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the approved Linux anchors that should make a Zigux idiom reviewable and repeatable.

For this anchor, the repo still exposes the sample-root port itself in `samples/zigux/bytestream_fifo.zig`. The bounded same-lane job for this note is therefore narrower than "write a new sample": keep the approved in-memory FIFO idiom clear, keep the roadmap gap stated honestly, and stop claiming the older focused replay, manifest, survey, or shared build packet as current direct evidence when fresh readback does not return those paths.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 confirmed these same-lane facts:

- `samples/kfifo/bytestream-example.c` remains the Linux anchor for this slice.
- `samples/zigux/bytestream_fifo.zig` is directly readable on current `master`.
- that sample file still makes the non-runtime idiom explicit through `BytestreamFifoSample.descriptor()`, `StorageBacking.embedded_fixed_buffer`, `reviewContract().focus`, `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle.
- the shared Phase 5 guide in `Documentation/zigux/phase5-sample-review-guide.md` and the sample-root summary in `samples/zigux/README.md` already keep this anchor routed through the survey note plus the sample-root file instead of pretending that a broader replay packet is directly readable.
- the same direct readback did not recover these older companion paths:
  - `zigux/tests/phase5_bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - `zigux/tests/phase5_build.zig`

Treat those four paths as current public-tree gaps for this anchor until a fresh reread proves they returned.

That means the honest same-lane posture today is:

- the roadmap-backed kfifo sample idiom is still present at the sample root
- current direct evidence is the sample file plus the shared contributor wording that points back to this survey note
- the older focused replay, manifest-backed packet, survey replay, and shared Phase 5 build route should stay framed as missing readback rather than current proof

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

## Historical verification snapshot

An older commit-pinned replay snapshot for this bytestream packet remains recorded in prior survey wording, but it should no longer be presented as current direct proof while the companion files above are not directly readable on `master`.

Treat any earlier references to `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig` as historical packet evidence only until a fresh reread confirms those exact paths returned.

## Contributor refresh prompts for the current packet

When a contributor updates `samples/zigux/bytestream_fifo.zig` or one of its directly coupled reminder surfaces, keep these prompts explicit:

- does `BytestreamFifoSample.descriptor()` still name `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- does the sample still keep `StorageBacking.embedded_fixed_buffer` explicit so the roadmap-backed idiom remains a bounded fixed-buffer ring instead of an implied allocation-backed runtime queue?
- does `reviewContract().focus` still keep the cue order explicit for `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`?
- do `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()` still keep preview, rollover, and queue-shape evidence visible from the sample file itself?
- if a shared Phase 5 doc, README, or checklist mentions `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig`, did a fresh reread confirm those exact paths first?
- do the docs still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The roadmap gap here is no longer "Zigux still needs a kfifo reference sample." The more precise same-lane gap is:

- the roadmap-backed `kfifo` anchor already has a directly readable sample-root implementation
- current `master` does not directly expose the older focused replay, manifest-backed packet, survey replay, or shared `phase5_build.zig` route for that anchor
- Phase 5 reminder surfaces therefore need to keep the sample-root-only readback posture explicit instead of repeating older broader packet claims

So the honest same-lane follow-through is a truthfulness repair: keep this survey aligned with the sample-root file and the current shared guide surfaces now, and only widen it again if the missing companion paths return.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example

- `rg -n "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|Phase 5" Documentation/zigux samples`

2. confirm the direct sample-local surface

- `zig test samples/zigux/bytestream_fifo.zig`

3. confirm any broader replay or build-path wording only after a fresh reread of the exact companion paths above

## Non-goals

This survey does not yet claim:

- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- loadable-module wiring or runtime registration support
- lock-contention or blocking semantics

## Next bounded step

Leave the bytestream survey packet parked unless a fresh bytestream-local reread changes one of two bounded facts:

- one or more of `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig` return and the survey note should restore broader direct-readback wording
- another shared reminder surface still presents one of those missing paths as directly readable and needs one more lane-local truthfulness repair

Do not widen that follow-up into runtime work or broader sample behavior unless the sample-root file itself changes.