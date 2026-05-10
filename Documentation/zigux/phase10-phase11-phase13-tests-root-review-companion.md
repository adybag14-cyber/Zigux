# Phase 10 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet and
the review needs a compact tests-root carryover prompt.

Keep this note aligned with `zigux/tests/README.md`,
`Documentation/zigux/review-checklist.md`, and the packet-local closure or
workflow notes when they describe the same shared review surface.

The historical filename is retained because current `master` still has live
Phase 10 shared-surface references to this companion path. This restored note is
intentionally reduced to the Phase 10 packet that is still actively referenced
and fully verifiable from current `master`.

## Phase 10 tests-root packet

Keep the current shared Phase 10 packet explicit:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_closure_manifest.json`
- `drivers/virtio/virtio.zig`
- `drivers/virtio/virtio_driver_id.zig`
- `drivers/virtio/virtio_verify.zig`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_reset_queue.zig`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `zigux/tests/phase10_virtio_driver_id.zig`
- `drivers/virtio/virtio_ring.zig`
- `drivers/virtio/virtio_ring_verify.zig`
- `zigux/tests/phase10_virtio_ring.zig`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `drivers/virtio/virtio_input.zig`
- `drivers/virtio/virtio_input_verify.zig`
- `zigux/tests/phase10_virtio_input.zig`
- `zigux/tests/phase10_virtio_input_probe_preflight.zig`
- `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- `zigux/tests/phase10_virtio_input_registration_preflight.zig`
- `zigux/tests/phase10_virtio_input_teardown_observation.zig`
- `zigux/tests/phase10_virtio_input_status_drain.zig`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `drivers/virtio/virtio_mmio.zig`
- `drivers/virtio/virtio_mmio_verify.zig`
- `zigux/tests/phase10_virtio_mmio.zig`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Tests-root reviewer prompt:
- Do the shared closure note, shared build route, shared closure manifest, the
  direct `drivers/virtio/virtio.zig` plus `drivers/virtio/virtio_driver_id.zig`
  review surfaces, the core, ring, input, and MMIO manifests and survey replays,
  the focused input probe-preflight, queue-callback-preflight,
  registration-preflight, teardown-observation, and status-drain replays, and
  the five shipped Phase 10 packet guards still describe the same checker-backed
  virtio lab packet without implying a missing `validate-phase10.py`,
  `check-phase10-harness-coverage.py`, or `phase10-validate` surface?

## Shared rule

When this packet changes, keep the broad tests-root reminder, the shared review
checklist, this compact companion, and the Phase 10 packet-local closure note
reviewable together.
