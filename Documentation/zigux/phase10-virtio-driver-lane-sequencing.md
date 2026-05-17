# Phase 10 Virtio Driver Lane Sequencing
This note keeps the active Phase 10 virtio driver pod split into bounded owner lanes so shared reminder surfaces do not collapse core, ring, input, MMIO, and risky-transport follow-through into one noisy bucket.

## Scope
Use this note when a Phase 10 change touches the shared reminder packet under `Documentation/zigux/phase10-*.md`, `scripts/zigux/check-phase10-*.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md`.

## Lane Split
Keep the current lane split explicit:
- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, and the shared Phase 10 wording in the docs root, review checklist, scripts root, and tests root
- current `master` still does not materialize `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, or `zigux/Makefile` through the direct readback available in this lane, so keep those validator-first and Linux-style make-route names framed as last-known packet members until a fresh reread proves they are back
- core lane `P10-L01` owns the bounded core packet around `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `Documentation/zigux/phase10-virtio-core-survey.md`; if `Documentation/zigux/phase10-virtio-core-slice.md` is still absent on current `master`, record it as a repo-reality gap instead of direct evidence
- ring lane `P10-L10` owns the queue-local wrapper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, and `Documentation/zigux/phase10-virtio-ring-survey.md`
- MMIO lane `P10-L11` owns the bounded MMIO helper packet around `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`; if a dedicated `Documentation/zigux/phase10-virtio-mmio-slice.md` companion or standalone `zigux/tests/phase10_virtio_mmio.zig` replay is not directly re-readable on current `master`, keep it framed as a repo-reality gap or closure-packet vocabulary rather than direct evidence
- input lane `P10-L13` owns the current input packet through `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-input-survey.md`
- risky-transport follow-through stays outside the shared reminder lane: keep `phase10-virtio-input-registration-lifecycle` and `phase10-mmio-lifecycle-and-irq-paths` parked as the next bounded transport blockers named by `Documentation/zigux/phase10-closure-evidence.md` instead of flattening them into current closure claims

## Shared Packet Boundaries
The shared Phase 10 reminder packet should stay parked on the shared reminder and checker stack:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Current `master` already gives this lane directly re-readable packet-local anchors through `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`. Use those anchors before widening shared wording back into direct claims about validator-first routes, Linux-style make routes, or packet-local slice companions that current readback still does not materialize.

## Sequencing Rules
1. Prefer one Phase 10 lane at a time instead of batching core, ring, input, MMIO, and risky-transport reminder work into one mixed change.
2. Keep the shared reminder lane honest: it may repair only the shared packet truthfulness surfaces and must not absorb driver-local helper changes unless that owner lane is the thing moving.
3. Keep the ring lane below transport-backed execution: queue shape, callback pacing, notify preparation, reset readiness, and reset reuse stay queue-local review surfaces, not IRQ, DMA, or live reset claims.
4. Keep the input lane below `input_register_device()` lifecycle closure: queue-callback ordering, registration blockers, teardown observation, and status-drain review stay bounded in memory.
5. Keep the MMIO lane below transport-backed queue setup, IRQ delivery, DMA handoff, and probe or remove lifecycle claims.
6. Future shared-note refreshes should start from `Documentation/zigux/phase10-closure-evidence.md` plus the directly re-readable packet-local anchors before restating inventory counts, route names, or direct-readback posture.
7. If a packet-local companion is absent on current `master`, record that gap explicitly instead of silently re-promoting it into shipped shared evidence.

## Non-Goals
This note does not widen Phase 10 into:
- queue setup or reset execution parity
- IRQ parity or DMA-facing behavior
- probe, remove, freeze, or restore lifecycle closure
- an Architecture Council reopen or a freeze-map status change
- direct proof that the validator-first or Linux-style make-route stack has returned on current `master`
