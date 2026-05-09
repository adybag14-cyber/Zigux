# Phase 10 Virtio Driver Lane Sequencing

This note turns the currently landed Phase 10 virtio evidence into one bounded anti-overlap map for driver lanes only.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-driver-lane-sequencing`
- shared packet: this owner map coordinates multiple driver lanes and therefore does not claim one dedicated lane key
- scope: use the current core, ring, input, and MMIO survey packets to say which Phase 10 driver lane owns which already-landed evidence and which next bounded step still belongs to that lane
- product boundary:
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`

## Why this note exists

The live repo already has four distinct Phase 10 driver packets:

- the core survey packet around `drivers/virtio/virtio.c`
- the ring survey packet around `drivers/virtio/virtio_ring.c`
- the input survey packet around `drivers/virtio/virtio_input.c`
- the MMIO survey packet around `drivers/virtio/virtio_mmio.c`

Those packets now share build wiring, one closure manifest, one shared closure note, the direct `zig build test --build-file zigux/tests/phase10_build.zig` route, shared `make -C zigux phase10-test` and `make -C zigux phase10` routes, and adjacent checker references. That shared replay surface is useful, but it also makes it easier for nearby scheduled runs to borrow each other's helper scope or reopen the wrong survey packet.

This note keeps the Phase 10 driver tranche honest by separating shared replay routes from per-lane ownership.

## Shared packet versus lane ownership

Shared Phase 10 replay surface:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_closure_manifest.json`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `zigux/Makefile`
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

These shared docs, the shared closure note, packet guards, the MMIO freeze-boundary checker, the direct `zig build` route, the make routes, plus the shared closure manifest prove that the current bounded virtio packet still replays together. They do not change which lane owns a helper, verify replay, manifest, survey gate, or next bounded follow-up. When those shared summaries call out the current focused replay evidence, keep `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `drivers/virtio/virtio_mmio_verify.zig`, and `zigux/tests/phase10_virtio_mmio.zig` explicit as lane-owned replays instead of collapsing them into generic focused-test shorthand.

## Lane map

`P10-L01` core lane owns the core lab-validation packet:

- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `scripts/zigux/check-phase10-core-packet.py`
- the bounded `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, and `drivers/virtio/virtio_verify.zig` review surface
- the focused `zigux/tests/phase10_virtio_core_reset_queue.zig` and `zigux/tests/phase10_virtio_driver_id.zig` replays

The next honest core step stays outside transport-backed probe or remove work. If this lane reopens, it should only fix directly coupled drift in the core lab-validation packet.

`P10-L07` ring lane owns queue-local virtqueue-wrapper evidence:

- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring.zig`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `scripts/zigux/check-phase10-ring-packet.py`
- `drivers/virtio/virtio_ring.zig`
- `drivers/virtio/virtio_ring_verify.zig`

This lane may talk about adjacent MMIO footing when the survey compares roadmap posture, but it does not own MMIO helper growth, MMIO manifests, or MMIO next-step selection. Fresh ring-packet readback now shows the queue-local follow-through is already landed: broken-queue recovery, clear-broken blocker exposure, packed-ring event-index review, and notification-data wrap-transition review are part of the shipped ring helper plus verifier packet, so the remaining roadmap lab-driver bridge stays MMIO-owned. If this lane reopens, keep it to the next smallest ring-packet truthfulness sync in the survey, manifest, slice, or dedicated guard rather than reopening new queue-local helper growth.

`P10-L13` input lane owns the lab-only input packet:

- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_input.zig`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `scripts/zigux/check-phase10-input-packet.py`
- `drivers/virtio/virtio_input.zig`
- `drivers/virtio/virtio_input_verify.zig`
- the focused `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` replays

This lane consumes shared core, ring, and MMIO prerequisites, but it does not own wrapper-layer growth in those packets. Its next bounded work stays inside input registration truthfulness, ownership notes, wrapper-facing verify replays, focused probe-preflight, queue-callback-preflight, registration-preflight, teardown-observation, or status-drain replays, or similarly narrow survey-backed repairs.

`P10-L10` MMIO lane owns MMIO helper footing, the risky-transport freeze boundary, and MMIO-local transport posture evidence:

- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio.zig`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `drivers/virtio/virtio_mmio.zig`
- `drivers/virtio/virtio_mmio_verify.zig`

Ring, core, and input lanes may cite this packet as adjacent evidence, but they should not absorb its config-window, config-write planning, config-write disposition, transport-identity, probe-preflight, selected-queue readiness, queue-discovery, IRQ, reset, or lifecycle follow-up. The shared `scripts/zigux/check-phase10-mmio-freeze-boundary.py` guard still belongs to this MMIO lane because it is the checker-backed proof that the risky transport posture and allowed Phase 10 destination family stay aligned with the MMIO packet instead of drifting into a broader transport claim. Its next bounded work stays inside those already-landed MMIO wrapper footholds or similarly narrow checker, manifest, slice-note, survey-note, or helper-test repairs until fresh reopen evidence exists for broader transport work.

## Anti-overlap rules

- If a Phase 10 run changes `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, the core manifest, the direct `zigux/tests/phase10_virtio_core.zig` replay, the focused `zigux/tests/phase10_virtio_core_reset_queue.zig` or `zigux/tests/phase10_virtio_driver_id.zig` replays, the core survey gate, or the core checker, that work belongs to the core lane.
- If a Phase 10 run changes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, the ring manifest, the direct `zigux/tests/phase10_virtio_ring.zig` replay, the ring survey gate, or the ring checker, that work belongs to the ring lane.
- If a Phase 10 run changes `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, the input manifest, the direct `zigux/tests/phase10_virtio_input.zig` replay, the focused `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, or `zigux/tests/phase10_virtio_input_status_drain.zig` replays, the input survey gate, or the input checker, that work belongs to the input lane.
- If a Phase 10 run changes `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, the direct `zigux/tests/phase10_virtio_mmio.zig` replay, the MMIO manifest, the MMIO survey gate, the MMIO checker, or `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, that work belongs to the MMIO packet instead of ring, input, or core follow-through.
- Shared build or make replay drift should only reopen the smallest directly coupled lane packet unless the break truly spans multiple driver packets at once.
- If a Phase 10 run only changes `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, `zigux/Makefile`, or the shared Phase 10 packet guards, it should reopen the smallest directly coupled shared review surface first instead of quietly consuming one of the driver lanes.

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the Phase 10 core, ring, input, and MMIO driver packets again. Fresh shared-surface readback now shows the docs-root, scripts-root, closure-note, lane-sequencing, companion, and tests-root Phase 10 summaries already keep the landed direct `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, the focused `zigux/tests/phase10_virtio_input_probe_preflight.zig` replay, and the adjacent queue-callback-preflight, registration-preflight, teardown-observation, and status-drain reminders explicit.

The next same-lane follow-through is now one shared-checklist truthfulness repair in `Documentation/zigux/review-checklist.md`: keep `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and `drivers/virtio/virtio_mmio.zig` visible beside the already-named `drivers/virtio/virtio_driver_id.zig`, the focused verify replays, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, and the adjacent queue-callback-preflight, registration-preflight, teardown-observation, and status-drain reminders so the reviewer-facing Phase 10 packet stays aligned with the broader docs-root, scripts-root, tests-root, closure-note, and companion summaries without reopening helper, manifest, survey, or checker work.
