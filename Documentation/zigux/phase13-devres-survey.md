# Phase 13 devres helper DMA/scatterlist boundary survey

This lane stays inside the Phase 13 shared-helper tranche and records the current `lib/devres.c` helper-first boundary without claiming live device-resource teardown, live MMIO mappings, live DMA-backed helpers, live scatter-gather ownership, or generic devres-group ownership.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-helper-dma-scatterlist-boundary-reviewability`
- `PHASE13_SURVEYED_COMMIT=aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb`
- scope: the landed `lib/devres.zig` helper slice, its dedicated Phase 13 tests and manifest, the shared Phase 13 build wiring, and the lane notes that keep the helper-first iomap or resource planners plus explicit DMA/scatterlist blockers pinned to the current repo state
- product boundary:
  - `lib/devres.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`

Current repo state on `master`:

- reviewed against `master` commit `aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb` immediately before this evidence-refresh series landed
- `lib/devres.zig` already anchors a helper-first `DevresHelperLab` on `lib/devres.c`
- compared against the earlier surveyed head `66b55d8a9a800345097f3c04b9f95130b1f8d0b8`, the current helper packet now advances by rejecting full-width inclusive MMIO resource spans that would overflow size math before request-region or remap planning begins; the refreshed `lib/devres.zig` helper surface now hashes to `sha256 11b2d4e475b7d21c1086679a438a851f1f12df15aa655b75e8a78fee7427bc21`
- compared against that same earlier surveyed head, the dedicated `zigux/tests/phase13_devres.zig` replay remains hash-stable at `sha256 7dc45ab99f46d5424e3d757f720e58654aaea326b13db1af601be88c3cbff476` while still covering the direct non-posted wrapper path
- the shipped `DevresHelperLab` descriptor now says explicitly that the helper-only surface still avoids live DMA-backed mappings and scatterlist ownership instead of leaving that boundary only in the manifest and prose packet
- a direct token scan of current `lib/devres.zig` finds only the `touches_live_dma` and `touches_live_scatterlist` descriptor markers and no `dmam_alloc_coherent`, `dmam_free_coherent`, `dma_map_resource`, `dma_unmap_resource`, `dma_map_sgtable`, `struct scatterlist`, or `sg_table` helper entrypoints
- `zigux/tests/phase13_devres.zig` already exercises managed `__devm_ioremap()` lifetime planning, the direct `devm_ioremap()`, `devm_ioremap_uc()`, `devm_ioremap_wc()`, and `devm_ioremap_np()` acquire wrappers, `__devm_ioremap_resource()` planning, `devm_of_iomap()` translation handoff, `devm_ioport_map()` lifetime bookkeeping, `devm_arch_phys_wc_add()` token retention, and `devm_arch_io_reserve_memtype_wc()` range retention
- the current helper lab still exposes no `dma*`, `dmam_*`, `scatterlist`, `sg_table`, or `sg_*` ownership surface, so the Phase 13 packet remains outside DMA-backed and scatter-gather behavior rather than merely leaving that boundary implicit
- `Documentation/zigux/phase13-devres-slice.md` already marks the helper boundary clearly, but until this packet landed the DMA/scatterlist boundary posture was not recorded in the same manifest-backed survey shape as the other active Phase 13 anchors
- `zigux/Makefile` and `zigux/tests/phase13_build.zig` already expose the shared Phase 13 replay entrypoints that this survey now joins

Why this matters for Phase 13:

- the roadmap treats Phase 13 as the shared helper tranche, so `lib/devres.c` belongs here only as long as it stays helper-first and reviewable
- MMIO- and iomap-adjacent helpers are exactly the kind of risky surface that the roadmap says should remain wrapper-first before any wider runtime claims
- recording the current helper surface in a manifest-backed survey stops later runs from mistaking these planners for live mapping parity or from reopening the already-landed helper-only work as if it were still missing

What is landed today:

- managed `__devm_ioremap()` lifetime planning, including retained release records on success and free-on-failure cleanup when mapping returns `NULL`
- the direct `devm_ioremap()` wrapper path that keeps the plain managed ioremap export explicit instead of leaving it implied by the internal lifetime helper
- the `devm_ioremap_uc()` wrapper path and exact `devm_iounmap()` pointer-match release behavior
- the `devm_ioremap_wc()` wrapper path without widening into live write-combined mappings
- the `devm_ioremap_np()` wrapper path so the direct non-posted managed mapping export is reviewable instead of being inferred only from the generic lifetime helper or from resource-flag fallback
- managed `__devm_ioremap_resource()` planning around memory-resource validation, overflow-safe inclusive size calculation, pretty-name construction, request-region gating, remap cleanup, and non-posted fallback when the resource flags demand it
- the adjacent `devm_ioremap_resource_wc()` wrapper path without widening into live write-combined mappings
- `devm_of_iomap()` planning around translated resource selection, optional size reporting, and delegation into the managed-resource planner without walking a live device tree
- `devm_ioport_map()` and `devm_ioport_unmap()` lifetime bookkeeping without claiming live port-space side effects
- token-style `devm_arch_phys_wc_add()` release planning and range-style `devm_arch_io_reserve_memtype_wc()` release planning without claiming live memtype mutation

What remains explicitly blocked:

- live MMIO side effects such as `devres_alloc_node()` ownership, `devres_add()` installation, `devm_request_mem_region()` side effects, and direct `ioremap()` or `iounmap()` execution against real hardware state
- live DMA-backed helpers such as `dmam_alloc_coherent()`, `dmam_free_coherent()`, `dma_map_resource()`, `dma_unmap_resource()`, or `dma_map_sgtable()` ownership and execution
- live scatter-gather ownership such as `struct scatterlist`, `sg_table`, `sg_*` iteration, merge, or detach-time cleanup behavior
- live device-tree walking, overlapping resource arbitration, or broader `struct device_node` ownership beyond the pure `devm_of_iomap()` planner boundary
- live MTRR or arch memtype state mutation beyond the token-style and range-style detach bookkeeping planners

The next honest bounded step for this lane is to keep the survey packet aligned with the helper lab and shared Phase 13 replay. New product work should move in the dedicated helper lanes rather than reopening this now-recorded helper-first DMA/scatterlist boundary packet.
