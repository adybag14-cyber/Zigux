# Phase 10 Virtio Input Slice

This slice keeps the current `virtio_input` packet reviewable as a bounded Phase 10 lab-driver surface.

## Scope

Keep this note focused on the helper-facing and replay-facing packet that already exists around `drivers/virtio/virtio_input.c`.

The current slice is anchored by the direct helper in `drivers/virtio/virtio_input.zig`, the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, and the bounded status-completion drain summaries in `zigux/tests/phase10_virtio_input_status_drain.zig`.

## What This Slice Covers

- helper-local identity, capability, multitouch-slot, probe-preflight, registration-preflight, queue-callback-preflight, status-drain, and teardown-observation summaries that stay inside VM-friendly lab validation
- the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay that proves bounded ordering below registration lifecycle claims
- the focused queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- bounded status-completion drain summaries in `zigux/tests/phase10_virtio_input_status_drain.zig`

## What This Slice Does Not Claim

This slice does not claim transport-backed probe, remove, freeze, restore, or reset paths. Those remain outside the current Phase 10 input packet while risky transport stays blocked.

## Next Packet-Local Follow-Through

Keep the next reminder-only follow-through inside the directly coupled survey note, manifest, and survey gate while the adjacent shared build-graph repair stays parked in the dedicated compile-path lane.
