# Phase 10 Virtio Input Slice

This note records the current shared Phase 10 virtio input packet around `drivers/virtio/virtio_input.zig` and the bounded review surface guarded by `scripts/zigux/check-phase10-input-packet.py`.

## Packet Surface

The current slice keeps the direct helper in `drivers/virtio/virtio_input.zig`, the dedicated probe-preflight helper in `drivers/virtio/virtio_input_probe_preflight.zig`, the dedicated queue-callback-preflight helper in `drivers/virtio/virtio_input_queue_callback_preflight.zig`, the dedicated registration-preflight helper in `drivers/virtio/virtio_input_registration_preflight.zig`, the dedicated status-drain helper in `drivers/virtio/virtio_input_status_drain.zig`, the dedicated teardown-observation helper in `drivers/virtio/virtio_input_teardown_observation.zig`, and the wrapper-facing verify helper in `drivers/virtio/virtio_input_verify.zig` aligned with the direct gate in `zigux/tests/phase10_virtio_input.zig`, the dedicated probe-preflight replay in `zigux/tests/phase10_virtio_input_probe_preflight.zig`, the queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, the bounded status-drain replay in `zigux/tests/phase10_virtio_input_status_drain.zig`, the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the dedicated survey gate in `zigux/tests/phase10_virtio_input_survey.zig`, and the manifest-backed packet inventory in `zigux/tests/phase10_virtio_input_manifest.json`.

The same packet keeps the queue-handling story explicit without widening into transport-backed runtime claims: probe staging stays identity-first, the dedicated queue-callback-preflight helper plus replay keep callback ordering reviewable before live event delivery, registration staging still stops at local blocker reporting below `input_register_device()`, teardown review remains reset-local, wrapper-facing verify coverage keeps teardown-reset parity explicit across reset, queued status completions are reclaimed only in memory, and the dedicated survey gate plus manifest-backed inventory keep the landed queue-handling, registration-preflight, status-drain, teardown-observation, and teardown-reset verify packet reviewable together through the shared Phase 10 build route.

## Local Boundaries

- the direct helper stays below real interrupt delivery and transport-backed queue execution
- the dedicated probe-preflight replay keeps name-plus-phys staging explicit while missing serial remains informational
- the dedicated queue-callback-preflight helper plus replay keep callback ordering reviewable before live event delivery
- the dedicated registration-preflight helper plus replay keep queue, event-buffer, capability, and multitouch blockers explicit below `input_register_device()`
- the wrapper-facing verify helper keeps queue-callback ordering, registration prerequisites, and teardown-reset parity explicit across reset without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims
- the dedicated teardown-observation helper plus replay keep reset-local cleanup and identity preservation reviewable without claiming remove, freeze, or restore parity
- the bounded status-drain helper plus replay only model queued status completions that are reclaimed in memory
- the dedicated survey gate plus manifest-backed inventory stay below transport-backed lifecycle closure while keeping the landed packet inventory explicit in the shared build route

## Review Reminder

When this packet is reread, keep `scripts/zigux/check-phase10-input-packet.py`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, and `zigux/tests/phase10_virtio_input_manifest.json` explicit in the same bounded Phase 10 story.
