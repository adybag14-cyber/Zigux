# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records what has now landed plus the remaining queue-wrapper gap against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter with queue callback bookkeeping, descriptor-shape metadata, and notification accounting. This survey started by making the missing ring-helper gap explicit, and it now records that the first `drivers/virtio/virtio_ring.zig` lab slice has landed without pretending queue lifecycle parity is complete.

## Survey findings

- `drivers/virtio/virtio_ring.c` is present on `master` at 3940 lines and spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_build.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`, and that core slice now covers queue callback bookkeeping, descriptor-shape metadata, and notification accounting.
- the current Zigux VirtIO surface now includes a bounded `drivers/virtio/virtio_ring.zig` helper for queue registration, layout metadata, outstanding-chain accounting, and notify-prepare bookkeeping.
- the live repo still does not model real descriptor tables, DMA helpers, interrupt callbacks, or transport-backed queue reset semantics.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule still points to another tiny in-memory ring helper next, such as callback-enable state or used-buffer polling, not MMIO or DMA work.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-survey-note`
- the landed `phase10-virtqueue-shape-helper`
- the ready-next `phase10-shared-virtqueue-layout-helper`
- the landed `phase10-virtio-ring-slice-note`
- the still-blocked `phase10-mmio-wrapper-lane`

This keeps the lane concrete and reviewable without overstating `virtio_ring` progress: the queue-shape foothold is real, the core-side queue metadata is already landed, and the risky transport-facing work is still intentionally blocked.

## Non-goals

This survey slice does not yet claim:

- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- `virtio_mmio.c` transport glue

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 virtio ring lane and add one tiny used-buffer polling or callback-enable helper next inside `drivers/virtio/virtio_ring.zig`, still in memory only, before any MMIO or DMA-facing work.
