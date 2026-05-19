# Phase 10 Virtio Ring Slice

This note records the current shared Phase 10 ring packet around `drivers/virtio/virtio_ring.c` and the bounded review surface guarded by `scripts/zigux/check-phase10-ring-packet.py`.

## Packet Surface

Fresh direct readback on current `master` now materializes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, and `zigux/tests/phase10_virtio_ring_survey.zig`, while the broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize through the same direct-readback path.

The shared ring packet therefore keeps the restored helper, the wrapper-facing verify replay, the focused prepare-kick, reset-reuse, broken-queue, and delayed-callback replays, and the dedicated survey replay as current direct evidence while `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `scripts/zigux/check-phase10-ring-packet.py`, and `zigux/tests/phase10_build.zig` stay directly re-readable on `master`.

The same packet keeps the queue-local helper ladder explicit without widening into transport-backed lifecycle claims: `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper` remain the bounded virtqueue-wrapper destinations that the restored helper now carries, the broader ring replay still remains outside direct current-head evidence in this slice, the dedicated survey gate is now a landed review surface inside this slice, and the MMIO-owned risky-transport bridge remains outside direct current-head evidence here too.

## Local Boundaries

- queue-local metadata stays below MMIO-backed queue discovery, IRQ acknowledgement, DMA handoff, and probe/remove lifecycle work
- notify bookkeeping stays in memory only and remains bounded to avail shadow, publish debt, kick-needed reporting, and notification-data summary state
- used-buffer polling and callback re-enable or delay stay queue-local and do not claim transport-backed interrupt delivery
- reset-local bookkeeping remains part of the ring packet vocabulary and is directly backed by the restored helper, the focused reset-reuse replay, and the dedicated survey replay on current `master`
- the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent MMIO packet in `drivers/virtio/virtio_mmio.zig`

## Review Reminder

When this packet is reread, keep `scripts/zigux/check-phase10-ring-packet.py`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_build.zig`, the shared closure packet, and the shared tests-root review companion explicit in the same bounded Phase 10 story, and keep the broader replay `zigux/tests/phase10_virtio_ring.zig` framed as a direct-readback gap until a fresh reread proves it returned.
