# Phase 13 devres Survey

This document records the bounded `P13-L01` helper-first MMIO safety survey lane around `lib/devres.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-helper-mmio-safety-survey`
- reviewed against live `master` `master-readback-2026-05-13`
- scope: the shipped `lib/devres.zig` helper lab, the existing `phase13-devres-slice` note, the shared `phase13-validate` make route, the direct devres and reviewability replays, the adjacent coherent-DMA boundary replay, and the manifest-backed devres packet-alignment checker that keeps the current helper-first MMIO survey truthful without claiming the older shared `zigux/tests/phase13_build.zig` bundle is present again
- product boundary:
  - `lib/devres.zig`
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `scripts/zigux/check-phase13-devres-packet-alignment.py`

## Why this slice exists

The Phase 13 roadmap explicitly names `lib/devres.c` as a shared subsystem-helper anchor.

That matters because `lib/devres.c` spans managed allocation, resource lifetime tracking, region reservation, device-tree resource translation, arch memtype cleanup, and neighboring helper families that can quickly drift into live MMIO, live device-tree, or live arch memtype claims if the lane overstates parity.

Current `master` still carries a real helper-first `lib/devres.zig` foothold for managed ioremap lifetime, pure `devm_of_iomap()` translation handoff, and WC token bookkeeping. The highest-value bounded work in this lane is therefore to keep that MMIO-facing packet explicit about what has landed and what live MMIO, device-tree, arch memtype, and scatterlist-backed ownership state is still blocked.

## Survey findings

- `lib/devres.zig` still models the starter `__devm_ioremap()` lifetime split between retained release records and free-on-failure cleanup, keeps `devm_iounmap()` pointer matching exact through the dedicated `planManagedIounmap()` planner, and preserves the pure `devm_ioremap_uc()` and `devm_ioremap_wc()` wrapper planners.
- the helper lab still carries a pure `__devm_ioremap_resource()` planner that checks memory-backed resources, computes inclusive size, preserves requested mapping types, and records busy-region and remap-failure shaping without claiming live side effects.
- the landed `devm_of_iomap()` bridge stays bounded to translated-resource selection by index, optional size reporting, and handoff into the existing managed-resource planner instead of pretending to walk a live device tree.
- the adjacent `devm_arch_io_reserve_memtype_wc()` and `devm_arch_phys_wc_add()` planners still stop at detach-time bookkeeping and failure shaping rather than claiming live arch memtype state transitions.
- exact helper-source readback on current `master` still shows `lib/devres.zig` touching no live device lists, no live MMIO side effects, and no live arch memtype mutation; the shipped planner set still stops at helper-first ioremap, translated-resource, and WC token bookkeeping.
- current `master` still ships the devres slice note, the shared `phase13-validate` make target, `scripts/zigux/validate-phase13-release.py`, the direct `zigux/tests/phase13_devres.zig` replay, the direct `zigux/tests/phase13_devres_reviewability.zig` companion, and the dedicated `zigux/tests/phase13_devres_dma_coherent.zig` boundary replay, but it still does not ship the older shared `zigux/tests/phase13_build.zig` packet surface that broader Phase 13 notes sometimes imply.
- the adjacent coherent-DMA evidence shard remains present on current `master`, but this survey lane keeps that shard as neighboring boundary proof rather than treating DMA-backed or scatterlist ownership as the core MMIO gap map.
- the current packet now keeps a helper-only DMA/scatterlist boundary explicit too: `lib/devres.zig` still exposes no DMA mapping helpers, no live scatterlist ownership, and no `sg_table` lifecycle control, so the coherent-DMA shard remains adjacent evidence rather than a claim of DMA-backed parity.

## Exact Live Readback

- live helper readback on current `master` still shows `.provides_iounmap_call_planning = true`, `pub const ManagedIounmapPlan`, `pub fn planManagedIounmap(`, and `.warns_on_release_miss = !release_matches` in `lib/devres.zig`, so the `devm_iounmap()` planner remains present as shipped evidence rather than as survey-only prose.
- the same helper readback also still shows `.provides_arch_phys_wc_token_planning = true`, `pub const ManagedPhysWcAddInput`, `pub const ManagedPhysWcAddPlan`, and `pub fn planArchPhysWcAdd(` in `lib/devres.zig`, so the token-style `devm_arch_phys_wc_add()` planner remains part of the current helper-first packet.
- `Documentation/zigux/phase13-devres-slice.md` still names `devm_iounmap()`, `devm_ioremap_uc()`, `devm_ioremap_wc()`, `devm_of_iomap()`, and `devm_arch_phys_wc_add()` as shipped helper-first evidence.
- `zigux/tests/phase13_devres.zig` is still present on current `master` and still replays the exact-match and release-miss `planManagedIounmap()` cases, the managed `devm_ioremap_uc()` and `devm_ioremap_wc()` wrapper paths, the pure `devm_of_iomap()` bridge, and the token-style phys-WC helper.
- `zigux/tests/phase13_devres_reviewability.zig` and `zigux/tests/phase13_devres_dma_coherent.zig` are both present on current `master`, while `zigux/tests/phase13_build.zig` is absent on current `master`.
- `zigux/tests/phase13_devres_manifest.json` now records the same `P13-L01` helper packet and the same live `master-readback-2026-05-13` marker as the survey note, direct replay, and reviewability gate, while also keeping the helper-only DMA/scatterlist boundary explicit beside the blocked MMIO, device-tree, and arch-memtype state gaps.
- older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift rather than as the current checker label for this helper-first packet.

## Recorded gaps

The current lane state is:

- landed `phase13-make-target`
- landed `phase13-devres-helper-starter`
- landed `phase13-devres-slice-note`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-test-gate`
- landed `phase13-devres-reviewability-gate`
- landed `phase13-devres-iounmap-planner`
- landed `phase13-devres-of-iomap-planner`
- landed `phase13-devres-arch-phys-wc-token-planner`
- blocked `phase13-devres-live-mmio-mappings`
- blocked `phase13-devres-live-device-tree-walk`
- blocked `phase13-devres-live-arch-memtype-state`
- blocked `phase13-devres-live-scatterlist-ownership`

This keeps the lane explicit without overstating progress: Zigux has a real helper-first MMIO safety foothold for managed ioremap lifetime planning, exact `devm_iounmap()` matching, pure translated-resource `devm_of_iomap()` handoff, detach-time WC memtype bookkeeping, and direct replay plus reviewability guards, but it still does not claim live MMIO mappings, live device-tree walking, live arch memtype state transitions, or live scatterlist ownership.

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

If this helper-local MMIO packet reopens, first compare `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` together on current `master` before widening anything else.
