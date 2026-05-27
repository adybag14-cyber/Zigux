# Phase 5 Kfifo Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 `kfifo` packet truthful when shared reviewer surfaces need to mention the bounded FIFO idiom that current `master` actually approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 `kfifo` anchor is still:

- `samples/kfifo/bytestream-example.c`

Fresh mixed reread on 2026-05-27 keeps the current non-runtime Zigux packet directly readable through these same-lane surfaces:

- `Documentation/zigux/phase5-kfifo-approved-idiom-gap.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/bytestream_fifo_window_contract.zig`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`
- `zigux/tests/phase5_build.zig`

Keep that packet framed as current direct sample-plus-reminder evidence rather than as proof that the broader Linux sample already has procfs, user-copy, locking, or module-registration parity.

## Approved idiom gap versus the roadmap

The roadmap asks Phase 5 to make approved Zigux idioms reviewable and repeatable for the named Linux sample anchors.

For `kfifo`, current `master` does meet that goal in a bounded way, but only through an in-memory bytestream sample. The approved idiom gap is therefore not "missing sample file" anymore. The real gap is that the landed sample still stops short of runtime-facing Linux parity and should keep saying so explicitly.

Keep the approved idiom bounded to this current landed posture:

- the queue is modeled entirely in memory
- `BytestreamFifoSample.descriptor()` keeps the Linux anchor path explicit
- `StorageBacking.embedded_fixed_buffer` stays the only storage backing
- the lifecycle stays bounded to `init()` -> replay helpers -> `exit()`
- preview, snapshot, remaining-capacity, queue-shape, and wraparound cues stay reviewable without hidden mutation
- the window-shape companion in `samples/zigux/bytestream_fifo_window_contract.zig` stays part of the approved review packet rather than an optional extra

The still-open roadmap gap is everything this packet intentionally does not claim:

- no `proc_create()` parity
- no `kfifo_from_user()` parity
- no `kfifo_to_user()` parity
- no locking, wait-queue, or runtime-owned registration story
- no promotion into the separate Phase 9 runtime family

## Exact approved cues to preserve

When Phase 5 reminder surfaces mention the `kfifo` anchor, keep these direct cues explicit:

- `samples/zigux/bytestream_fifo.zig` keeps the direct sample-root owner for the bounded packet
- `runAnchorReplay()` keeps ordered enqueue, drain, and wraparound replay visible
- `runPreviewBoundaryReplay()` and `runWrappedPreviewReplay()` keep non-destructive preview plus the wrapped visible-span split explicit
- `runRemainingCapacityReplay()` keeps `available()` and queue-shape reviewable without reducing the packet to queue-length math alone
- `runPartialEnqueueBoundaryReplay()` keeps short-capacity truncation explicit at the last two slots
- `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()` keep the queue-window contract reviewable
- `samples/zigux/bytestream_fifo_window_contract.zig` keeps the stable two-window visible and writable reference pattern explicit
- `zigux/tests/phase5_build.zig` stays shared rerun evidence for this packet rather than sample-local proof

## Review boundary

Current `master` still ships no standalone Phase 5 `samples/zigux/*bitmap*`, `*printf*`, `*vsprintf*`, `*cmdline*`, `*argv*`, `*rbtree*`, or broad `*format*` reference sample through this packet.

Use this note only to restate the approved bounded `kfifo` idiom inside the roadmap-backed Phase 5 anchor. Do not treat it as proof of:

- runtime bitmap delivery
- helper-family sample delivery outside the bytestream packet
- user-copy parity
- procfs parity
- locking parity
- module-registration parity

## Next bounded step

Leave this note parked unless a fresh reread shows that a shared Phase 5 reminder surface still talks about the `kfifo` anchor as if the sample were fully missing, or as if the landed bytestream packet already proved runtime-facing Linux parity. The next honest same-lane follow-through is a small reminder-surface alignment repair, not a broader behavior expansion.
