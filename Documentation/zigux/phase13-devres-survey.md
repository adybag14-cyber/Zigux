# Phase 13 devres DMA and scatterlist Boundary Survey

This document records the bounded `P13-L07` survey lane around the current DMA and scatterlist boundary evidence for `lib/devres.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-dma-scatterlist-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-18`
- scope: the docs-side devres slice note, the planning-only `dmam_alloc_coherent()` note and manifest, the direct DMA-boundary replay, the helper-first scatterlist helper and replay, and the roadmap-backed `lib/devres.c` anchor
- product boundary:
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
  - `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `lib/devres_scatterlist.zig`
  - `zigux/tests/phase13_devres_scatterlist.zig`

## Why this survey exists

The Phase 13 roadmap keeps `lib/devres.c` in the shared-helper tranche, but current `master` no longer ships the broader direct helper packet that older Phase 13 lane memory described. The honest same-lane task is therefore not to pretend `lib/devres.zig` is back. It is to record what current `master` actually ships for the DMA and scatterlist boundary, keep the helper-first and planning-only posture explicit, and leave live DMA-backed behavior and live scatterlist ownership blocked until a later bounded helper lane lands real code.

## Survey findings

- `Documentation/zigux/phase13-devres-slice.md` keeps the roadmap anchor visible while explicitly treating `lib/devres.zig`, the older direct devres replay, the older reviewability gate, and the older manifest-backed packet as repo-reality gaps on current `master`.
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md` records the next honest DMA-local follow-on as a pure `dmam_alloc_coherent()` planning surface, not as live DMA allocation behavior.
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` marks the packet as `planning_only` and keeps `phase13-devres-live-dmam-alloc-side-effects` and `phase13-devres-live-scatterlist-ownership` blocked.
- `zigux/tests/phase13_devres_dma_coherent.zig` fail-closes on those blocked DMA and scatterlist boundaries and on the planner note keeping `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, and `sg_*` lifecycle ownership out of scope.
- `lib/devres_scatterlist.zig` now provides a helper-first scatterlist lifetime planner through `DevresScatterlistHelper.descriptor()`, `planManagedScatterlistMap(...)`, and `planManagedScatterlistUnmap(...)`, while keeping `.touches_live_dma = false` and `.touches_live_scatterlist = false`.
- `zigux/tests/phase13_devres_scatterlist.zig` replays that scatterlist helper surface directly and keeps the release-record-retention, release-record-free, allocation-failure, and exact-release-match cases reviewable without claiming live DMA mapping or `sg_table` lifecycle control.

## Exact live readback

- current `master` still ships `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig`.
- current `master` does not ship `lib/devres.zig`, `Documentation/zigux/phase13-devres-survey.md` before this repair, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`.
- the live `phase13_devres_dmam_alloc_coherent_planner_manifest.json` packet still records `"packet": "phase13-devres-dmam-alloc-coherent-planner"`, `"status": "planning_only"`, `"id": "phase13-devres-live-dmam-alloc-side-effects"`, and `"id": "phase13-devres-live-scatterlist-ownership"`.
- the live `phase13_devres_dma_coherent.zig` replay still requires the planner note to keep generic DMA mapping helpers and scatterlist lifecycle ownership blocked.
- the live `devres_scatterlist.zig` helper descriptor still marks `provides_scatterlist_lifetime_planning = true`, `touches_live_dma = false`, and `touches_live_scatterlist = false`.

## Recorded gaps

The current lane state is:

- landed `phase13-devres-dma-boundary-replay`
- landed `phase13-devres-dmam-alloc-coherent-planner-note`
- landed `phase13-devres-dmam-alloc-coherent-planner-manifest`
- landed `phase13-devres-scatterlist-helper`
- landed `phase13-devres-scatterlist-replay`
- landed `phase13-devres-dma-scatterlist-boundary-survey-note`
- blocked `phase13-devres-live-dmam-alloc-side-effects`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-sg-table-lifecycle`
- blocked `phase13-devres-generic-dma-map-family`
- blocked `phase13-devres-broader-direct-helper-packet`

This keeps the lane honest: current `master` has real bounded DMA and scatterlist boundary evidence, but it still does not claim live DMA allocation side effects, generic DMA mapping ownership, live scatterlist ownership, `sg_table` lifecycle control, or the older broader `lib/devres.zig` helper packet.

## Non-goals

This survey does not claim:

- `lib/devres.zig` already landed on current `master`
- live `dmam_alloc_coherent()` side effects
- generic `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, or `dma_map_sgtable()` ownership
- live scatterlist ownership or `sg_table` lifecycle control
- IOMMU state, DMA attributes, or device-managed pool mutation
- wider devres group teardown parity

## Next bounded step

If this survey lane reopens, first compare `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` together on current `master` before widening anything else. Only rematerialize the broader direct helper packet if those same-lane surfaces and the roadmap evidence support it together.
