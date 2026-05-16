# Phase 10 Virtio MMIO Survey

This document records the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-survey`
- lane family: `Phase 10 virtio MMIO`
- surveyed against current `master` readback on `2026-05-16`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the current `drivers/virtio/virtio_mmio.zig` helper surface reviewable without claiming transport-backed queue setup, IRQ delivery, DMA, or probe/remove lifecycle parity
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`
  - `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 10 roadmap keeps `drivers/virtio/virtio_mmio.c` inside the VM-friendly lab-driver stage. In that stage, honest progress is bounded wrapper and validation work, not transport-backed lifecycle claims.

Current `master` already contains a real helper foothold in `drivers/virtio/virtio_mmio.zig`. The current helper packet covers transport identity readback, probe preflight gating, selected-queue readiness, staged config-write planning, and the newer config-write disposition summary that reports byte-level deltas without mutating the staged config window.

This survey exists to make that current helper packet explicit and reviewable on its own terms while keeping the larger risky transport bridge parked.

## Survey findings
- `drivers/virtio/virtio_mmio.zig` is present on current `master` and exposes `TransportIdentitySummary`, `ProbePreflightSummary`, `SelectedQueueReadinessSummary`, `ConfigWritePlanSummary`, `ConfigWriteDispositionSummary`, and `FeatureNegotiationSummary` as bounded MMIO lab surfaces.
- `VirtioMmioLab` stays in-memory and lab-oriented: it stages config bytes and feature words, tracks queue selection and queue readiness, and reports helper summaries without claiming a live hardware transport.
- the config-write disposition helper now reports `relative_end_offset`, `absolute_end_offset`, `previous_value`, `planned_value`, `changed_byte_mask`, and `has_changes`, which makes a staged config-window change reviewable at byte granularity.
- the helper-local tests inside `drivers/virtio/virtio_mmio.zig` cover stale-plan invalidation after a config-generation bump, stale-plan invalidation after config-byte restaging, legacy guest-page-size probe gating, and non-mutating config-write disposition reporting.
- `zigux/tests/phase10_build.zig` remains part of the shared Phase 10 review packet, and current `master` now wires the helper-local MMIO tests there by importing `drivers/virtio/virtio_mmio.zig` into the shared build gate beside the input-side queue-handling packet. A separate dedicated `phase10_virtio_mmio` replay step is still not materialized in that shared build route, so the current shared gate should be read as helper-local MMIO coverage rather than a broader transport-backed replay.
- `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md` remains the packet-local companion for the newest config-write disposition rung and should stay aligned with this broader survey note.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` remains the governing boundary note for this survey.
- this survey stays inside `drivers/virtio/*.zig` and shared validation surfaces.
- this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.
- this survey also does not claim ownership of the freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`.

## Non-goals
This survey does not claim:
- transport-backed queue setup or queue reset execution
- shared IRQ delivery parity
- DMA-facing behavior
- probe, remove, freeze, restore, or device-lifecycle closure
- an Architecture Council reopen or a freeze-map status change

## Gates
Current `master` keeps this MMIO lane reviewable through these bounded surfaces:
1. helper-local tests inside `drivers/virtio/virtio_mmio.zig`
2. `zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10` remain shared Phase 10 reminder routes, and the current build file now runs the helper-local MMIO tests through `drivers/virtio/virtio_mmio.zig` beside the input-side queue-handling packet even though it still does not materialize a separate dedicated `phase10_virtio_mmio` replay step

These gates should be read as helper-local review evidence and shared packet reminders only, not as proof of a transport-backed MMIO driver or a dedicated MMIO replay.

## Next bounded step
Keep the broader Phase 10 MMIO lane parked unless fresh repo inspection finds one directly coupled follow-through. The next honest same-lane step is to align one additional MMIO packet surface around the landed helper packet while keeping lifecycle-and-IRQ transport work blocked.
