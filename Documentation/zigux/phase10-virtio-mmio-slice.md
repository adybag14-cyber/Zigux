# Phase 10 Virtio MMIO Slice

This document tracks the first bounded `drivers/virtio/virtio_mmio.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-lab-helper`
- scope: identity-register reads, one bounded device-feature selector and read window, one bounded transport-backed config-word window, queue-selected register reads, queue_num_max and queue_num bookkeeping, queue_ready bookkeeping, helper-local status and config-generation bookkeeping, helper-local interrupt-status staging, dedicated Phase 10 MMIO tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap puts virtqueue wrappers ahead of MMIO work, but it also names `drivers/virtio/virtio_mmio.c` as the next transport-facing anchor after the earlier core, ring, and lab-driver footholds.

The live repo already had a survey lane that made the MMIO gap explicit. This slice records the smallest honest landed follow-on: a lab-only helper that exposes a bounded queue-selected register window, queue size bookkeeping, one device-feature selector and read window, one small transport-backed config-word window, and helper-local status or generation bookkeeping without pretending to own interrupt acknowledgement, reset flows, or probe lifecycle behavior.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_mmio.c`
- in-memory reads for the MMIO identity registers
- one bounded device-feature selector plus in-memory `device_features` read window
- one bounded transport-backed config-word read window rooted at the MMIO config-space base offset
- queue-selected reads for `queue_num_max`, `queue_num`, and `queue_ready`
- bounded queue selection with queue-count range checks
- bounded queue-size programming that rejects zero, non-power-of-two, oversized, and above-maximum queue counts
- helper-local status writes, helper-local config-generation bumps, and helper-local interrupt-status staging for VM-friendly validation
- register-window validation that rejects unaligned, unsupported, and out-of-window offsets plus writes to read-only MMIO registers
- dedicated Phase 10 tests and shared build wiring for the helper

## Non-goals

This slice does not yet claim:

- transport-backed config-space writes
- interrupt acknowledgement
- reset flows
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Keep the Phase 10 MMIO lane focused on review-surface truthfulness and other tightly coupled helper validation before widening into interrupt acknowledgement, queue discovery, reset paths, or probe lifecycle work.
