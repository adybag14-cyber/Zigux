# Phase 10 Virtio Ring Slice

This document tracks the first bounded `drivers/virtio/virtio_ring.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-lab-helper`
- scope: queue index bounds, descriptor-count validation, split or packed layout metadata, avail and used index bookkeeping, used-buffer polling, callback re-enable bookkeeping, delayed-callback pacing bookkeeping, broken-queue poll guarding, notify-prepare accounting, dedicated Phase 10 ring tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_ring.zig`
  - `zigux/tests/phase10_virtio_ring.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap puts virtqueue wrappers ahead of MMIO work and explicitly names `drivers/virtio/virtio_ring.c` as the next core anchor after `drivers/virtio/virtio.c`.

The live repo already had a survey lane that made the queue-wrapper gap explicit. This slice lands the smallest honest follow-on: a lab-only helper that records queue shape, used-buffer polling, callback re-enable state, broken-queue poll discipline, and notification bookkeeping in memory without pretending to own DMA mapping, real descriptor memory, or interrupt delivery.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_ring.c`
- bounded queue registration by queue index with power-of-two descriptor-count checks
- split versus packed layout metadata plus event-idx and indirect-descriptor intent flags
- avail index shadow bookkeeping for published descriptor chains
- bounded outstanding-chain accounting that prevents lab queue overflow
- used-buffer polling that reports only newly consumed chains since the last in-memory poll
- callback disable and re-enable bookkeeping that reports when the driver should poll for already-consumed chains
- delayed-callback pacing bookkeeping that mirrors the bounded `virtqueue_enable_cb_delayed()` threshold shape without claiming interrupt delivery or event-index writes
- broken-queue guards that reject queue-local polling and callback re-enable snapshots until the lab queue is cleared again
- kick-prepare notification bookkeeping that mirrors the smallest reviewable `num_added` flow from `virtio_ring.c`
- used-chain accounting that drains outstanding lab work without touching real transport paths
- dedicated Phase 10 tests and build wiring for the helper

## Non-goals

This slice does not yet claim:

- real split-ring or packed-ring descriptor memory layout parity
- DMA map or unmap wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle parity
- `virtio_mmio.c` transport glue

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

The queue-local ring lane no longer owns another honest helper-sized follow-up inside `virtio_ring.zig`. The remaining same-family step is the adjacent survey-backed `virtio_mmio` lifecycle, IRQ, queue-discovery, and reset packet, which stays blocked on risky transport and Architecture Council reopen rather than on another queue-local ring helper.
