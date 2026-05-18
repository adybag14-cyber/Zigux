# Phase 13 devres DMA and scatterlist Boundary Survey

This document records the bounded `P13-L07` survey lane around the current DMA and scatterlist boundary evidence for `lib/devres.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-dma-scatterlist-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-18`
- scope: the docs-side devres slice note, the dedicated `dmam_alloc_coherent()` helper and replay, the planning note and manifest, the direct DMA-boundary replay, the helper-first scatterlist helper and replay, and the roadmap-backed `lib/devres.c` anchor
- product boundary:
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
  - `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
  - `lib/devres.zig`
  - `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `lib/devres_scatterlist.zig`
  - `zigux/tests/phase13_devres_scatterlist.zig`

## Why this survey exists

The Phase 13 roadmap keeps `lib/devres.c` in the shared-helper tranche, but current `master` still does not ship the broader direct helper packet that older Phase 13 lane memory described. The honest same-lane task is therefore not to pretend the wide packet is back. It is to record what current `master` actually ships for the DMA and scatterlist boundary, keep the helper-first and planning-only posture explicit, and leave live DMA-backed behavior and live scatterlist ownership blocked until later bounded helper lanes land real code.

## Survey findings

- `Documentation/zigux/phase13-devres-slice.md` keeps the roadmap anchor visible while explicitly treating only the broader direct devres replay, older reviewability gate, older manifest-backed packet, and older packet-alignment checker as repo-reality gaps on current `master`.
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md` now records a landed pure `dmam_alloc_coherent()` planning surface instead of only a future note.
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` marks the packet as `starter_landed` while keeping `phase13-devres-live-dmam-alloc-side-effects` and `phase13-devres-live-scatterlist-ownership` blocked.
- `lib/devres.zig` now ships a pure `dmam_alloc_coherent()` planning surface through `DevresHelperLab.descriptor()`, `planManagedReleaseRecordLifetime(...)`, and `planManagedDmamAllocCoherent(...)`, while keeping `.touches_live_dma = false` and `.touches_live_scatterlist = false`.
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` replays that helper directly and keeps the retained-release-record, freed-release-record, and missing-release-record cases reviewable without claiming live DMA allocation side effects.
- `zigux/tests/phase13_devres_dma_coherent.zig` continues to fail-close on generic DMA and scatterlist ownership boundaries beside the new helper-first planner.
- `lib/devres_scatterlist.zig` and `zigux/tests/phase13_devres_scatterlist.zig` keep the helper-first scatterlist lifetime slice reviewable without widening into live DMA mapping or `sg_table` lifecycle control.

## Exact live readback

- current `master` now ships `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig`.
- current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`.
- the live `phase13_devres_dmam_alloc_coherent_planner_manifest.json` packet now records `"packet": "phase13-devres-dmam-alloc-coherent-planner"`, `"status": "starter_landed"`, `"planManagedReleaseRecordLifetime"`, `"id": "phase13-devres-live-dmam-alloc-side-effects"`, and `"id": "phase13-devres-live-scatterlist-ownership"`.
- the live `phase13_devres_dmam_alloc_coherent_planner.zig` replay now checks that `lib/devres.zig` keeps `provides_dmam_alloc_coherent_planning = true`, `.touches_live_dma = false`, and `.touches_live_scatterlist = false`.
- the live `phase13_devres_dma_coherent.zig` replay still requires the planner note to keep generic DMA mapping helpers and scatterlist lifecycle ownership blocked.
- the live `devres_scatterlist.zig` helper descriptor still marks `provides_scatterlist_lifetime_planning = true`, `touches_live_dma = false`, and `touches_live_scatterlist = false`.

## Recorded gaps

The current lane state is:

- landed `phase13-devres-dmam-alloc-coherent-helper`
- landed `phase13-devres-dmam-alloc-coherent-replay`
- landed `phase13-devres-dmam-alloc-coherent-planner-note`
- landed `phase13-devres-dmam-alloc-coherent-planner-manifest`
- landed `phase13-devres-dma-boundary-replay`
- landed `phase13-devres-scatterlist-helper`
- landed `phase13-devres-scatterlist-replay`
- landed `phase13-devres-dma-scatterlist-boundary-survey-note`
- blocked `phase13-devres-live-dmam-alloc-side-effects`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-sg-table-lifecycle`
- blocked `phase13-devres-generic-dma-map-family`
- blocked `phase13-devres-broader-direct-helper-packet`

This keeps the lane honest: current `master` has real bounded DMA and scatterlist boundary evidence plus one narrow helper-first `dmam_alloc_coherent()` planner, but it still does not claim live DMA allocation side effects, generic DMA mapping ownership, live scatterlist ownership, `sg_table` lifecycle control, or the older broader direct helper packet.

## Non-goals

This survey does not claim:

- the broader direct `phase13_devres` replay already landed on current `master`
- live `dmam_alloc_coherent()` side effects
- generic `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, or `dma_map_sgtable()` ownership
- live scatterlist ownership or `sg_table` lifecycle control
- IOMMU state, DMA attributes, or device-managed pool mutation
- wider devres group teardown parity

## Next bounded step

If this survey lane reopens, first compare `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` together on current `master` before widening anything else. Only rematerialize the broader direct helper packet if those same-lane surfaces and the roadmap evidence support it together.
