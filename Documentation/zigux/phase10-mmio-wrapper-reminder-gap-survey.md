# Phase 10 MMIO Wrapper Reminder Gap Survey

This note records the bounded `P10-L13` cleanup survey around the Phase 10 MMIO reminder stack.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-wrapper-reminder-gap`
- lane family: `Phase 10 virtio MMIO`
- lane key: `P10-L13`
- surveyed against current `master` readback on `2026-05-27`
- scope: compare the roadmap-backed MMIO wrapper packet against the current shared reminder surfaces and name the smallest same-lane cleanup step

## Why this survey exists

The Phase 10 roadmap keeps MMIO work inside wrapper-first lab-driver validation. That means the reminder stack should keep shipped wrapper files explicit when they are already part of current repo reality.

Current `master` already ships these dedicated MMIO wrapper surfaces beside `drivers/virtio/virtio_mmio.zig`:
- `drivers/virtio/virtio_mmio_apply_observation.zig`
- `drivers/virtio/virtio_mmio_config_write_plan_freshness.zig`
- `drivers/virtio/virtio_mmio_verify.zig`

The narrower MMIO survey and slice notes already treat those wrappers as part of the bounded packet, but the broader shared reminder stack still undercounts them in a few places.

## Current repo reality

Current `master` readback keeps the helper-local MMIO packet explicit through:
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`
- `drivers/virtio/virtio_mmio.zig`
- `drivers/virtio/virtio_mmio_apply_observation.zig`
- `drivers/virtio/virtio_mmio_config_write_plan_freshness.zig`
- `drivers/virtio/virtio_mmio_verify.zig`
- `zigux/tests/phase10_virtio_mmio.zig`
- `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`
- `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `zigux/tests/phase10_build.zig`

These surfaces stay bounded to reviewable lab evidence only. They do not claim queue execution parity, shared IRQ delivery, DMA behavior, or probe/remove lifecycle closure.

## Reminder-stack gap

The churn hotspot is not missing MMIO behavior. The hotspot is reminder drift.

Current shared reminder surfaces still describe the MMIO packet mostly through the helper file, the verify helper, the apply-observation replay pair, the survey gate, and the manifest, while undercounting the two shipped wrapper files themselves:
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`
- the shared reminder checker `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`

That undercount matters because the roadmap-backed packet is wrapper-first, and these two files are not speculative scaffolding anymore. They are already part of current repo reality and should be kept explicit by the same shared reminder surfaces that describe the rest of the MMIO packet.

## Why this is the right bounded cleanup target

This is the smallest same-lane truthfulness repair because it:
- stays inside Phase 10 MMIO reminder and validation surfaces
- avoids widening into transport-backed queue setup, IRQ delivery, DMA paths, or lifecycle work
- cleans up stale wrapper undercount rather than adding a new wrapper family
- gives the next run one exact reminder-stack follow-through instead of another broad survey pass

## Next same-lane step

Tighten one shared reminder packet at a time so the shipped MMIO wrapper files stop being implicit context and become explicit packet members in:
1. `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
2. `zigux/tests/README.md`
3. `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`

Keep that follow-through bounded to reminder text and checker truthfulness only. Do not widen the lane into MMIO behavior, transport execution, or freeze-boundary status changes.
