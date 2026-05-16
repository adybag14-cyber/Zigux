# Phase 10 virtio MMIO Config-Write Disposition Companion

This note records the bounded current-head readback for the latest `drivers/virtio/virtio_mmio.zig` config-write disposition helper.

## Status

- `PHASE10_STATUS=current_head_companion_landed`
- `PHASE10_FAMILY=virtio-mmio`
- `PHASE10_SURFACE=config-write-disposition-observation`
- `PHASE10_PROVENANCE_MODE=dated_master_readback`
- surveyed against current `master` readback on `2026-05-16`
- scope: document the helper-local disposition summary that now reports byte-level config-write deltas while keeping the broader MMIO lifecycle, IRQ, DMA, queue setup, and probe or remove packet blocked
- role: current-head truthfulness companion for the Phase 10 MMIO packet after the helper moved ahead of the older slice-step wording

## Why this companion exists

The Phase 10 roadmap still keeps `drivers/virtio/virtio_mmio.c` inside a risky transport family where honest progress is small, reviewable wrapper and validation surfaces rather than transport-backed queue setup, IRQ delivery, DMA, or lifecycle parity.

Current `master` now includes a newer helper-local rung in `drivers/virtio/virtio_mmio.zig`: `ConfigWriteDispositionSummary` and `configWriteDispositionSummary()` expose the staged config-write window with `relative_end_offset`, `absolute_end_offset`, `previous_value`, `planned_value`, `changed_byte_mask`, and `has_changes` while leaving the underlying config bytes unchanged.

The recent master history that introduced this helper did not move the broader MMIO review packet alongside it. The smallest honest follow-up is therefore a companion note that captures the live helper surface and its still-blocked boundary without pretending the full MMIO survey packet has already been reworked.

## Current Helper Surface

Current `master` readback shows the MMIO helper now includes:

- `ConfigWriteDispositionSummary` with start and end offsets for the staged config-write window
- `previous_value` and `planned_value` so a reviewer can compare the staged write against the existing config bytes
- `changed_byte_mask` so byte-level deltas are visible without replaying the full word manually
- `has_changes` derived from the actual byte-delta mask rather than a blanket true result
- generation-aware rejection through `error.ConfigWritePlanUnavailable` when no current staged plan is available
- helper-local replay coverage proving a one-byte delta, a no-op plan, stale-plan rejection after generation bump, and non-mutation of the config window

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

- `drivers/virtio/virtio_mmio.zig` now carries the richer config-write disposition observation helper
- the broader MMIO packet still needs a later packet-wide review refresh before it can claim fully aligned survey, closure, or lifecycle evidence for this rung
- the remaining roadmap-backed blocker in this family is still the larger lifecycle-and-IRQ transport surface, which is materially riskier than this helper-local observation step

## Safe Reading

Use this companion as the current-head explanation for the MMIO config-write disposition helper until the broader Phase 10 MMIO packet is refreshed in one coupled pass.

It should be read together with the existing MMIO slice and survey notes, not as a claim that those older packet surfaces have already been fully renumbered or rewritten.

## Next bounded step

Refresh one directly coupled Phase 10 MMIO review surface next so the packet catches up with the landed helper. The smallest honest follow-up is a survey or slice-note repair that names the disposition helper explicitly while keeping lifecycle-and-IRQ work blocked.
