# Phase 10 Virtio Core Slice

This document tracks the first bounded Phase 10 virtio-core starter under `drivers/virtio/`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-lab-starter`
- scope: status sequencing, bounded feature negotiation, queue callback bookkeeping, dedicated Phase 10 test wiring, and a lab-only review note only
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio.c` as the first virtio-core anchor and calls for lab-only validation before any deeper queue, transport, or MMIO work.

The live repo did not yet have any `drivers/virtio/*.zig` foothold. This slice lands the smallest honest core step: a lab-only state model for reset, `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, and `DRIVER_OK` sequencing plus bounded offered-feature checks and transport refusal handling.

## Landed starter surface

- module descriptor metadata naming the `drivers/virtio/virtio.c` anchor
- bounded reset behavior that clears negotiated state without pretending to touch real transport registers
- explicit `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, `DRIVER_OK`, `FAILED`, and `DEVICE_NEEDS_RESET` status-bit handling
- feature-offer validation that rejects driver requests for features the device did not advertise
- feature-window closure checks that keep driver feature offers closed once `FEATURES_OK` negotiation has been finalized
- bounded feature-index guards that reject requests outside the lab model's fixed feature-bit capacity
- queue callback registration bookkeeping that stays blocked until feature negotiation succeeds and never pretends to touch real transport setup
- queue callback enable, disable, unregister, and notification accounting that remains entirely in-memory for lab validation
- queue descriptor shape metadata that records bounded readable and writable descriptor counts plus indirect-descriptor intent without claiming real ring setup
- reset handling that clears queue callback registrations along with negotiated feature state
- a transport-acceptance toggle so the Phase 10 gate can model both successful `FEATURES_OK` handshakes and refusal paths
- dedicated Phase 10 tests and build wiring for the starter slice

## Roadmap Gap Snapshot

- covered now:
  - lab-only validation for `drivers/virtio/virtio.c`
  - core-side status sequencing and feature negotiation
  - bounded queue callback bookkeeping and queue shape metadata for reviewable lab tests
- still intentionally missing:
  - real virtqueue wrappers from `virtio_ring.c`
  - real MMIO wrappers from `virtio_mmio.c`
  - dual implementations for risky transport-facing paths
  - probe, remove, and real device lifecycle wiring

This keeps the Phase 10 core lane honest: the live Zigux slice now describes one queue's shape in memory, which narrows the gap to future virtqueue work without pretending any transport or ring code has already landed.

## Non-goals

This slice does not yet claim:

- real virtqueue wrapper parity
- real MMIO register reads or writes
- `virtio_mmio.c` transport glue
- `virtio_ring.c` queue lifecycle or notification behavior

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 virtio-core lane and add the next small core-only bridge from `drivers/virtio/virtio.c`, such as config-change enable and disable bookkeeping, before widening into `virtio_mmio` or `virtio_ring` transport work.
