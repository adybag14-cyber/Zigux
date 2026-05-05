# Phase 13 devres Survey

This document records the bounded Phase 13 survey and reviewability lane around `lib/devres.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=devres-mmio-helper-survey`
- scope: the landed `lib/devres.zig` helper lab, its dedicated Phase 13 test, the shared Phase 13 build and make wiring, and the lane notes that compare the current MMIO-facing helper boundary against the roadmap
- product boundary:
  - `lib/devres.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `lib/devres.c` as a shared subsystem-helper anchor.

That matters because `lib/devres.c` spans managed allocation, resource lifetime tracking, region reservation, device-tree resource translation, and arch memtype release behavior that can quickly turn into risky live MMIO state if the lane overclaims parity.

The live Zigux tree is no longer survey-only here. It already carries a helper-first `lib/devres.zig` lab, so the highest-value work in this lane is to keep that real MMIO-adjacent footing reviewable against the roadmap instead of letting the missing survey packet hide where live state is still blocked.

## Survey findings

- `lib/devres.zig` already models the starter `__devm_ioremap()` lifetime split between retained release records and free-on-failure cleanup, and it keeps `devm_iounmap()` pointer matching exact.
- the current helper lab also carries a pure `__devm_ioremap_resource()` planner that checks memory-backed resources, computes inclusive size, preserves requested mapping types, and records busy-region and remap-failure shaping without claiming live side effects.
- the landed `devm_of_iomap()` planner stays bounded to translated-resource selection by index, optional size reporting, and handoff into the existing managed-resource planner instead of pretending to walk a live device tree.
- the adjacent `devm_arch_io_reserve_memtype_wc()` planner already records detach-time cleanup intent for WC reservations while keeping live arch memtype mutation out of scope.
- the helper lab now also carries the promised tiny `devm_arch_phys_wc_add()` token planner, limited to release-token retention on success and release-record cleanup on negative token returns without claiming live arch memtype add or remove side effects.
- the shared Phase 13 build and make target already replay the devres packet, so the missing gap was no longer helper behavior first. It was that this MMIO-facing lane still lacked a manifest-backed survey packet naming the remaining blocked live-state boundaries.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-devres-helper-starter`
- landed `phase13-devres-test-gate`
- landed `phase13-devres-slice-note`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-managed-resource-planner`
- landed `phase13-devres-of-iomap-planner`
- landed `phase13-devres-arch-io-wc-planner`
- landed `phase13-devres-arch-phys-wc-token`
- blocked `phase13-devres-live-mmio-mappings`
- blocked `phase13-devres-live-device-tree-walk`
- blocked `phase13-devres-live-arch-memtype-state`

This keeps the lane explicit without overstating progress: Zigux has a real helper-first devres foothold for MMIO-adjacent planning, but it still does not claim live MMIO mappings, resource-region mutations, device-tree walking, or arch memtype state transitions.

## Non-goals

This slice does not claim:

- live MMIO mappings or unmap side effects
- live region reservation or release-region mutation
- device-tree walking or ownership of OF nodes
- generic devres groups or broader teardown parity
- DMA-backed mappings or scatterlist ownership
- live arch memtype mutation or token-release side effects

## Gates

1. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Keep the Phase 13 devres MMIO lane steady unless fresh repo evidence exposes another equally small exported-helper gap inside `lib/devres.zig`. Do not widen into live MMIO, device-tree walking, generic devres groups, or arch memtype side effects just to keep the lane active.
