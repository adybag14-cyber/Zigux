# Phase 13 devres DMA, scatterlist, and MMIO Boundary Survey

This document records the bounded `P13-L01` survey lane around the current `lib/devres.c` helper packet on `master`: the shipped DMA and scatterlist boundary evidence, plus the still-missing MMIO and iomap safety gaps that remain open against the Phase 13 roadmap.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-mmio-dma-scatterlist-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-21`
- scope: the docs-side devres slice note, the dedicated `dmam_alloc_coherent()` helper and replay, the planning notes and manifests, the direct DMA-boundary replay, the helper-first scatterlist helper and replay, the dedicated scatterlist helper slice and build shard, the dedicated MMIO packet checker, the roadmap-backed `lib/devres.c` anchor, and the missing MMIO or iomap helper-first packet that this lane still has to keep visible
- product boundary:
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
  - `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
  - `Documentation/zigux/phase13-devres-scatterlist-planner.md`
  - `Documentation/zigux/phase13-devres-scatterlist-slice.md`
  - `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`
  - `lib/devres.zig`
  - `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `lib/devres_scatterlist.zig`
  - `zigux/tests/phase13_devres_scatterlist.zig`
  - `zigux/tests/phase13_devres_scatterlist_build.zig`
  - `scripts/zigux/check-phase13-devres-mmio-packet.py`

## Why this survey exists

The Phase 13 roadmap still keeps `lib/devres.c` in the shared-helper tranche, and that means the survey has to stay honest about two things at once:

- what current `master` really ships today for helper-first DMA and scatterlist boundary evidence
- which MMIO and iomap safety helpers are still missing from the live `lib/devres.zig` packet even though the roadmap-backed devres lane still needs those gaps kept visible

The honest same-lane task is therefore not to pretend the wider direct helper packet has come back. It is to record the shipped DMA and scatterlist planner surfaces, fail closed on the blocked live DMA and scatterlist ownership boundaries, and explicitly keep the missing MMIO or iomap helper family visible as a repo-reality gap instead of letting the survey collapse into adjacent DMA-only ownership.

## Survey findings

- `Documentation/zigux/phase13-devres-slice.md` keeps the roadmap anchor visible while explicitly treating only the broader direct devres replay, older reviewability gate, older manifest-backed packet, and older packet-alignment checker as repo-reality gaps on current `master`.
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md` records a landed pure `dmam_alloc_coherent()` planning surface instead of only a future note.
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` marks the packet as `starter_landed` while keeping `phase13-devres-live-dmam-alloc-side-effects` and `phase13-devres-live-scatterlist-ownership` blocked.
- `Documentation/zigux/phase13-devres-scatterlist-planner.md` records a landed pure scatterlist lifetime planning surface instead of leaving that helper as adjacent evidence only.
- `Documentation/zigux/phase13-devres-scatterlist-slice.md` and `zigux/tests/phase13_devres_scatterlist_build.zig` keep the dedicated scatterlist planner shard reviewable as part of the same bounded packet instead of leaving that helper-first companion implicit.
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json` marks the packet as `starter_landed` while keeping `phase13-devres-live-scatterlist-ownership`, `phase13-devres-live-sg-table-lifecycle`, and `phase13-devres-generic-dma-map-family` blocked.
- `lib/devres.zig` ships a pure `dmam_alloc_coherent()` planning surface through `DevresHelperLab.descriptor()`, `planManagedReleaseRecordLifetime(...)`, `planManagedDmamAllocCoherent(...)`, and `planManagedDmamFreeCoherent(...)`, while keeping `.touches_live_dma = false` and `.touches_live_scatterlist = false`.
- helper-source readback shows `lib/devres.zig` still omits live `dmam_alloc_coherent()`, `dmam_free_coherent()`, generic `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, and `sg_init_table()` ownership markers.
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` replays that helper directly and keeps the retained-release-record, explicit detach-cleanup, freed-release-record, and missing-release-record cases reviewable without claiming live DMA allocation side effects.
- `zigux/tests/phase13_devres_dma_coherent.zig` continues to fail closed on generic DMA and scatterlist ownership boundaries beside the new helper-first planner.
- `lib/devres_scatterlist.zig` ships helper-first scatterlist lifetime planning through `planManagedScatterlistMap(...)`, `scatterlistReleaseMatches(...)`, and `planManagedScatterlistUnmap(...)`, and `zigux/tests/phase13_devres_scatterlist.zig` replays retained-release-record success, freed-release-record fallback, release-record-allocation failure, exact release-match behavior, and the dedicated planner note or manifest packet without widening into live DMA mapping or `sg_table` lifecycle control.
- helper-source readback shows `lib/devres_scatterlist.zig` still omits live `sg_alloc_table()`, `sg_free_table()`, `sg_dma_address()`, `sg_dma_len()`, `dma_map_sg()`, `dma_unmap_sg()`, and `dma_map_sgtable()` ownership markers, so the current scatterlist slice remains planner-only.
- `scripts/zigux/check-phase13-devres-mmio-packet.py` now fail-closes on the survey note, slice note, planner note, scatterlist slice, helper manifests, focused replays, helper-local MMIO absences, and the scatterlist build shard so the missing MMIO and iomap gaps cannot silently disappear from current `master`.
- helper-source readback also shows that current `master` still ships no MMIO or iomap helper-first surface in `lib/devres.zig`: there are no `devm_iounmap(`, `devm_ioremap_np(`, `devm_of_iomap(`, `devm_arch_phys_wc_add(`, or `devm_arch_io_reserve_memtype_wc(` markers in the live helper file.
- current `master` likewise ships no dedicated MMIO-facing replay or manifest packet alongside the current DMA planner packet: `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` remain absent, so the survey has to keep those MMIO and iomap safety surfaces framed as missing roadmap gaps rather than implied shipped coverage.

