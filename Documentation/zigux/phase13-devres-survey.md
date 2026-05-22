# Phase 13 devres DMA, scatterlist, and MMIO Boundary Survey

This document records the bounded `P13-L01` survey lane around the current `lib/devres.c` helper packet on `master`: the shipped DMA, scatterlist, helper-first iounmap, and helper-first iomap planning evidence, plus the still-missing non-posted wrapper and arch-memtype safety gaps that remain open against the Phase 13 roadmap.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-mmio-dma-scatterlist-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-22`
- scope: the docs-side devres slice note, the dedicated `dmam_alloc_coherent()` helper and replay, the planning notes and manifests, the direct DMA-boundary replay, the helper-first scatterlist helper and replay, the helper-first `devm_iounmap()` cleanup planner, the helper-first `devm_of_iomap()` planner, the dedicated DMA-boundary checker, the dedicated MMIO packet checker, the roadmap-backed `lib/devres.c` anchor, and the still-missing non-posted or arch-memtype helper packet that this lane still has to keep visible

## Why this survey exists

The Phase 13 roadmap still keeps `lib/devres.c` in the shared-helper tranche, and that means the survey has to stay honest about two things at once:

- what current `master` really ships today for helper-first DMA, scatterlist, iounmap, and iomap planning evidence
- which MMIO, non-posted wrapper, and arch-memtype safety helpers are still missing from the live `lib/devres.zig` packet even though the roadmap-backed devres lane still needs those gaps kept visible

The honest same-lane task is therefore not to pretend the wider direct helper packet has come back. It is to record the shipped DMA, scatterlist, iounmap, and iomap planner surfaces, fail closed on the blocked live DMA and scatterlist ownership boundaries, and explicitly keep the missing non-posted or arch-memtype helper family visible as a repo-reality gap instead of letting the survey collapse into adjacent DMA-only ownership.

## Survey findings

- `Documentation/zigux/phase13-devres-slice.md` keeps the roadmap anchor visible while explicitly treating only the broader direct devres replay, older reviewability gate, older manifest-backed packet, and older packet-alignment checker as repo-reality gaps on current `master`.
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md` records a landed pure `dmam_alloc_coherent()` planning surface instead of only a future note.
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` marks the packet as `starter_landed` while keeping `phase13-devres-live-dmam-alloc-side-effects` and `phase13-devres-live-scatterlist-ownership` blocked.
- `Documentation/zigux/phase13-devres-scatterlist-planner.md` records a landed pure scatterlist lifetime planning surface instead of leaving that helper as adjacent evidence only.
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json` marks the packet as `starter_landed` while keeping `phase13-devres-live-scatterlist-ownership`, `phase13-devres-live-sg-table-lifecycle`, and `phase13-devres-generic-dma-map-family` blocked.
- `Documentation/zigux/phase13-devres-iounmap-planner.md` records a landed pure `devm_iounmap()` cleanup planning surface instead of leaving MMIO cleanup entirely in the gap list.
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json` marks the packet as `starter_landed` while keeping the remaining non-posted, arch-memtype, and live-MMIO boundaries blocked.
- `Documentation/zigux/phase13-devres-iomap-planner.md` records a landed pure `devm_of_iomap()` planning surface instead of leaving iomap reviewability entirely in the gap list.
- `zigux/tests/phase13_devres_iomap_planner_manifest.json` marks the packet as `starter_landed` while keeping the remaining non-posted, arch-memtype, and live-MMIO boundaries blocked.
- `lib/devres.zig` ships a pure `dmam_alloc_coherent()` planning surface through `DevresHelperLab.descriptor()`, `planManagedReleaseRecordLifetime(...)`, `planManagedDmamAllocCoherent(...)`, and `planManagedDmamFreeCoherent(...)`, plus helper-first iomap planning through `planDeviceTreeIomap(...)` and helper-first iounmap cleanup planning through `planManagedIounmapCleanup(...)`, while keeping `.touches_live_dma = false`, `.touches_live_scatterlist = false`, and `.touches_live_mmio = false`.
- helper-source readback shows `lib/devres.zig` still omits live `dmam_alloc_coherent()`, `dmam_free_coherent()`, generic `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, `sg_init_table()`, `devm_ioremap_np(`, `devm_of_iomap(`, `devm_arch_phys_wc_add(`, and `devm_arch_io_reserve_memtype_wc(` markers.
- `zigux/tests/phase13_devres_iomap_planner.zig` replays the helper-first iomap surface directly and keeps the translation-miss, request-region-denial, and remap-failure cases reviewable without claiming live MMIO mapping side effects or device-tree walks.
- `zigux/tests/phase13_devres_iounmap_planner.zig` replays the helper-first iounmap cleanup surface directly and keeps the tracked-mapping, missing-release-record, and no-mapping cases reviewable without claiming live MMIO mapping side effects.
- `scripts/zigux/check-phase13-devres-mmio-packet.py` now fail-closes on the same helper-first iomap and iounmap packet surfaces that the survey records, while `scripts/zigux/check-phase13-devres-iomap-planner.py` and `scripts/zigux/check-phase13-devres-iounmap-planner.py` keep those helper-first MMIO packets aligned around their helpers, notes, manifests, and replays.

## Exact live readback

- current `master` now ships `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner.zig`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, and `scripts/zigux/check-phase13-devres-mmio-packet.py`.
- current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`.
- the live `phase13_devres_iomap_planner_manifest.json` packet records `"packet": "phase13-devres-iomap-planner"`, `"status": "starter_landed"`, `planDeviceTreeIomap`, `"id": "phase13-devres-missing-devm-ioremap-np-surface"`, `"id": "phase13-devres-missing-devm-arch-phys-wc-add-surface"`, `"id": "phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface"`, `"id": "phase13-devres-live-mmio-mapping-state"`, `"id": "phase13-devres-live-device-tree-walks"`, and `"id": "phase13-devres-live-arch-memtype-mutation"`.

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
- landed `phase13-devres-iounmap-planner-note`
- landed `phase13-devres-iounmap-planner-manifest`
- landed `phase13-devres-iounmap-planner-replay`
- landed `phase13-devres-iomap-planner-note`
- landed `phase13-devres-iomap-planner-manifest`
- landed `phase13-devres-iomap-planner-replay`
- blocked `phase13-devres-live-dmam-alloc-side-effects`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-sg-table-lifecycle`
- blocked `phase13-devres-generic-dma-map-family`
- blocked `phase13-devres-missing-devm-ioremap-np-surface`
- blocked `phase13-devres-missing-devm-arch-phys-wc-add-surface`
- blocked `phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface`
- blocked `phase13-devres-live-mmio-mapping-state`
- blocked `phase13-devres-live-device-tree-walks`
- blocked `phase13-devres-live-arch-memtype-mutation`
- blocked `phase13-devres-broader-direct-helper-packet`

This keeps the lane honest: current `master` has real bounded DMA, scatterlist, iounmap, and iomap planning evidence, but it still does not claim live DMA allocation side effects, generic DMA mapping ownership, live scatterlist ownership, `sg_table` lifecycle control, helper-first non-posted or arch-memtype planners, live MMIO mappings, live device-tree walks, arch memtype mutation, or the older broader direct helper packet.

## Next bounded step

If this survey lane reopens, first compare `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres_iomap_planner.zig`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, and `scripts/zigux/check-phase13-devres-mmio-packet.py` together on current `master` before widening anything else. Only rematerialize a helper-first non-posted or arch-memtype planner if those same-lane surfaces and the roadmap evidence support it together.
