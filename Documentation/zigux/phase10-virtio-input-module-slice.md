# Phase 10 Virtio Input Module Slice

This note records the currently landed module-facing packet around `drivers/virtio/virtio_input.zig`.

## Module Packet

The current module packet keeps the direct helper in `drivers/virtio/virtio_input.zig`, the dedicated registration-preflight helper in `drivers/virtio/virtio_input_registration_preflight.zig`, the direct gate in `zigux/tests/phase10_virtio_input.zig`, the dedicated probe-preflight replay in `zigux/tests/phase10_virtio_input_probe_preflight.zig`, the dedicated queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, the dedicated status-drain replay in `zigux/tests/phase10_virtio_input_status_drain.zig`, and the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`.

The same packet also keeps the direct-helper-backed probe-preflight, registration-preflight, and status-drain replay boundaries explicit: probe handoff now stays name-plus-phys driven while missing serial remains informational, registration staging now keeps queue, event-buffer, capability, and multitouch blockers explicit below `input_register_device()`, and queued status completions are still reclaimed in memory without widening into transport-backed queue callbacks. The module-facing story therefore keeps identity staging, registration blockers, status completion review, and reset-local teardown cleanup reviewable in the same bounded packet instead of flattening the input lane back to queue-only wording.

## Local Boundaries

- the direct-helper-backed probe-preflight replay stays below real input registration and keeps name-plus-phys identity staging explicit while missing serial stays informational
- the dedicated queue-callback-preflight replay stays below real device event delivery
- the dedicated registration-preflight helper plus replay stay below `input_register_device()` lifecycle claims and keep queue setup, event-buffer fill, capability-setup, and multitouch-slot blockers explicit
- the teardown-observation replay stays below remove, freeze, restore, and transport-backed reset parity while keeping identity preservation and runtime cleanup explicit
- the bounded status-drain helper plus replay only model queue callbacks and completed status sends that can be reviewed locally in memory
- registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice

## Review Reminder

When this packet is reread, keep `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the bounded status-drain helper plus replay, and the reminder that queued status completions are only reclaimed in memory explicit in the same module-facing story.