## Exact live readback

- current `master` now ships `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `scripts/zigux/check-phase13-devres-mmio-packet.py`.
- current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`.
- the live `phase13_devres_dmam_alloc_coherent_planner_manifest.json` packet records `"packet": "phase13-devres-dmam-alloc-coherent-planner"`, `"status": "starter_landed"`, `planManagedReleaseRecordLifetime`, `planManagedDmamFreeCoherent`, `release_record_consumed`, `"id": "phase13-devres-live-dmam-alloc-side-effects"`, and `"id": "phase13-devres-live-scatterlist-ownership"`.
- the live `phase13_devres_scatterlist_planner_manifest.json` packet records `"packet": "phase13-devres-scatterlist-planner"`, `"status": "starter_landed"`, `planManagedScatterlistMap`, `scatterlistReleaseMatches`, `planManagedScatterlistUnmap`, `"id": "phase13-devres-live-scatterlist-ownership"`, `"id": "phase13-devres-live-sg-table-lifecycle"`, and `"id": "phase13-devres-generic-dma-map-family"`.
- the live `phase13_devres_dmam_alloc_coherent_planner.zig` replay checks that `lib/devres.zig` keeps `provides_dmam_alloc_coherent_planning = true`, `.touches_live_dma = false`, and `.touches_live_scatterlist = false`.
- the live `phase13_devres_dma_coherent.zig` replay still requires the planner notes to keep generic DMA mapping helpers and scatterlist lifecycle ownership blocked.
- helper-source readback shows `lib/devres.zig` keeps the boundary planning-only: it contains `planManagedDmamAllocCoherent`, `planManagedDmamFreeCoherent`, `.touches_live_dma = false`, and `.touches_live_scatterlist = false`, but omits live `dmam_alloc_coherent()`, `dmam_free_coherent()`, generic `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, and `sg_init_table()` markers.
- helper-source readback also shows that `lib/devres.zig` omits the MMIO and iomap safety family markers `devm_iounmap(`, `devm_ioremap_np(`, `devm_of_iomap(`, `devm_arch_phys_wc_add(`, and `devm_arch_io_reserve_memtype_wc(`.
- the live `devres_scatterlist.zig` helper descriptor still marks `provides_scatterlist_lifetime_planning = true`, `touches_live_dma = false`, and `touches_live_scatterlist = false`, and the helper body stays bounded to `planManagedScatterlistMap`, `scatterlistReleaseMatches`, and `planManagedScatterlistUnmap` while omitting live `sg_alloc_table()`, `sg_free_table()`, `sg_dma_address()`, `sg_dma_len()`, `dma_map_sg()`, `dma_unmap_sg()`, and `dma_map_sgtable()` ownership.
- the live `check-phase13-devres-mmio-packet.py` packet guard requires the survey note, slice note, planner note, scatterlist slice, planner manifest, focused replays, helper-local MMIO absences, scatterlist helper markers, and scatterlist build shard to agree before the bounded MMIO packet can pass.

## Recorded gaps

The current lane state is:

- landed `phase13-devres-dmam-alloc-coherent-helper`
- landed `phase13-devres-dmam-alloc-coherent-replay`
- landed `phase13-devres-dmam-alloc-coherent-planner-note`
- landed `phase13-devres-dmam-alloc-coherent-planner-manifest`
- landed `phase13-devres-dmam-free-coherent-cleanup-planner`
- landed `phase13-devres-dma-boundary-replay`
- landed `phase13-devres-scatterlist-helper`
- landed `phase13-devres-scatterlist-replay`
- landed `phase13-devres-scatterlist-planner-note`
- landed `phase13-devres-scatterlist-planner-manifest`
- landed `phase13-devres-dma-scatterlist-boundary-survey-note`
- blocked `phase13-devres-live-dmam-alloc-side-effects`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-sg-table-lifecycle`
- blocked `phase13-devres-generic-dma-map-family`
- blocked `phase13-devres-missing-devm-iounmap-surface`
- blocked `phase13-devres-missing-devm-ioremap-np-surface`
- blocked `phase13-devres-missing-devm-of-iomap-surface`
- blocked `phase13-devres-missing-devm-arch-phys-wc-add-surface`
- blocked `phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface`
- blocked `phase13-devres-live-mmio-mapping-state`
- blocked `phase13-devres-live-device-tree-walks`
- blocked `phase13-devres-live-arch-memtype-mutation`
- blocked `phase13-devres-broader-direct-helper-packet`

This keeps the lane honest: current `master` has real bounded DMA and scatterlist boundary evidence plus one narrow helper-first `dmam_alloc_coherent()` planner with explicit detach cleanup planning and one dedicated helper-first scatterlist planner packet with exact release-match reviewability, but it still does not claim live DMA allocation side effects, generic DMA mapping ownership, live scatterlist ownership, `sg_table` lifecycle control, helper-first MMIO or iomap planners, live MMIO mappings, device-tree walks, arch memtype mutation, or the older broader direct helper packet.

## Non-goals

This survey does not claim:

- the broader direct `phase13_devres` replay already landed on current `master`
- live `dmam_alloc_coherent()` side effects
- generic `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, or `dma_map_sgtable()` ownership
- live scatterlist ownership or `sg_table` lifecycle control
- shipped `sg_alloc_table()`, `sg_free_table()`, `sg_dma_address()`, `sg_dma_len()`, `dma_map_sg()`, or `dma_unmap_sg()` ownership
- shipped `devm_iounmap()`, `devm_ioremap_np()`, `devm_of_iomap()`, `devm_arch_phys_wc_add()`, or `devm_arch_io_reserve_memtype_wc()` helper surfaces
- live MMIO mapping state, device-tree walks, or arch memtype mutation
- IOMMU state, DMA attributes, or device-managed pool mutation
- wider devres group teardown parity

## Next bounded step

If this survey lane reopens, first compare `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `scripts/zigux/check-phase13-devres-mmio-packet.py` together on current `master` before widening anything else. Only rematerialize the broader direct helper packet or any MMIO-facing helper slice if those same-lane surfaces and the roadmap evidence support it together.