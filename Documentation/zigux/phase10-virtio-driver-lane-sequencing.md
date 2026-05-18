# Phase 10 Virtio Driver Lane Sequencing
This note keeps the active Phase 10 virtio driver pod split into bounded owner lanes so shared reminder surfaces do not collapse core, ring, input, MMIO, and risky-transport follow-through into one noisy bucket.

## Scope
Use this note when a Phase 10 change touches the shared reminder packet under `Documentation/zigux/phase10-*.md`, `scripts/zigux/check-phase10-*.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md`.

## Lane Split
Keep the current lane split explicit:
- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-shared-freeze-boundary.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, and the shared Phase 10 wording in the docs root, review checklist, scripts root, and tests root
- current `master` still does not materialize `scripts/zigux/validate-phase10.py` or `scripts/zigux/validate-phase10-closure.py` through the direct readback available in this lane, while `zigux/Makefile` now rematerializes and its live body exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`, so keep those still-missing dedicated validator-script names framed as last-known packet members or repo-reality gaps while treating the returned Makefile-backed route stack as the shared build gate
- core lane `P10-L01` owns the bounded core packet around `drivers/virtio/virtio.zig`, while `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `scripts/zigux/check-phase10-core-packet.py` should stay framed as last-known packet members or repo-reality gaps until a fresh direct reread proves they materialize again on current `master`; keep the returned shared reminder packet aligned to that narrower core-side readback posture instead of restating the broader packet as fully landed here
- ring lane `P10-L05` owns the queue-local wrapper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, and `scripts/zigux/check-phase10-ring-packet.py`
- MMIO lane `P10-L11` owns the bounded MMIO helper packet around `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`; `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` are back as directly re-readable helper-local manifest and replay anchors and should stay paired with `drivers/virtio/virtio_mmio.zig` plus `drivers/virtio/virtio_mmio_verify.zig` in the shared reminder packet
- input lane `P10-L13` owns the current input packet through `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-input-survey.md`
- risky-transport follow-through stays outside the shared reminder lane: keep `phase10-virtio-input-registration-lifecycle` and `phase10-mmio-lifecycle-and-irq-paths` parked as the next bounded transport blockers named by `Documentation/zigux/phase10-closure-evidence.md` instead of flattening them into current closure claims

## Shared Packet Boundaries
The shared Phase 10 reminder packet should stay parked on the shared reminder and checker stack:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `scripts/zigux/check-phase10-bootstrap-route.py`
- `scripts/zigux/check-phase10-shared-freeze-boundary.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Current `master` gives this lane a mixed set of directly re-readable packet-local anchors: `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/Makefile` still materialize here, while authenticated contents reads still fail for `Documentation/zigux/phase10-virtio-core-slice.md` and `Documentation/zigux/phase10-virtio-core-survey.md`. Use the directly re-readable ring, input, and MMIO anchors before widening shared wording back into direct claims about the missing core-side companions or the still-missing dedicated `scripts/zigux/validate-phase10.py` and `scripts/zigux/validate-phase10-closure.py` surfaces. Keep the returned `zigux/Makefile` body together with `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate rather than restating them as gaps.

## Sequencing Rules
1. Prefer one Phase 10 lane at a time instead of batching core, ring, input, MMIO, and risky-transport reminder work into one mixed change.
2. Keep the shared reminder lane honest: it may repair only the shared packet truthfulness surfaces and must not absorb driver-local helper changes unless that owner lane is the thing moving.
3. Keep the ring lane below transport-backed execution: queue shape, callback pacing, notify preparation, reset readiness, reset reuse, broken-queue fencing, and delayed-callback budgeting stay queue-local review surfaces, not IRQ, DMA, or live reset claims.
4. Keep the input lane below `input_register_device()` lifecycle closure: queue-callback ordering, registration blockers, teardown observation, and status-drain review stay bounded in memory.
5. Keep the MMIO lane below transport-backed queue setup, IRQ delivery, DMA handoff, and probe or remove lifecycle claims.
6. Future shared-note refreshes should start from `Documentation/zigux/phase10-closure-evidence.md` plus the directly re-readable packet-local anchors before restating inventory counts, route names, or direct-readback posture.
7. If a packet-local companion is absent on current `master`, record that gap explicitly instead of silently re-promoting it into shipped shared evidence.
8. Treat the shared `zigux/tests/phase10_build.zig` route as already-landed validation evidence for the directly re-readable ring helper packet, the input packet's direct gate plus its probe-preflight, queue-callback-preflight, registration-preflight, status-drain, teardown-observation, survey, and verify compile entries, and the helper-local MMIO replay and survey compile entries; do not keep routing that build-graph work into stale adjacent reminder text.

## Non-Goals
This note does not widen Phase 10 into:
- queue setup or reset execution parity
- IRQ parity or DMA-facing behavior
- probe, remove, freeze, or restore lifecycle closure
- an Architecture Council reopen or a freeze-map status change
- direct proof that the dedicated validator-script stack or the broader core-side packet has returned on current `master`
