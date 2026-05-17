# Phase 10 virtio MMIO Config-Write Disposition Companion

This note records the bounded current-head readback for the latest `drivers/virtio/virtio_mmio.zig` config-write disposition helper.

## Status

- `PHASE10_STATUS=current_head_companion_landed`
- `PHASE10_FAMILY=virtio-mmio`
- `PHASE10_SURFACE=config-write-disposition-observation`
- `PHASE10_PROVENANCE_MODE=dated_master_readback`
- surveyed against current `master` readback on `2026-05-17`
- scope: document the helper-local disposition summary that reports byte-level config-write deltas while keeping the broader MMIO lifecycle, IRQ, DMA, queue setup, and probe or remove packet blocked
- role: packet-local current-head companion for the Phase 10 MMIO packet, aligned with the live MMIO survey while keeping the byte-level disposition rung explicit on its own terms

## Why this companion exists

The Phase 10 roadmap still keeps `drivers/virtio/virtio_mmio.c` inside a risky transport family where honest progress is small, reviewable wrapper and validation surfaces rather than transport-backed queue setup, IRQ delivery, DMA, or lifecycle parity.

Current `master` includes a newer helper-local rung in `drivers/virtio/virtio_mmio.zig`: `ConfigWriteDispositionSummary` and `configWriteDispositionSummary()` expose the staged config-write window with `relative_end_offset`, `absolute_end_offset`, `previous_value`, `planned_value`, `changed_byte_mask`, and `has_changes` while leaving the underlying config bytes unchanged.

The broader MMIO survey packet now names that helper and keeps its blocked boundary explicit, so this companion no longer serves as a catch-up note for a stale survey. Instead, it stays as the packet-local detail surface for the byte-level disposition rung while the riskier lifecycle-and-IRQ transport work remains parked.

## Current Helper Surface

Current `master` readback shows the MMIO helper now includes:

- `ConfigWriteDispositionSummary` with start and end offsets for the staged config-write window
- `previous_value` and `planned_value` so a reviewer can compare the staged write against the existing config bytes
- `changed_byte_mask` so byte-level deltas are visible without replaying the full word manually
- `has_changes` derived from the actual byte-delta mask rather than a blanket true result
- generation-aware rejection through `error.ConfigWritePlanUnavailable` when no current staged plan is available
- helper-local replay coverage proving a one-byte delta, a no-op plan, stale-plan rejection after generation bump, stale-plan rejection after config-byte restaging, and non-mutation of the config window

## Boundary Kept Honest

This helper still does not claim:

- transport-backed writes into a live MMIO config window
- queue discovery or queue execution parity
- shared interrupt delivery parity
- DMA-facing behavior
- probe, remove, freeze, restore, or device-lifecycle closure

The helper remains planning-only and observation-only. It surfaces what a staged write would touch without claiming that the write executed against hardware.

## Current Repo Reality

The current MMIO family is still best read as a bounded lab helper packet:

- `drivers/virtio/virtio_mmio.zig` carries the richer config-write disposition observation helper
- `drivers/virtio/virtio_mmio_verify.zig` keeps the changed-byte-count and queue-readiness wrapper proof explicit beside the helper
- `Documentation/zigux/phase10-virtio-mmio-survey.md` now names the disposition helper and the same blocked lifecycle-and-IRQ boundary
- `zigux/tests/phase10_build.zig` still imports `drivers/virtio/virtio_mmio.zig` into the shared Phase 10 build gate for helper-local MMIO coverage
- repeated authenticated contents reads still return missing for `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/tests/phase10_virtio_mmio_manifest.json`, so keep those adjacent MMIO packet members framed as repo-reality gaps until a fresh reread proves they materialize again

## Safe Reading

Use this companion as the packet-local explanation for the MMIO config-write disposition helper together with the live MMIO survey, the direct helper file, the verify wrapper, and the shared Phase 10 build gate.

It should not be read as a claim that the MMIO lane has crossed into transport-backed writes, queue execution, IRQ delivery, DMA, or lifecycle closure.

## Next bounded step

Keep the broader Phase 10 MMIO lane parked unless fresh repo inspection finds one directly coupled follow-through. The next honest same-lane step is one additional packet-local or shared reminder surface repair around the already-landed MMIO helper packet while lifecycle-and-IRQ transport work stays blocked.
