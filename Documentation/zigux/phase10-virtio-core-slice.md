# Phase 10 Virtio Core Slice

This document tracks the first bounded Phase 10 virtio-core starter under `drivers/virtio/`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-lab-starter`
- scope: status sequencing, bounded feature negotiation, driver-name bookkeeping, queue callback bookkeeping, config-change bookkeeping, dedicated Phase 10 test wiring, and a lab-only review note only
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio.c` as the first virtio-core anchor and calls for lab-only validation before any deeper queue, transport, or MMIO work.

This lane started from an empty `drivers/virtio/*.zig` footing. The live repo now carries the smallest honest core step: a lab-only state model for reset, `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, and `DRIVER_OK` sequencing plus bounded offered-feature checks, transport refusal handling, driver-name bookkeeping, and config-change bookkeeping.

## Landed starter surface

- module descriptor metadata naming the `drivers/virtio/virtio.c` anchor
- bounded reset behavior that clears negotiated state without pretending to touch real transport registers
- explicit `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, `DRIVER_OK`, `FAILED`, and `DEVICE_NEEDS_RESET` status-bit handling
- feature-offer validation that rejects driver requests for features the device did not advertise
- feature-window closure checks that keep driver feature offers closed once `FEATURES_OK` negotiation has been finalized
- bounded feature-index guards that reject requests outside the lab model's fixed feature-bit capacity
- bounded driver-name bookkeeping that keeps named and anonymous lab-driver attachment visible without pretending to wire real probe or remove paths
- queue callback registration bookkeeping that stays blocked until feature negotiation succeeds and never pretends to touch real transport setup
- queue callback enable, disable, unregister, and notification accounting that remains entirely in-memory for lab validation
- queue descriptor shape metadata that records bounded readable and writable descriptor counts plus indirect-descriptor intent without claiming real ring setup
- config-change enable, disable, pending, flush, and reset bookkeeping that stays entirely in memory while making the later `virtio_config_enable()` and `virtio_config_disable()` review surface concrete
- reset handling that clears queue callback registrations along with negotiated feature state
- a transport-acceptance toggle so the Phase 10 gate can model both successful `FEATURES_OK` handshakes and refusal paths
- dedicated Phase 10 tests and build wiring for the starter slice

## Roadmap Gap Snapshot

- covered now:
  - lab-only validation for `drivers/virtio/virtio.c`
  - core-side status sequencing and feature negotiation
  - bounded driver-name, queue callback, and queue shape bookkeeping for reviewable lab tests
  - core-side bookkeeping that now supports the separate `virtio_ring`, `virtio_input`, and `virtio_mmio` lab slices without claiming transport parity
- still intentionally missing:
  - real virtqueue wrappers from `virtio_ring.c`
  - real MMIO wrappers from `virtio_mmio.c`
  - dual implementations for risky transport-facing paths
  - probe, remove, and real device lifecycle wiring

This keeps the Phase 10 core lane honest: the live Zigux slice now describes one queue's shape plus bounded driver-name and config-change paths in memory, and that core bookkeeping now feeds the separate `virtio_ring`, `virtio_input`, and `virtio_mmio` lab helpers without pretending transport-backed lifecycle behavior has already landed.

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

Stay in the broader Phase 10 virtio lane only for another small core-local bridge that is still missing after the landed ring, input, and MMIO footholds, such as bounded config-generation bookkeeping, before widening into interrupt acknowledgement, reset flows, or probe lifecycle work.
