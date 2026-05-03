# Phase 10 Virtio Core Slice

This document tracks the first bounded Phase 10 virtio-core starter under `drivers/virtio/`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-lab-starter`
- scope: status sequencing, bounded feature negotiation, queue callback bookkeeping, registration identity bookkeeping, driver ID-table match bookkeeping, config-change, driver-binding, remove-side bookkeeping, and config-generation bookkeeping, dedicated Phase 10 test wiring, and a lab-only review note only
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio.c` as the first virtio-core anchor and calls for lab-only validation before any deeper queue, transport, or MMIO work.

This lane started from an empty `drivers/virtio/*.zig` footing. The live repo now carries the smallest honest core step: a lab-only state model for reset, `ACKNOWLEDGE`, `DRIVER`, `FEATURES_OK`, and `DRIVER_OK` sequencing plus bounded offered-feature checks, registration identity bookkeeping, bounded device and vendor ID-table matching with `VIRTIO_DEV_ANY_ID` wildcards, transport refusal handling, config-change bookkeeping, the `drv && drv->config_changed` driver-binding branch, one bounded config-generation observation surface, one bounded remove-side handoff, and an explicit summary of the last config-change delivery disposition.

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
- registration identity bookkeeping for the `register_virtio_device()` and `virtio_uevent()` path, including the bounded `virtio%u` device name and modalias string
- bounded driver ID-table matching that records exact, wildcard, and first-match ordering behavior for `virtio_id_match()` and the `virtio_dev_match()` scan without widening into probe or remove lifecycle work
- config-change enable, disable, pending, flush, and reset bookkeeping that stays entirely in memory while making the later `virtio_config_enable()` and `virtio_config_disable()` review surface concrete
- driver-binding bookkeeping that records whether the bound driver exposes `config_changed` before the lab helper reports in-memory delivery
- driver-remove bookkeeping that disables the core-side config path, clears queue and handler bookkeeping, and returns the in-memory status word to `ACKNOWLEDGE` without pretending to touch transport reset or MMIO state
- bounded config-generation summaries that record generation, last observed generation, and pending observation state without pretending to read transport MMIO registers
- config-change disposition summaries that record whether the last `__virtio_config_changed()` replay was deferred, delivered to a present handler, or ignored because no handler was bound
- reset handling that clears queue callback registrations along with negotiated feature state
- a transport-acceptance toggle so the Phase 10 gate can model both successful `FEATURES_OK` handshakes and refusal paths
- dedicated Phase 10 tests and build wiring for the starter slice

## Roadmap Gap Snapshot

- covered now:
  - lab-only validation for `drivers/virtio/virtio.c`
  - core-side status sequencing, feature negotiation, bounded driver ID-table matching, and one bounded remove-side handoff
  - bounded queue callback bookkeeping, queue shape metadata, config-generation summaries, and config-change disposition summaries for reviewable lab tests
- still intentionally missing:
  - real virtqueue wrappers from `virtio_ring.c`
  - real MMIO wrappers from `virtio_mmio.c`
  - dual implementations for risky transport-facing paths
  - probe, remove, and real device lifecycle wiring

This keeps the Phase 10 core lane honest: the live Zigux slice now describes one queue's shape, one bounded registration identity path, one bounded driver ID-table match path, one bounded config-change path, one bounded config-generation observation path, one bounded remove-side handoff, and the last config-change delivery disposition in memory, which narrows the gap to future virtqueue work without pretending any transport or ring code has already landed.

The same parked core packet also participates in the shared closure evidence bundle through `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, and `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, so the current review path is broader than the dedicated core test alone even though the starter surface remains core-local.

## Non-goals

This slice does not yet claim:

- real virtqueue wrapper parity
- real MMIO register reads or writes
- `virtio_mmio.c` transport glue
- `virtio_ring.c` queue lifecycle or notification behavior

## Gates

1. run the shared closure inventory gate
- `python3 scripts/zigux/check-phase10-closure-inventory.py`

2. run the shared closure validation path
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

4. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Leave the Phase 10 virtio-core helper parked unless fresh review drift appears inside the landed driver ID-match, config-generation, config-change disposition, remove-side bookkeeping, or shared closure-evidence packet. Any future reopen in this lane should stay explicit about the remaining blocked probe, full remove, and transport-backed reset lifecycle gap instead of widening into `virtio_mmio` or `virtio_ring` work indirectly.
