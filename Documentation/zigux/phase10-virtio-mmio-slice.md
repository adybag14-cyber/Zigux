# Phase 10 Virtio MMIO Slice

This note records the current shared Phase 10 virtio MMIO packet around `drivers/virtio/virtio_mmio.c` and the bounded review surface guarded by `scripts/zigux/check-phase10-mmio-packet.py`.

## Packet Surface

The current slice keeps `drivers/virtio/virtio_mmio.zig` aligned with `drivers/virtio/virtio_mmio_verify.zig`, the helper-local replay in `zigux/tests/phase10_virtio_mmio.zig`, the dedicated survey gate in `zigux/tests/phase10_virtio_mmio_survey.zig`, the manifest-backed packet inventory in `zigux/tests/phase10_virtio_mmio_manifest.json`, the broader survey in `Documentation/zigux/phase10-virtio-mmio-survey.md`, the packet-local config-write companion in `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, and the shared Phase 10 build route in `zigux/tests/phase10_build.zig`.

The same packet keeps the MMIO wrapper ladder explicit without widening into transport-backed execution: transport-identity readback, probe-preflight gating, selected-queue readiness, interrupt-ack disposition review, staged feature-word negotiation, planning-only config-write observation, and config-write disposition review all remain in-memory surfaces that stop short of live queue setup, IRQ delivery, DMA handoff, or probe/remove lifecycle closure.

## Local Boundaries

- transport identity stays below live MMIO pointer reads or writes
- queue readiness stays bounded to selected-queue programming and ready-state review, not queue discovery or execution parity
- interrupt-ack disposition stays bounded to pending, acknowledged, ignored, and remaining bits review, not live IRQ delivery parity
- feature negotiation stays observational and keeps shared, device-only, and driver-only bits explicit without claiming live negotiation
- config-write planning and disposition stay planning-only and keep the config window unchanged while surfacing byte-level deltas and generation drift
- the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice and still requires an Architecture Council reopen before any transport-backed follow-through

## Review Reminder

When this packet is reread, keep `scripts/zigux/check-phase10-mmio-packet.py`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, and `zigux/tests/phase10_build.zig` explicit in the same bounded Phase 10 story.
