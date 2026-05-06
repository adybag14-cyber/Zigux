# Phase 10 Virtio Ring Slice

This document tracks the first bounded `drivers/virtio/virtio_ring.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-lab-helper`
- scope: queue index bounds, descriptor-count validation, split or packed layout metadata, avail and used index bookkeeping, used-buffer polling, callback re-enable bookkeeping, delayed-callback pacing bookkeeping, broken-queue discipline, reset-readiness preflight bookkeeping, notify-prepare accounting, dedicated Phase 10 ring tests, the shared Phase 10 core/input/MMIO packet guards, the shared reset-queue, driver-id, and input status-drain replays, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_ring.zig`
  - `zigux/tests/phase10_virtio_ring.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap puts virtqueue wrappers ahead of MMIO work and explicitly names `drivers/virtio/virtio_ring.c` as the next core anchor after `drivers/virtio/virtio.c`.

The live repo already had a survey lane that made the queue-wrapper gap explicit. This slice lands the smallest honest follow-on: a lab-only helper that records queue shape, used-buffer polling, callback re-enable state, broken-queue discipline, reset-readiness preflight, and notification bookkeeping in memory without pretending to own DMA mapping, real descriptor memory, or interrupt delivery.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_ring.c`
- bounded queue registration by queue index with power-of-two descriptor-count checks
- split versus packed layout metadata plus event-idx and indirect-descriptor intent flags
- avail index shadow bookkeeping for published descriptor chains
- bounded outstanding-chain accounting that prevents lab queue overflow
- used-buffer polling that reports only newly consumed chains since the last in-memory poll
- callback disable and re-enable bookkeeping that reports when the driver should poll for already-consumed chains
- delayed-callback pacing bookkeeping that mirrors the bounded `virtqueue_enable_cb_delayed()` threshold shape without claiming interrupt delivery or event-index writes
- broken-queue discipline that rejects fresh publish, kick-preparation, queue-local polling, and callback re-enable snapshots until the lab queue is cleared again
- reset-readiness preflight bookkeeping that reports whether `resetQueue()` is safe and, if not, names the exact queue-local blocker before any transport-facing reset claim
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

2. run the Linux-style replay routes
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates keep the ring helper reviewable through the direct build replay plus the shipped `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, and `scripts/zigux/check-phase10-mmio-packet.py` guards, the shared `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` replays, and the Linux-style `make -C zigux phase10-test` plus `make -C zigux phase10` routes.

## Next bounded step

The queue-local ring lane should stay parked unless current head reveals another directly coupled truthfulness repair inside this same packet. The new reset-readiness preflight closes the last honest queue-only follow-up before the still-blocked MMIO lifecycle, IRQ, queue-discovery, and reset packet.