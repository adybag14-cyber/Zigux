# Phase 10 Virtio Driver Lane Sequencing

This note turns the currently landed Phase 10 virtio evidence into one bounded anti-overlap map for driver lanes only.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-driver-lane-sequencing`
- lane: `P10-Y06`
- scope: use the current core, ring, input, and MMIO survey packets to say which Phase 10 driver lane owns which already-landed evidence and which next bounded step still belongs to that lane
- product boundary:
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`

## Why this note exists

The live repo already has four distinct Phase 10 driver packets:

- the core survey packet around `drivers/virtio/virtio.c`
- the ring survey packet around `drivers/virtio/virtio_ring.c`
- the input survey packet around `drivers/virtio/virtio_input.c`
- the MMIO survey packet around `drivers/virtio/virtio_mmio.c`

Those packets now share build wiring, one closure manifest, shared `make -C zigux phase10-test` and `make -C zigux phase10` routes, and adjacent checker references. That shared replay surface is useful, but it also makes it easier for nearby scheduled runs to borrow each other's helper scope or reopen the wrong survey packet.

This note keeps the Phase 10 driver tranche honest by separating shared replay routes from per-lane ownership.

## Shared packet versus lane ownership

Shared Phase 10 replay surface:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_closure_manifest.json`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `zigux/Makefile`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

These shared docs, packet guards, routes, plus the shared closure manifest prove that the current bounded virtio packet still replays together. They do not change which lane owns a helper, verify replay, manifest, survey gate, or next bounded follow-up. When those shared summaries call out the current focused replay evidence, keep `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` explicit as lane-owned replays instead of collapsing them into generic focused-test shorthand.

## Lane map

`P10-L01` core lane owns the core lab-validation packet:

- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `scripts/zigux/check-phase10-core-packet.py`
- the bounded `drivers/virtio/virtio.zig` and `drivers/virtio/virtio_driver_id.zig` review surface
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

This lane may talk about adjacent MMIO footing when the survey compares roadmap posture, but it does not own MMIO helper growth, MMIO manifests, or MMIO next-step selection. Its next bounded work stays queue-local, such as broken-queue recovery or packed-ring event-index review.

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
- the focused `zigux/tests/phase10_virtio_input_status_drain.zig` replay

This lane consumes shared core, ring, and MMIO prerequisites, but it does not own wrapper-layer growth in those packets. Its next bounded work stays inside input registration truthfulness, ownership notes, wrapper-facing verify replays, or similarly narrow survey-backed repairs.

`P10-L10` MMIO lane owns MMIO helper footing and risky-transport boundaries:

- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio.zig`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `drivers/virtio/virtio_mmio.zig`

Ring, core, and input lanes may cite this packet as adjacent evidence, but they should not absorb its transport-identity helper, queue-discovery, IRQ, reset, or lifecycle follow-up.

## Anti-overlap rules

- If a Phase 10 run changes `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, the core manifest, the direct `zigux/tests/phase10_virtio_core.zig` replay, the core survey gate, or the core checker, that work belongs to the core lane.
- If a Phase 10 run changes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, the ring manifest, the direct `zigux/tests/phase10_virtio_ring.zig` replay, the ring survey gate, or the ring checker, that work belongs to the ring lane.
- If a Phase 10 run changes `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, the input manifest, the direct `zigux/tests/phase10_virtio_input.zig` replay, the input survey gate, the focused status-drain replay, or the input checker, that work belongs to the input lane.
- If a Phase 10 run changes `drivers/virtio/virtio_mmio.zig`, the direct `zigux/tests/phase10_virtio_mmio.zig` replay, the MMIO manifest, the MMIO survey gate, or the MMIO checker, that work belongs to the MMIO packet instead of ring, input, or core follow-through.
- Shared build or make replay drift should only reopen the smallest directly coupled lane packet unless the break truly spans multiple driver packets at once.
- If a Phase 10 run only changes `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, `zigux/Makefile`, or the shared Phase 10 packet guards, it should reopen the smallest directly coupled shared review surface first instead of quietly consuming one of the driver lanes.

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the Phase 10 core, ring, input, and MMIO driver packets again. Any deeper helper or survey work should return to the owning driver lane instead of expanding this note.
