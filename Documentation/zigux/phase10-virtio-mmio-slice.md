# Phase 10 Virtio MMIO Slice

This document tracks the bounded `drivers/virtio/virtio_mmio.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-queue-notify-helper`
- scope: bounded MMIO register offsets, device-feature page selection, driver-feature page writes, queue-select and queue-size planning, queue-ready bookkeeping, queue-notify snapshots, status and reset bookkeeping, config-generation tracking, interrupt-status acknowledge bookkeeping, dedicated Phase 10 MMIO tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary transport anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo now has the virtio core, ring, and input lab footholds plus the earlier MMIO survey lane. This slice lands the next honest follow-on after the queue-register helper: an in-memory queue-notify snapshot that models only the smallest reviewable notify surface from `virtio_mmio.c` without pretending to own queue-address programming, shared interrupt delivery, probe and remove lifecycle, or DMA-facing transport work.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_mmio.c`
- bounded register-offset constants for the device-features, driver-features, queue-select, queue-size, queue-ready, queue-notify, interrupt, status, and config-generation window
- device-feature page selection and readback for the low and high 32-bit feature pages
- driver-feature page selection and write bookkeeping for the same bounded two-page feature window
- queue selection and queue-register summaries for a tiny in-memory queue window
- queue-size planning that rejects zero, unavailable, and out-of-range queue sizes and refuses resize while the selected queue is already ready
- queue-ready writes that require a configured queue size first and stay in-memory only
- queue-notify snapshots that require a configured ready queue, return the selected queue identity, and count in-memory notify events without claiming device-side side effects
- explicit status writes that reject reset-through-the-wrong-path and keep reset on its own helper branch
- dedicated reset bookkeeping that clears in-memory queue size, queue ready state, and queue notify counts without claiming queue teardown parity
- in-memory config-generation snapshots and increment bookkeeping
- interrupt-status bookkeeping plus bounded interrupt acknowledge behavior for the reviewable queue and config interrupt bits only
- dedicated Phase 10 tests and build wiring for the helper

## Non-goals

This slice does not yet claim:

- real MMIO pointer reads or writes
- queue-address register programming for legacy PFN or modern DESC, AVAIL, and USED windows
- queue setup and teardown parity
- config-space reads or writes through `VIRTIO_MMIO_CONFIG`
- probe, remove, freeze, restore, or command-line device creation parity
- DMA-facing virtqueue setup, teardown, or interrupt delivery

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 MMIO lane and add one small version-scoped queue-address planning helper next around legacy PFN versus modern DESC, AVAIL, and USED register windows without widening into probe, remove, DMA, or full interrupt-handler paths.
