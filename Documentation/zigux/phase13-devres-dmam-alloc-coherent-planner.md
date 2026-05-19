# Phase 13 devres dmam_alloc_coherent Planner

This bounded `P13-L08` helper-first packet lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig` while keeping live DMA state, scatterlist ownership, and broader devres-group behavior blocked.

The planner stays intentionally narrow:
- routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)` so the release-record ownership rule is reviewable as its own shared helper step
- routes `planManagedDmamFreeCoherent(...)` through one private `planReleaseCall(...)` helper so detach cleanup review stays aligned with the retained release-record path
- accepts already-decided allocation inputs rather than talking to live hardware state
- records whether a successful planned coherent allocation retains detach-time cleanup ownership on success
- turns that successful allocation plan into explicit detach cleanup planning through `planManagedDmamFreeCoherent(...)`
- records whether that planned coherent free consumes the retained release record and releases the allocation from devres
- records whether a failed allocation frees the release record and avoids retaining detach-time cleanup ownership
- keeps `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, and `sg_*` lifecycle ownership out of scope
- does not claim live DMA allocation side effects, IOMMU state, DMA attributes, device-managed pool mutation, or wider devres group teardown behavior

The helper packet now consists of:
- `lib/devres.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`

Fixture governance stays helper-local:
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` owns the retained-release-record, freed-release-record, missing-release-record, and detach-cleanup fixture coverage for `planManagedReleaseRecordLifetime(...)`, `planManagedDmamAllocCoherent(...)`, and `planManagedDmamFreeCoherent(...)`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` is the packet-local owner map for that fixture and should stay aligned with the helper and planner replay
- `zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only and does not own the release-record lifetime or detach-cleanup fixture for this planner packet

Adjacent boundary evidence stays unchanged:
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `zigux/tests/phase13_devres_dma_coherent.zig`

Standalone replay handles:
- `zig test --dep devres -Mroot=zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig -Mdevres=lib/devres.zig`
- `zig test zigux/tests/phase13_devres_dma_coherent.zig`