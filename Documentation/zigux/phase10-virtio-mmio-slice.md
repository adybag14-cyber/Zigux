# Phase 10 Virtio MMIO Slice

This document tracks the bounded `drivers/virtio/virtio_mmio.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-config-write-helper`
- scope: bounded MMIO register offsets, device-feature page selection, driver-feature page writes, queue-select and queue-size planning, queue-ready bookkeeping, queue-notify snapshots, version-scoped queue-address planning, read-only config-window snapshots, in-memory config-write planning, status and reset bookkeeping, config-generation tracking, interrupt-status acknowledge bookkeeping, dedicated Phase 10 MMIO tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary transport anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo now has the virtio core, ring, and input lab footholds plus the earlier MMIO survey lane. This slice now records the next honest follow-on after the config-window helper: an in-memory config-write planning helper that keeps previous and planned byte, halfword, and word values reviewable against the current config-generation while leaving the underlying config window unchanged and without pretending to own full config-space parity, queue setup, shared interrupt delivery, probe and remove lifecycle, or DMA-facing transport work.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_mmio.c`
- bounded register-offset constants for the device-features, driver-features, guest-page-size, queue-select, queue-size, queue-ready, queue-notify, queue-address, interrupt, status, and config-generation window
- device-feature page selection and readback for the low and high 32-bit feature pages
- driver-feature page selection and write bookkeeping for the same bounded two-page feature window
- queue selection and queue-register summaries for a tiny in-memory queue window
- queue-size planning that rejects zero, unavailable, and out-of-range queue sizes and refuses resize while the selected queue is already ready
- queue-ready writes that require a configured queue size first and stay in-memory only
- queue-notify snapshots that require a configured ready queue, return the selected queue identity, and count in-memory notify events without claiming device-side side effects
- version-scoped queue-address planning that records either legacy guest-page-size, queue-align, and queue-PFN values or modern DESC, AVAIL, and USED addresses while the queue is configured but not yet ready
- read-only config-window snapshots that return a bounded byte, halfword, or word from a tiny in-memory config window together with the current config-generation
- in-memory config-write planning that records previous and planned byte, halfword, and word values for bounded config-window updates while leaving the underlying config window unchanged and without claiming device-side application
- explicit status writes that reject reset-through-the-wrong-path and keep reset on its own helper branch
- dedicated reset bookkeeping that clears in-memory queue size, queue ready state, queue notify counts, and queue-address planning state without claiming queue teardown parity
- in-memory config-generation snapshots and increment bookkeeping
- interrupt-status bookkeeping plus bounded interrupt acknowledge behavior for the reviewable queue and config interrupt bits only
- dedicated Phase 10 tests and build wiring for the helper

## Non-goals

This slice does not yet claim:

- real MMIO pointer reads or writes
- queue setup and teardown parity
- full queue-address programming side effects across legacy PFN or modern DESC, AVAIL, and USED windows
- full config-space write parity or device-side application through `VIRTIO_MMIO_CONFIG`
- full config-field parity across the broader transport surface
- probe, remove, freeze, restore, or command-line device creation parity
- DMA-facing virtqueue setup, teardown, or interrupt delivery

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Leave the MMIO lane parked unless a future inspection can split `phase10-mmio-lifecycle-and-irq-paths` into a smaller transport-safe observation helper without claiming queue setup, IRQ delivery, probe, or remove parity.
