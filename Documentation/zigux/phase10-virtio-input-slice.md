# Phase 10 Virtio Input Slice

This note records the current shared Phase 10 virtio input packet around `drivers/virtio/virtio_input.zig` and the bounded review surface guarded by `scripts/zigux/check-phase10-input-packet.py`.

## Packet Surface

The current slice keeps the direct helper in `drivers/virtio/virtio_input.zig`, the dedicated probe-preflight helper in `drivers/virtio/virtio_input_probe_preflight.zig`, the dedicated registration-preflight helper in `drivers/virtio/virtio_input_registration_preflight.zig`, and the wrapper-facing verify helper in `drivers/virtio/virtio_input_verify.zig` aligned with the direct gate in `zigux/tests/phase10_virtio_input.zig`, the dedicated probe-preflight replay in `zigux/tests/phase10_virtio_input_probe_preflight.zig`, the queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, the bounded status-drain replay in `zigux/tests/phase10_virtio_input_status_drain.zig`, and the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`.

The same packet keeps the queue-handling story explicit without widening into transport-backed runtime claims: probe staging stays identity-first, queue-callback readiness still sits behind queue configuration and buffer fill, registration staging still stops at local blocker reporting below `input_register_device()`, teardown review remains reset-local, and queued status completions are reclaimed only in memory.

## Local Boundaries

- the direct helper stays below real interrupt delivery and transport-backed queue execution
- the dedicated probe-preflight replay keeps name-plus-phys staging explicit while missing serial remains informational
- the queue-callback-preflight replay keeps callback ordering reviewable before live event delivery
- the dedicated registration-preflight helper plus replay keep queue, event-buffer, capability, and multitouch blockers explicit below `input_register_device()`
- the wrapper-facing verify helper keeps queue-callback ordering and registration prerequisites explicit without widening into transport-backed queue execution
- the teardown-observation replay keeps reset-local cleanup and identity preservation reviewable without claiming remove, freeze, or restore parity
- the bounded status-drain helper plus replay only model queued status completions that are reclaimed in memory

## Review Reminder

When this packet is reread, keep `scripts/zigux/check-phase10-input-packet.py`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, and `zigux/tests/phase10_virtio_input_teardown_observation.zig` explicit in the same bounded Phase 10 story.
