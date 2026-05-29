# Phase 10 ABI and Export Parity Scoreboard

This note records the bounded P10-L12 scoreboard state for the active Phase 10 virtio lab-driver packet. It is intentionally notes-only: scoreboard wording should move only when live repository evidence changes, and it must not claim transport-backed parity while the risky transport bridge remains blocked.

## Roadmap Scope

- roadmap phase: `Phase 10: Virtio and Lab Drivers`
- Linux anchors: `drivers/virtio/virtio.c`, `drivers/virtio/virtio_ring.c`, `drivers/virtio/virtio_input.c`, and `drivers/virtio/virtio_mmio.c`
- required features tracked here: `virtqueue wrappers`, `MMIO wrappers`, `lab-only driver validation`, and `dual implementations for risky areas`
- current risky transport posture: `blocked_on_risky_transport`

## Current Scoreboard

- `virtqueue_wrappers=starter_landed`
- `mmio_wrappers=starter_landed`
- `lab_only_driver_validation=starter_landed`
- `dual_implementations_for_risky_areas=blocked_on_risky_transport`

The scoreboard remains a starter parity packet, not a production transport claim. It is valid only while the closure evidence continues to point at driver-local lab slices, survey manifests, and shared validation gates instead of DMA paths, IRQ parity, probe/remove lifecycle completion, queue reset execution, or input registration lifecycle parity.

## Fresh Parity Evidence Recorded

Current `master` now includes `scripts/zigux/check-phase10-ring-manifest-destinations.py`, a dedicated P10-L10 guard for the ring manifest. That checker is substantive parity evidence because it fails closed if `zigux/tests/phase10_virtio_ring_manifest.json` drifts back to the older shared `drivers/virtio/virtio_ring.zig` destinations for these dedicated queue-wrapper helpers:

- `phase10-callback-enable-helper` -> `drivers/virtio/virtio_ring_callback_enable.zig`
- `phase10-queue-reset-readiness-helper` -> `drivers/virtio/virtio_ring_reset_readiness.zig`

The same checker also requires the manifest summary flags that prove the dedicated callback-enable and reset-readiness surfaces are present. This keeps the virtqueue-wrapper scoreboard anchored to concrete wrapper destinations rather than broad ring-helper shorthand.

## Replay Packet

The note was grounded in these live current-master surfaces:

- `Documentation/zigux/phase10-closure-evidence.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `scripts/zigux/check-phase10-ring-manifest-destinations.py`
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`

The narrow replay for the fresh guard is:

```sh
python3 scripts/zigux/check-phase10-ring-manifest-destinations.py --self-test
python3 scripts/zigux/check-phase10-ring-manifest-destinations.py
```

## Boundary

This note does not reopen Phase 10 transport behavior. It records one roadmap-aligned parity-evidence improvement in the ABI/export scoreboard family and leaves the remaining risky transport work blocked until an architecture-council-backed bridge exists.
