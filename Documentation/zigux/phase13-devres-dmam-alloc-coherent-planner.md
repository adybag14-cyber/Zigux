# Phase 13 devres dmam_alloc_coherent Planner

This bounded `P13-L08` planner packet records the next honest DMA-local follow-on for `lib/devres.c` after `zigux/tests/phase13_devres_dma_coherent.zig` materialized on current `master`, while `lib/devres.zig` itself remains an explicit repo-reality gap.

The planner stays intentionally narrow:
- it proposes only a pure `dmam_alloc_coherent()` planning surface for `lib/devres.zig`
- it keeps allocation outcome, release-record retention, and detach-time cleanup intent reviewable without claiming live DMA allocation side effects
- it treats the landed `zigux/tests/phase13_devres_dma_coherent.zig` replay as adjacent boundary proof, not as ownership of the new planner packet itself
- it keeps `dma_map_*`, `dma_unmap_*`, `dma_sync_*`, `dma_mmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, and `sg_*` lifecycle ownership out of scope
- it keeps IOMMU state, DMA attributes, device-managed pool mutation, and wider devres group teardown behavior out of scope
- it does not treat the replay as proof that `lib/devres.zig` or the older direct helper packet already landed on current `master`

The planner records the minimum reviewable contract for a future helper-first slice:
- accept already-decided allocation inputs rather than talking to live hardware state
- report whether the planned coherent allocation would retain cleanup ownership on success
- report whether a failed allocation would avoid retaining detach-time cleanup ownership
- keep scatterlist lifecycle and generic DMA mapping helpers blocked as adjacent follow-on work, not as part of this packet

Standalone replay for this planner packet:
- `zig test zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zig test zigux/tests/phase13_devres_dma_coherent.zig`
