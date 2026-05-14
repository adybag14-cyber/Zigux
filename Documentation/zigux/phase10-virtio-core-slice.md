# Phase 10 Virtio Core Slice

This note keeps the shipped Phase 10 core packet reviewable around `drivers/virtio/virtio.c` without widening into transport-backed lifecycle claims.

## Scope

Keep this slice aligned with:
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `scripts/zigux/check-phase10-core-packet.py`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `zigux/tests/phase10_build.zig`
- `drivers/virtio/virtio.zig`
- `drivers/virtio/virtio_driver_id.zig`
- `drivers/virtio/virtio_verify.zig`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_reset_queue.zig`
- `zigux/tests/phase10_virtio_driver_id.zig`

## Shipped Packet

Current `master` keeps the bounded core helper packet explicit through:
- the direct `drivers/virtio/virtio.zig` helper for status sequencing, feature negotiation narrowing, queue-shape bookkeeping, config-generation bookkeeping, interrupt acknowledgements, lifecycle guards, and reset replay in memory only
- the direct `drivers/virtio/virtio_driver_id.zig` helper for exact, wildcard, and unmatched identity-table reviewability without claiming bus registration
- the direct `drivers/virtio/virtio_verify.zig` replay for wrapper-facing lifecycle checkpoints, narrowed-feature summaries, failed-status teardown, and reset replay review
- the focused `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, and `zigux/tests/phase10_virtio_driver_id.zig` replays
- the dedicated survey packet through `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, and `Documentation/zigux/phase10-virtio-core-survey.md`
- the shared `zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10` replay routes

That keeps the Phase 10 roadmap destination family explicit through `drivers/virtio/*.zig` plus the justified support boundary in `zigux/kernel/` and `zigux/helpers/`.

## Boundary

This slice is still lab-only driver validation evidence. It does not claim:
- dual implementations for risky transport-facing paths
- transport-backed probe, full remove, or reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- MMIO register-window or IRQ behavior from `virtio_mmio.c`
- input registration lifecycle behavior from `virtio_input.c`

Keep the blocked risky-transport posture explicit beside `Documentation/zigux/freeze-map.md` and `zigux/tests/phase10_closure_manifest.json`.
