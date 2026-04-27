# Phase 10 Virtio MMIO Slice

This document tracks the first bounded `drivers/virtio/virtio_mmio.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-register-window-helper`
- scope: bounded MMIO register offsets, device-feature page selection, driver-feature page writes, status and reset bookkeeping, config-generation tracking, interrupt-status acknowledge bookkeeping, dedicated Phase 10 MMIO tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary transport anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo now has the virtio core, ring, and input lab footholds plus the earlier MMIO survey lane. This slice lands the first honest follow-on: an in-memory register-window helper that models only the smallest reviewable MMIO surface from `virtio_mmio.c` without pretending to own queue setup, probe and remove lifecycle, or DMA-facing transport work.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_mmio.c`
- bounded register-offset constants for the device-features, driver-features, interrupt, status, and config-generation window
- device-feature page selection and readback for the low and high 32-bit feature pages
- driver-feature page selection and write bookkeeping for the same bounded two-page feature window
- explicit status writes that reject reset-through-the-wrong-path and keep reset on its own helper branch
- in-memory config-generation snapshots and increment bookkeeping
- interrupt-status bookkeeping plus bounded interrupt acknowledge behavior for the reviewable queue and config interrupt bits only
- dedicated Phase 10 tests and build wiring for the helper

## Non-goals

This slice does not yet claim:

- real MMIO pointer reads or writes
- queue selection, queue size, ready-state, or notify register parity
- config-space reads or writes through `VIRTIO_MMIO_CONFIG`
- probe, remove, freeze, restore, or command-line device creation parity
- DMA-facing virtqueue setup, teardown, or interrupt delivery

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 MMIO lane and add one small queue-register planning helper next, most likely around queue select, queue size bounds, and ready-state bookkeeping, without widening into probe, remove, DMA, or full interrupt-handler paths.
