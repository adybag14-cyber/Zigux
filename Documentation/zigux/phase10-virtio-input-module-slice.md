# Phase 10 Virtio Input Module Slice

This note records the currently landed module-facing packet around `drivers/virtio/virtio_input.zig`.

## Module Packet

The current module packet keeps the direct helper beside the dedicated probe-preflight helper in `drivers/virtio/virtio_input_probe_preflight.zig`, the dedicated registration-preflight helper in `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, the direct gate in `zigux/tests/phase10_virtio_input.zig`, the dedicated queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, and the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`.

The same packet also keeps the bounded probe-preflight, registration-preflight, and status-drain helper boundaries explicit: probe handoff now stays name-plus-phys driven while missing serial remains informational, registration staging now keeps queue, event-buffer, capability, and multitouch blockers explicit below `input_register_device()`, and queued status completions are still reclaimed in memory without widening into transport-backed queue callbacks. The module-facing story therefore keeps identity staging, registration blockers, and reset-local teardown cleanup reviewable in the same bounded packet instead of flattening the input lane back to verify-plus-queue-only wording.

## Local Boundaries

- the dedicated probe-preflight helper stays below real input registration and keeps name-plus-phys identity staging explicit while missing serial stays informational
- the dedicated queue-callback-preflight replay stays below real device event delivery
- the dedicated registration-preflight helper plus replay stay below `input_register_device()` lifecycle claims and keep queue setup, event-buffer fill, capability-setup, and multitouch-slot blockers explicit
- the teardown-observation replay stays below remove, freeze, restore, and transport-backed reset parity while keeping identity preservation and runtime cleanup explicit
- the bounded status-drain helper only models queue callbacks and completed status sends that can be reviewed locally in memory
- registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice

## Review Reminder

When this packet is reread, keep `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the bounded status-drain helper, and the reminder that queued status completions are only reclaimed in memory explicit in the same module-facing story.
