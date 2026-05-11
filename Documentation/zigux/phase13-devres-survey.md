# Phase 13 devres Survey

This document records the bounded Phase 13 survey lane around `lib/devres.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-dma-scatterlist-boundary-survey`
- reviewed against live `master` readback on `2026-05-11`
- scope: the shipped `lib/devres.zig` helper lab, the existing `phase13-devres-slice` note, the shared Phase 13 make and release-validator surfaces that still mention this tranche, and one helper-local DMA or scatterlist boundary replay that keeps the current helper-first packet truthful without pretending the missing wider build or checker packet is already back
- product boundary:
  - `lib/devres.zig`
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_devres_dma_coherent.zig`

## Why this slice exists

The Phase 13 roadmap explicitly names `lib/devres.c` as a shared subsystem-helper anchor.

That matters because `lib/devres.c` spans managed allocation, resource lifetime tracking, region reservation, device-tree resource translation, arch memtype cleanup, and neighboring helper families that can quickly drift into live DMA-backed or scatterlist ownership if the lane overclaims parity.

Current `master` still carries a real helper-first `lib/devres.zig` foothold, but the broader packet surfaces that used to prove this boundary together are no longer all present. The highest-value bounded work in this lane is therefore to keep the live helper surface reviewable and explicit about where DMA-backed and scatterlist-owned behavior still remains blocked.

## Survey findings

- `lib/devres.zig` still models the starter `__devm_ioremap()` lifetime split between retained release records and free-on-failure cleanup, keeps `devm_iounmap()` pointer matching exact through the dedicated `planManagedIounmap()` planner, and preserves the pure `devm_ioremap_wc()`-style write-combined wrapper step.
- the helper lab still carries a pure `__devm_ioremap_resource()` planner that checks memory-backed resources, computes inclusive size, preserves requested mapping types, and records busy-region and remap-failure shaping without claiming live side effects.
- the landed `devm_of_iomap()` planner stays bounded to translated-resource selection by index, optional size reporting, and handoff into the existing managed-resource planner instead of pretending to walk a live device tree.
- the adjacent `devm_arch_io_reserve_memtype_wc()` and `devm_arch_phys_wc_add()` planners still stop at detach-time bookkeeping and failure shaping rather than claiming live arch memtype state transitions.
- exact helper-source readback on current `master` shows `lib/devres.zig` still exposes no `dmam_alloc_*`, `dma_map_*`, `dma_unmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, or `sg_*` ownership surface; the shipped planner set still stops at helper-first ioremap, translated-resource, and WC memtype bookkeeping.
- current `master` still ships the devres slice note, the shared `phase13-validate` make target, and `scripts/zigux/validate-phase13-release.py`, but it no longer ships the older dedicated `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, or `scripts/zigux/check-phase13-devres-packet.py` packet surfaces that earlier lane notes referenced.
- this survey therefore keeps the DMA or scatterlist boundary explicit through one standalone manifest-backed replay instead of overstating the missing wider packet as if it were still present on `master`.

## Recorded gaps

The current lane state is:

- landed `phase13-make-target`
- landed `phase13-devres-helper-starter`
- landed `phase13-devres-slice-note`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-dma-coherent-replay`
- blocked `phase13-build-gate`
- blocked `phase13-devres-test-gate`
- blocked `phase13-devres-reviewability-gate`
- blocked `phase13-devres-live-mmio-mappings`
- blocked `phase13-devres-live-dma-backed-helpers`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-device-tree-walk`
- blocked `phase13-devres-live-arch-memtype-state`

This keeps the lane explicit without overstating progress: Zigux has a real helper-first devres foothold for managed resource planning, detach-time bookkeeping, and one dedicated coherent-DMA boundary replay, but it still does not claim live MMIO mappings, live DMA-backed helpers, live scatterlist ownership, live device-tree walking, or live arch memtype state transitions.

## Non-goals

This slice does not claim:

- live MMIO mappings or unmap side effects
- live region reservation or release-region mutation
- live DMA-backed helpers or DMA mapping ownership
- live scatterlist ownership or `sg_table` lifecycle control
- device-tree walking or ownership of OF nodes
- generic devres groups or broader teardown parity
- live arch memtype mutation or token-release side effects

## Gates

1. run the shared Phase 13 release validator
- `python3 scripts/zigux/validate-phase13-release.py`

2. run the convenience target
- `make -C zigux phase13-validate`

## Next bounded step

If this helper-local boundary packet remains useful after the current repo drift settles, the next honest same-lane move is to restore one tiny shared Phase 13 wiring surface for the DMA or scatterlist replay without widening into live mappings, live DMA ownership, scatterlist delivery, or broader release-validator ownership.
