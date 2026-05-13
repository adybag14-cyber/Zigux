# Phase 10 Virtio Input Module Slice

This note records the currently landed module-facing packet around `drivers/virtio/virtio_input.zig`.

## Module Packet

The current module packet keeps `drivers/virtio/virtio_input_verify.zig` beside the direct helper, the dedicated queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, and the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`.

The same packet also keeps the bounded status-drain helper explicit: it reclaims queued status completions in memory without widening into transport-backed queue callbacks. The module-facing story therefore keeps registration blockers and reset-local teardown cleanup reviewable in the same bounded packet instead of flattening the input lane back to verify-plus-queue-only wording.

## Local Boundaries

- the dedicated queue-callback-preflight replay stays below real device event delivery
- the registration-preflight replay stays below `input_register_device()` lifecycle claims and keeps capability-setup plus multitouch-slot blockers explicit
- the teardown-observation replay stays below remove, freeze, restore, and transport-backed reset parity while keeping identity preservation and runtime cleanup explicit
- the bounded status-drain helper only models queue callbacks and completed status sends that can be reviewed locally in memory
- registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice

## Review Reminder

When this packet is reread, keep `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the bounded status-drain helper, and the reminder that queued status completions are only reclaimed in memory explicit in the same module-facing story.
