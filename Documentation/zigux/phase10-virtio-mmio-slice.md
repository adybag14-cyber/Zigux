# Phase 10 Virtio MMIO Slice

This document tracks the first bounded `drivers/virtio/virtio_mmio.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-lab-helper`
- scope: identity-register reads, one bounded device-feature selector and read window, one bounded transport-backed config-word window, one bounded config-word write planning summary, one bounded config-write disposition summary, one bounded probe-preflight summary, queue-selected register reads, queue_num_max and queue_num bookkeeping, queue_ready bookkeeping, helper-local status and config-generation bookkeeping, helper-local interrupt-status staging, dedicated Phase 10 MMIO tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
  - `scripts/zigux/check-phase10-mmio-packet.py`

## Why this slice exists

The Phase 10 roadmap puts virtqueue wrappers ahead of MMIO work, but it also names `drivers/virtio/virtio_mmio.c` as the next transport-facing anchor after the earlier core, ring, and lab-driver footholds.

The live repo already had a survey lane that made the MMIO gap explicit. This slice records the smallest honest landed follow-on: a lab-only helper that exposes a bounded queue-selected register window, queue size bookkeeping, one device-feature selector and read window, one small transport-backed config-word window, one config-word write planning summary, one config-write disposition summary for that prepared word window, one probe-preflight summary for the earliest `virtio_mmio_probe()`-style checks, and helper-local status or generation bookkeeping without pretending to own interrupt acknowledgement, reset flows, queue discovery, or probe lifecycle behavior.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_mmio.c`
- in-memory reads for the MMIO identity registers
- one bounded device-feature selector plus in-memory `device_features` read window
- one bounded transport-backed config-word read window rooted at the MMIO config-space base offset
- one bounded config-word write planning summary that reports the current generation, previous word value, and planned value without mutating the staged config window
- one bounded config-write disposition summary that reports the absolute end of the prepared config-word window plus a changed-byte mask without mutating the staged config window
- one bounded probe-preflight summary that keeps the earliest `virtio_mmio_probe()`-style checks reviewable through magic and version constants, device presence, vendor presence, legacy guest-page-size intent, bounded queue-register readiness, and interrupt-ack readiness
- queue-selected reads for `queue_num_max`, `queue_num`, and `queue_ready`
- bounded queue selection with queue-count range checks
- bounded queue-size programming that rejects zero, non-power-of-two, oversized, and above-maximum queue counts
- helper-local status writes, helper-local config-generation bumps, and helper-local interrupt-status staging for VM-friendly validation
- register-window validation that rejects unaligned, unsupported, and out-of-window offsets plus writes to read-only MMIO registers
- dedicated Phase 10 tests and shared build wiring for the helper

## Ownership Handoff

This MMIO slice owns only driver-local lab slices and shared validation gates for the landed register, feature-word, config-window, config-write planning, config-write disposition, probe-preflight, queue-size, status, generation, and interrupt-staging helper surface.

It does not own queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe or remove lifecycle behavior.

Any attempt to reopen those blocked transport paths needs an Architecture Council reopen request with fresh linked evidence attached before this slice can claim broader ownership.

## Non-goals

This slice does not yet claim:

- transport-backed config-space writes
- interrupt acknowledgement
- reset flows
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated MMIO packet review guard
- `python3 scripts/zigux/check-phase10-mmio-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-mmio-packet.py`

2. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

3. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Keep the Phase 10 MMIO lane focused on another transport-safe observation helper or tightly coupled helper validation beyond the landed config-write disposition surface before widening into interrupt acknowledgement, queue discovery, reset paths, or probe lifecycle work.
