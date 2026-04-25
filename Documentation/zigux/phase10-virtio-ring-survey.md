# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records the remaining queue-wrapper gap against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter with queue callback bookkeeping, yet it still has no `drivers/virtio/virtio_ring.zig` slice, no dedicated `virtio_ring` survey artifact, and no queue-wrapper note that compares the repo state directly against the roadmap. This survey makes that gap explicit without pretending queue lifecycle parity has landed.

## Survey findings

- `drivers/virtio/virtio_ring.c` is present on `master` at 3940 lines and spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_build.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`.
- the current Zigux VirtIO surface still stops at lab-only status negotiation and bounded queue callback registration. It does not yet model queue descriptors, ring memory layout, notify prepare, used-buffer polling, or transport-backed queue reset semantics.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule still points to a small queue-shape helper as the next honest step inside Phase 10.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-survey-note`
- the ready-next `phase10-virtqueue-shape-helper`
- the ready-next `phase10-shared-virtqueue-layout-helper`
- the still-blocked `phase10-mmio-wrapper-lane`

This keeps the lane concrete and reviewable without overstating `virtio_ring` progress.

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

Stay in the Phase 10 virtio ring lane and add one tiny `drivers/virtio/virtio_ring.zig` queue-shape helper next, focused on queue index, descriptor-count bounds, and notification bookkeeping only, before any MMIO or DMA-facing work.
