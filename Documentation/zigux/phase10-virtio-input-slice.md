# Phase 10 Virtio Input Slice

This slice keeps the current `virtio_input` packet reviewable as a bounded Phase 10 lab-driver surface.

## Scope

Keep this note focused on the helper-facing, manifest-backed, checker-backed, and replay-facing packet that already exists around `drivers/virtio/virtio_input.c`.

The current slice is anchored by the direct helper in `drivers/virtio/virtio_input.zig`, the dedicated probe-preflight helper in `drivers/virtio/virtio_input_probe_preflight.zig`, the direct gate in `zigux/tests/phase10_virtio_input.zig`, the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the bounded status-completion drain helper plus replay in `zigux/tests/phase10_virtio_input_status_drain.zig`, the committed survey manifest in `zigux/tests/phase10_virtio_input_manifest.json`, the survey gate in `zigux/tests/phase10_virtio_input_survey.zig`, and the dedicated packet checker in `scripts/zigux/check-phase10-input-packet.py`.

## What This Slice Covers

- the direct helper in `drivers/virtio/virtio_input.zig`, including the helper-local identity, capability, multitouch-slot, registration-preflight, queue-callback-preflight, status-drain, and teardown-observation summaries that stay inside VM-friendly lab validation
- the dedicated probe-preflight helper in `drivers/virtio/virtio_input_probe_preflight.zig` together with the direct gate in `zigux/tests/phase10_virtio_input.zig`
- the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay that proves bounded ordering below registration lifecycle claims
- the focused queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- the focused registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`
- the focused teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`
- the bounded status-completion drain helper plus replay in `zigux/tests/phase10_virtio_input_status_drain.zig`
- the committed survey manifest in `zigux/tests/phase10_virtio_input_manifest.json`, the survey gate in `zigux/tests/phase10_virtio_input_survey.zig`, and the dedicated packet checker in `scripts/zigux/check-phase10-input-packet.py` that keep the same bounded Phase 10 input packet fail-closed

## What This Slice Does Not Claim

This slice does not claim transport-backed probe, remove, freeze, restore, or reset paths. Those remain outside the current Phase 10 input packet while risky transport stays blocked.

## Next Packet-Local Follow-Through

Keep the next reminder-only follow-through inside the directly coupled survey note, survey manifest, survey gate, dedicated packet checker, direct gate, and slice metadata while the adjacent shared build-graph follow-through stays parked in the dedicated compile-path lane.

## Review Reminder

When this packet is reread, keep `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, `scripts/zigux/check-phase10-input-packet.py`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the bounded status-drain helper, and the reminder that queued status completions are only reclaimed in memory explicit in the same bounded manifest-backed checker-backed story.
