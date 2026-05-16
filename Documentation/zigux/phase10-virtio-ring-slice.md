# Phase 10 Virtio Ring Slice

This note records the current shared Phase 10 virtio ring packet around `drivers/virtio/virtio_ring.zig` and the bounded review surface guarded by `scripts/zigux/check-phase10-ring-packet.py`.

## Packet Surface

The current slice keeps the direct helper in `drivers/virtio/virtio_ring.zig` and the wrapper-facing verify helper in `drivers/virtio/virtio_ring_verify.zig` aligned with the direct gate in `zigux/tests/phase10_virtio_ring.zig`, the notify-prepare idempotent replay in `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, the reset-reuse replay in `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, the survey gate in `zigux/tests/phase10_virtio_ring_survey.zig`, and the packet-local inventory in `zigux/tests/phase10_virtio_ring_manifest.json`.

The same packet keeps the queue-local helper ladder explicit without widening into transport-backed lifecycle claims: `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper` remain reviewable here as the bounded virtqueue-wrapper surface.

## Local Boundaries

- queue-local metadata stays below MMIO-backed queue discovery, IRQ acknowledgement, DMA handoff, and probe or remove lifecycle work
- notify bookkeeping stays in memory only and remains bounded to avail shadow, publish debt, kick-needed reporting, and notification-data summary state
- used-buffer polling and callback re-enable or delay stay queue-local and do not claim transport-backed interrupt delivery
- `resetQueue()` clears avail, used, callback, outstanding-chain, and notify bookkeeping while preserving descriptor-count and layout metadata for reuse
- reset-readiness preflight reports unpublished-chain, outstanding-chain, unpolled-used-chain, and broken-queue blockers before any transport-backed reset execution is claimed
- the wrapper-facing verify helper keeps delayed-callback pacing, packed event-index cues, clear-broken blocker exposure, and reset-readiness blockers explicit without widening into MMIO execution
- the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent MMIO packet in `drivers/virtio/virtio_mmio.zig`

## Review Reminder

When this packet is reread, keep `scripts/zigux/check-phase10-ring-packet.py`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-ring-survey.md`, and `Documentation/zigux/phase10-virtio-ring-slice.md` explicit in the same bounded Phase 10 story.
