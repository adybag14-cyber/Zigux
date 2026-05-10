# Phase 10 Virtio Ring Slice
This document tracks the first bounded `drivers/virtio/virtio_ring.c` lab helper under Phase 10.
## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-lab-helper`
- scope: queue index bounds, descriptor-count validation, split or packed layout metadata, avail and used index bookkeeping, used-buffer polling, callback re-enable bookkeeping, delayed-callback pacing bookkeeping, broken-queue discipline, reset-readiness preflight bookkeeping, notify-prepare accounting, the dedicated ring helper replay, the committed ring survey manifest and survey gate, the dedicated ring packet review guard, the dedicated ring verify replay, and the shared Phase 10 build-and-make routes
- product boundary:
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `drivers/virtio/virtio_ring.zig`
  - `drivers/virtio/virtio_ring_verify.zig`
  - `zigux/tests/phase10_virtio_ring.zig`
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `scripts/zigux/check-phase10-ring-packet.py`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
## Why this slice exists
The Phase 10 roadmap puts virtqueue wrappers ahead of MMIO work and explicitly names `drivers/virtio/virtio_ring.c` as the next core anchor after `drivers/virtio/virtio.c`.
The live repo already had a survey lane that made the queue-wrapper gap explicit. This slice records the smallest honest landed follow-on: a lab-only helper that records queue shape, used-buffer polling, callback re-enable state, broken-queue discipline, reset-readiness preflight, and notification bookkeeping in memory without pretending to own DMA mapping, real descriptor memory, or interrupt delivery while keeping the survey-backed review packet explicit.
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
- an adjacent manifest-backed survey-and-checker packet: `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_build.zig`, and `make -C zigux phase10` keep the queue-local wrapper packet reviewable together
## Non-goals
This slice does not yet claim:
- real split-ring or packed-ring descriptor memory layout parity
- DMA map or unmap wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle parity
- `virtio_mmio.c` transport glue
## Gates
1. run the dedicated ring packet review guard
   - `python3 scripts/zigux/check-phase10-ring-packet.py --self-test`
   - `python3 scripts/zigux/check-phase10-ring-packet.py`
2. run the dedicated ring helper replay
   - `zig test zigux/tests/phase10_virtio_ring.zig`
3. run the dedicated ring survey gate
   - `zig test zigux/tests/phase10_virtio_ring_survey.zig`
4. run the dedicated Phase 10 build
   - `zig build test --build-file zigux/tests/phase10_build.zig`
5. run the convenience target
   - `make -C zigux phase10`
## Next bounded step
Keep the queue-local ring lane parked unless current head reveals another directly coupled slice-note, survey-note, manifest, checker, verify-replay, or helper-test truthfulness repair inside this same packet. Do not widen into MMIO lifecycle, IRQ, queue-discovery, or reset packet work without fresh reopen evidence.
