# Phase 13 devres scatterlist Planner

This bounded `P13-L08` helper-first packet lands one pure scatterlist lifetime planning surface in `lib/devres_scatterlist.zig` while keeping live DMA mapping state, live scatterlist ownership, `sg_table` lifecycle control, and broader devres-group behavior blocked.

The planner stays intentionally narrow:
- routes `planManagedScatterlistMap(...)` through one helper-local release-record outcome so retained cleanup ownership stays reviewable as its own shared helper step
- keeps the mapped-segment readiness rule explicit by requiring a positive mapped count that does not exceed the original segment count
- records whether a successful planned scatterlist map retains detach-time unmap ownership on success
- records whether failed mapping frees the release record and avoids retaining detach-time unmap ownership
- records whether impossible over-mapped scatterlist results free the release record and avoid retaining detach-time unmap ownership
- routes `planManagedScatterlistUnmap(...)` through exact original-entry and mapped-entry matching so release drift stays reviewable without claiming live unmap side effects
- records whether a release-count mismatch surfaces a warn-on-release-miss outcome without claiming live unmap side effects
- exposes `scatterlistReleaseMatches(...)` as the helper-first exact-match check rather than folding that policy into broader runtime ownership
- routes `planManagedScatterlistTableTeardown(...)` through initialized-table, release-record, and mapped-count gating so helper-first `sg_table` free eligibility stays reviewable without claiming live `sg_free_table()` side effects
- records whether an initialized table becomes free-ready once mapped entries drain to zero and the release record is still present
- records whether mapped scatterlist state still requires unmap-before-free planning instead of claiming live table teardown
- records whether missing release records or over-mapped counts warn rather than claiming live `sg_table` lifecycle mutation
- keeps `sg_alloc_table()`, `sg_free_table()`, `sg_dma_address()`, `sg_dma_len()`, `dma_map_sg()`, `dma_unmap_sg()`, `dma_map_sgtable()`, and `sg_table` lifecycle ownership out of scope
- does not claim live DMA mapping side effects, scatterlist ownership mutation, IOMMU state, DMA attributes, or wider devres group teardown behavior

The helper packet now consists of:
- `lib/devres_scatterlist.zig`
- `Documentation/zigux/phase13-devres-scatterlist-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `scripts/zigux/check-phase13-devres-scatterlist-planner.py`

Fixture governance stays helper-local:
- `zigux/tests/phase13_devres_scatterlist.zig` owns the retained-release-record, freed-release-record, impossible-overmapped-request, missing-release-record, exact-release-match, warn-on-release-miss, free-ready-teardown, unmap-before-free, and overmapped-teardown-warning fixture coverage for `planManagedScatterlistMap(...)`, `scatterlistReleaseMatches(...)`, `planManagedScatterlistUnmap(...)`, and `planManagedScatterlistTableTeardown(...)`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md` keeps the helper-local scope and non-goals aligned with this planner note, the manifest, and the replay
- `zigux/tests/phase13_devres_scatterlist_build.zig` keeps the dedicated build shard aligned with the helper-first scatterlist replay
- `scripts/zigux/check-phase13-devres-scatterlist-planner.py` is the packet-local validation guard for the helper, slice, note, manifest, build shard, and replay
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json` is the packet-local owner map for that fixture set and should stay aligned with the helper, checker, slice, build shard, and scatterlist replay
- `zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only and does not own the helper-local scatterlist fixture packet
- `Documentation/zigux/phase13-devres-survey.md` remains adjacent boundary evidence only and does not own the helper-local scatterlist fixture packet

Standalone replay handles:
- `zig test --dep devres_scatterlist -Mroot=zigux/tests/phase13_devres_scatterlist.zig -Mdevres_scatterlist=lib/devres_scatterlist.zig`
- `zig build test --build-file zigux/tests/phase13_devres_scatterlist_build.zig`
- `python3 scripts/zigux/check-phase13-devres-scatterlist-planner.py`
- `python3 scripts/zigux/check-phase13-devres-scatterlist-planner.py --self-test`
- `zig test zigux/tests/phase13_devres_dma_coherent.zig`
