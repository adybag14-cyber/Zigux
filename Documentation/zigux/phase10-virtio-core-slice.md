# Phase 10 Virtio Core Slice

This document tracks the first bounded Phase 10 virtio-core starter under `drivers/virtio/`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-lab-starter`
- scope: status sequencing, bounded feature negotiation, driver-name bookkeeping, queue callback bookkeeping, config-change bookkeeping, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guard bookkeeping, reset replay bookkeeping, bounded device-identity and driver-ID matching, dedicated Phase 10 test wiring, and a lab-only review note only
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `drivers/virtio/virtio_driver_id.zig`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_virtio_driver_id.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
- review surface:
  - `Documentation/zigux/phase10-virtio-core-slice.md`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_virtio_driver_id.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
- current review note:
  - current `master` carries no standalone `zigux/tests/phase10_virtio_core_manifest.json` or `zigux/tests/phase10_virtio_core_survey.zig`; reviewers should treat the core lane as a slice-note-plus-build-and-test packet until those files actually ship again

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio.c` as the first virtio-core anchor and calls for lab-only validation before any deeper queue, transport, or MMIO work.

This lane started from an empty `drivers/virtio/*.zig` footing. The live repo now carries the smallest honest core step: a lab-only state model for reset, `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, and `DRIVER_OK` sequencing plus bounded offered-feature checks, transport refusal handling, driver-name bookkeeping, config-change bookkeeping, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guard bookkeeping, reset replay bookkeeping, and one sibling helper that replays bounded `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()` device-identity paths without widening into probe or remove claims.

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
- config-generation bookkeeping that keeps delivered generations, pending generations, and driver acknowledgements visible without pretending to wire real transport reads
- bounded interrupt-reason staging and acknowledgement bookkeeping that keeps pending and acknowledged queue-used or config-change reasons visible without claiming transport-backed IRQ handling
- lifecycle guard bookkeeping that makes the remaining attach, feature-negotiation, driver-ready, queue-registration, and reset-required gates visible before any transport-backed runtime work is claimed
- reset replay bookkeeping that keeps the negotiated-feature, queue-callback, config-generation, and interrupt state that would be rebuilt after a reset-required path visible without pretending to run a transport-backed reset flow
- bounded device-identity registration that keeps the `virtio%u` device name and `virtio:d...v...` modalias reviewable in memory without claiming bus registration
- bounded driver-ID table matching that records exact, wildcard-device, wildcard-vendor, and unmatched `virtio_id_match()` outcomes without widening into probe or remove wiring
- reset handling that clears queue callback registrations along with negotiated feature state
- a transport-acceptance toggle so the Phase 10 gate can model both successful `FEATURES_OK` handshakes and refusal paths
- dedicated Phase 10 tests and build wiring for the starter slice
- an intentionally compact review packet: the current core lane is reviewed through this slice note plus `phase10_virtio_core.zig`, `phase10_virtio_driver_id.zig`, `phase10_build.zig`, and `make -C zigux phase10`, not through a separate core manifest or survey gate

## Roadmap Gap Snapshot

- covered now:
  - lab-only validation for `drivers/virtio/virtio.c`
  - core-side status sequencing and feature negotiation
  - bounded driver-name, queue callback, queue shape, config-generation, interrupt-ack, lifecycle guard, and reset replay bookkeeping for reviewable lab tests
  - bounded device-identity and driver-ID review surfaces for `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()`
  - core-side bookkeeping that now supports the separate `virtio_ring`, `virtio_input`, and `virtio_mmio` lab slices without claiming transport parity
- still intentionally missing:
  - real virtqueue wrappers from `virtio_ring.c`
  - real MMIO wrappers from `virtio_mmio.c`
  - dual implementations for risky transport-facing paths
  - probe, remove, and real device lifecycle wiring

This keeps the Phase 10 core lane honest: the live Zigux slice now describes one queue's shape plus bounded driver-name, config-change, config-generation, interrupt-ack, lifecycle guard, reset replay, device-identity, and driver-ID paths in memory, and that core bookkeeping now feeds the separate `virtio_ring`, `virtio_input`, and `virtio_mmio` lab helpers without pretending transport-backed lifecycle behavior has already landed.

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

Leave the Phase 10 virtio core lane parked unless fresh repo inspection finds directly coupled drift in the slice note, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, or the shared `phase10_build.zig` route. Any future same-family move should stay tightly bounded around this core-only review packet or a roadmap-backed transport-facing lifecycle study rather than widening into probe, remove, or MMIO glue work.
