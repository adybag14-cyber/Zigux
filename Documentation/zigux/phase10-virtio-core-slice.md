# Phase 10 Virtio Core Slice

This document tracks the first bounded Phase 10 virtio-core starter under `drivers/virtio/`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-lab-starter`
- scope: status sequencing, bounded feature negotiation, driver-validation narrowing, driver-name bookkeeping, queue callback bookkeeping, config-change bookkeeping, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guard bookkeeping, reset replay bookkeeping, bounded device-identity and driver-ID matching, the committed core survey manifest and survey gate, the dedicated Phase 10 core packet guard, the shared reset-queue and driver-id replays, dedicated Phase 10 build wiring, and the shared Phase 10 build-and-make routes
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `drivers/virtio/virtio_driver_id.zig`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_virtio_core_reset_queue.zig`
  - `zigux/tests/phase10_virtio_driver_id.zig`
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
- review surface:
  - `Documentation/zigux/phase10-virtio-core-slice.md`
  - `Documentation/zigux/phase10-virtio-core-survey.md`
  - `scripts/zigux/check-phase10-core-packet.py`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_virtio_core_reset_queue.zig`
  - `zigux/tests/phase10_virtio_driver_id.zig`
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
- current review note:
  - current `master` again carries a standalone `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `scripts/zigux/check-phase10-core-packet.py`; reviewers should treat the core lane as a manifest-backed survey packet plus build-and-test packet instead of a slice-note-only surface, including the shared `make -C zigux phase10-test` and `make -C zigux phase10` replay routes, and this packet is the current roadmap-facing `lab-only driver validation` evidence for the core anchor rather than a missing starter

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio.c` as the first virtio-core anchor and calls for lab-only validation before any deeper queue, transport, or MMIO work.

This lane started from an empty `drivers/virtio/*.zig` footing. The live repo now carries the smallest honest core step: a lab-only state model for reset, `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, and `DRIVER_OK` sequencing plus bounded offered-feature checks, driver-validation narrowing, transport refusal handling, driver-name bookkeeping, config-change bookkeeping, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guard bookkeeping, reset replay bookkeeping, and one sibling helper that replays bounded `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()` device-identity paths without widening into probe or remove claims.

## Landed starter surface

- module descriptor metadata naming the `drivers/virtio/virtio.c` anchor
- bounded reset behavior that clears negotiated state without pretending to touch real transport registers
- explicit `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, `DRIVER_OK`, `FAILED`, and `DEVICE_NEEDS_RESET` status-bit handling
- feature-offer validation that rejects driver requests for features the device did not advertise
- driver-validation narrowing that lets the lab helper replay how driver-side review can trim the offered feature set before the final `FEATURES_OK` handshake is accepted
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
- a restored manifest-backed review packet: the current core lane is reviewed through this slice note, the dedicated survey note and gate, the packet checker, `phase10_virtio_core.zig`, `phase10_virtio_core_reset_queue.zig`, `phase10_virtio_driver_id.zig`, `phase10_build.zig`, and the shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes

## Roadmap Gap Snapshot

- covered now:
  - lab-only validation for `drivers/virtio/virtio.c`
  - core-side status sequencing and feature negotiation
  - bounded driver-validation narrowing, driver-name, queue callback, queue shape, config-generation, interrupt-ack, lifecycle guard, and reset replay bookkeeping for reviewable lab tests
  - bounded device-identity and driver-ID review surfaces for `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()`
  - roadmap-facing `lab-only driver validation` evidence through the manifest, survey gate, survey note, dedicated checker, shared build replay, and shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes
- still intentionally missing:
  - real virtqueue wrappers from `virtio_ring.c`
  - real MMIO wrappers from `virtio_mmio.c`
  - dual implementations for risky transport-facing paths
  - the transport-backed probe or remove bridge needed to turn the starter into a true lab driver

## Non-goals

This slice does not yet claim:

- real virtqueue wrapper parity
- real MMIO register reads or writes
- `virtio_mmio.c` transport glue
- `virtio_ring.c` queue lifecycle or notification behavior

## Gates

1. run the dedicated core packet checker
- `python3 scripts/zigux/check-phase10-core-packet.py`

2. run the core survey gate
- `zig test zigux/tests/phase10_virtio_core_survey.zig`

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

4. run the Linux-style replay routes
- `make -C zigux phase10-test`
- `make -C zigux phase10`

## Next bounded step

Leave the Phase 10 virtio core lane parked unless fresh repo inspection finds directly coupled drift in the slice note, the roadmap-facing lab-validation evidence, the blocked bridge wording, the restored survey packet, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, or the shared `phase10_build.zig` route. Any future same-family move should stay tightly bounded around this core-only review packet rather than widening into probe, remove, or MMIO glue work.
