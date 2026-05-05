# Phase 13 devres Survey

This document records the bounded Phase 13 survey lane around `lib/devres.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-dma-scatterlist-boundary-survey`
- survey provenance refreshed against verified master head `e59df689d080aa11773adda87f00c2d650caade8`
- scope: the landed `lib/devres.zig` helper lab, its dedicated Phase 13 test, the focused reviewability gate, the shared Phase 13 build and make wiring, and the lane notes that compare the current helper-only DMA/scatterlist boundary against the roadmap
- product boundary:
  - `lib/devres.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `lib/devres.c` as a shared subsystem-helper anchor.

That matters because `lib/devres.c` spans managed allocation, resource lifetime tracking, region reservation, device-tree resource translation, arch memtype cleanup, and neighboring helper families that can quickly drift into live DMA-backed or scatter-gather ownership if the lane overclaims parity.

The live Zigux tree is no longer survey-only here. It already carries a helper-first `lib/devres.zig` lab, so the highest-value work in this lane is to keep that real foothold reviewable against the roadmap and explicit about where DMA-backed and scatterlist-owned behavior still remains blocked.

## Survey findings

- `lib/devres.zig` already models the starter `__devm_ioremap()` lifetime split between retained release records and free-on-failure cleanup, and it keeps `devm_iounmap()` pointer matching exact.
- the current helper lab also carries a pure `__devm_ioremap_resource()` planner that checks memory-backed resources, computes inclusive size, preserves requested mapping types, and records busy-region and remap-failure shaping without claiming live side effects.
- the landed `devm_of_iomap()` planner stays bounded to translated-resource selection by index, optional size reporting, and handoff into the existing managed-resource planner instead of pretending to walk a live device tree.
- the adjacent `devm_arch_io_reserve_memtype_wc()` planner already records detach-time cleanup intent for WC reservations while keeping live arch memtype mutation out of scope.
- the matching `devm_arch_phys_wc_add()` token planner now records retained removal tokens on success and frees release records on negative token returns while keeping `arch_phys_wc_del()` reviewable and out of live side-effect territory.
- the shared Phase 13 build and make target already replay the devres packet, so the remaining lane-local gap is not new helper behavior first. It is keeping the helper-only DMA/scatterlist boundary explicit and machine-checkable wherever the survey packet records current Phase 13 evidence.
- exact boundary evidence on current `master`: `lib/devres.zig` still exposes no `dmam_alloc_*`, `dma_map_*`, `dma_unmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, or `sg_*` ownership surface; the shipped planner set still stops at helper-first ioremap, translated-resource, and WC memtype bookkeeping.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-devres-helper-starter`
- landed `phase13-devres-test-gate`
- landed `phase13-devres-reviewability-gate`
- landed `phase13-devres-slice-note`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-managed-resource-planner`
- landed `phase13-devres-of-iomap-planner`
- landed `phase13-devres-arch-io-memtype-planner`
- landed `phase13-devres-arch-phys-wc-token-planner`
- blocked `phase13-devres-live-mmio-mappings`
- blocked `phase13-devres-live-dma-backed-helpers`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-device-tree-walk`
- blocked `phase13-devres-live-arch-memtype-state`

This keeps the lane explicit without overstating progress: Zigux has a real helper-first devres foothold for managed resource planning and detach-time bookkeeping, but it still does not claim live MMIO mappings, live DMA-backed helpers, live scatter-gather ownership, live device-tree walking, or live arch memtype state transitions.

## Non-goals

This slice does not claim:

- live MMIO mappings or unmap side effects
- live region reservation or release-region mutation
- live DMA-backed helpers or DMA mapping ownership
- live scatter-gather ownership or `sg_table` lifecycle control
- device-tree walking or ownership of OF nodes
- generic devres groups or broader teardown parity
- live arch memtype mutation or token-release side effects

## Gates

1. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Keep this lane inside survey-packet truthfulness unless current repo evidence reopens it again. The next same-family work, if needed, is another packet-local alignment that keeps the helper-only DMA/scatterlist boundary explicit without widening into live mappings, live DMA ownership, scatterlist delivery, or broader release-validator ownership.
