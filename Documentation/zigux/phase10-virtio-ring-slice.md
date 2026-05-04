# Phase 10 Virtio Ring Slice

This document tracks the bounded queue-discipline packet around `drivers/virtio/virtio_ring.c` under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-lab-helper`
- scope: queue index bounds, descriptor-count validation, split or packed layout metadata, avail and used index bookkeeping, used-buffer polling, callback disable and re-enable bookkeeping, callback enable-prepare snapshots, delayed-callback pacing bookkeeping, notify-prepare accounting with rollover flushing, queue-reset guard and drained-queue reset bookkeeping, drained broken-queue recovery bookkeeping, dedicated Phase 10 ring tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_ring.zig`
  - `zigux/tests/phase10_virtio_ring.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap puts virtqueue wrappers ahead of MMIO work and explicitly names `drivers/virtio/virtio_ring.c` as the next core anchor after `drivers/virtio/virtio.c`.

The live repo already had a survey lane that made the queue-wrapper gap explicit. This slice now records the landed queue-local packet: a lab-only helper that covers queue shape, used-buffer polling, callback disable and re-enable state, callback enable-prepare snapshots, notification bookkeeping with rollover flushing, drained-queue reset discipline, and drained broken-queue recovery discipline in memory without pretending to own DMA mapping, real descriptor memory, or interrupt delivery.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_ring.c`
- bounded queue registration by queue index with power-of-two descriptor-count checks
- split versus packed layout metadata plus event-idx and indirect-descriptor intent flags
- avail index shadow bookkeeping for published descriptor chains
- bounded outstanding-chain accounting that prevents lab queue overflow
- used-buffer polling that reports only newly consumed chains since the last in-memory poll
- callback disable and re-enable bookkeeping that reports when the driver should poll for already-consumed chains
- callback enable-prepare snapshots that keep the bounded `virtqueue_enable_cb_prepare()` plus `virtqueue_poll()` race check reviewable without transport-backed callbacks
- delayed-callback pacing bookkeeping that mirrors the bounded `virtqueue_enable_cb_delayed()` threshold shape without claiming interrupt delivery or event-index writes
- kick-prepare notification bookkeeping that mirrors the smallest reviewable `num_added` flow from `virtio_ring.c` and flushes pending notify work before the 16-bit counter wraps silently
- queue-reset guard bookkeeping that refuses resets while unpublished descriptor chains, outstanding used work, or unpolled completions still remain
- drained-queue reset bookkeeping that clears live avail, used, callback, and notify state while preserving queue shape metadata for reuse
- broken-queue recovery that only reuses drained queues through the existing reset discipline and clears the broken marker without claiming real transport reset, descriptor reclamation, or IRQ delivery
- used-chain accounting that drains outstanding lab work without touching real transport paths
- dedicated Phase 10 tests and build wiring for the helper

The same parked ring packet also participates in the shared closure evidence bundle through `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, and `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, so the current review path is broader than the dedicated ring test alone even though the landed helper surface remains queue-local.

## Ownership handoff

- this slice owns only the queue-local review packet around `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and the two ring notes
- the still-blocked transport-facing follow-up `phase10-mmio-lifecycle-and-irq-paths` stays owned by the adjacent MMIO packet in `zigux/tests/phase10_virtio_mmio_manifest.json` plus `Documentation/zigux/phase10-virtio-mmio-slice.md` and `Documentation/zigux/phase10-virtio-mmio-survey.md`
- shared closure evidence remains the owner of the cross-slice scoreboard, freeze-boundary posture, and combined validation route; this ring note should not be used to reopen MMIO, IRQ, or lifecycle claims on its own

## Non-goals

This slice does not yet claim:

- real split-ring or packed-ring descriptor memory layout parity
- DMA map or unmap wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle parity
- `virtio_mmio.c` transport glue

## Gates

1. run the shared closure inventory gate
- `python3 scripts/zigux/check-phase10-closure-inventory.py`

2. run the shared closure validation path
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

4. run the convenience target
- `make -C zigux phase10`

## Next bounded step

The queue-local ring lane now covers the smallest honest reset-discipline, broken-queue-recovery, and notify-rollover steps as well, and the adjacent MMIO packet owns the remaining `phase10-mmio-lifecycle-and-irq-paths` blocker. Do not reopen `virtio_ring.zig` for more speculative in-memory queue work; leave this packet parked unless a future Phase 10 review can split that MMIO-owned blocker into a smaller transport-safe observation helper without widening the ring slice.
