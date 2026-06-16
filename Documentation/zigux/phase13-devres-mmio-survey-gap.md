# Phase 13 devres MMIO Survey Gap

This bounded `P13-L01` companion records the current helper-first MMIO survey drift against the Phase 13 roadmap anchor at `lib/devres.c`.

## Current repo evidence

- the roadmap still keeps `lib/devres.c` inside bounded shared-helper delivery, with MMIO, resource-lifetime, device-tree, and arch memtype work staying helper-first and explicitly non-live until stronger proof lands
- current `master` still ships the helper-local `lib/devres.zig` MMIO packet, the direct replay `zigux/tests/phase13_devres.zig`, the reviewability companion `zigux/tests/phase13_devres_reviewability.zig`, the coherent-DMA boundary replay `zigux/tests/phase13_devres_dma_coherent.zig`, and the helper-local checker split through `scripts\zigux/check_phase13_devres_shared_lifetime_packet.zig`, `scripts\zigux/check_phase13_devres_dma_boundary.zig`, and `scripts\zigux/check_phase13_devres_mmio_packet.zig`
- current `Documentation/zigux/phase13-devres-survey.md` still records the landed MMIO planner story, but its scope, survey findings, gates, and next-step text still point at the older `scripts\zigux/check_phase13_devres_packet_alignment.zig` and `scripts\zigux/validate_phase13_release.zig` packet names instead of the shipped current-master checker split
- current `master` still keeps `zigux/tests/phase13_build.zig` absent, so the older shared-build packet should remain framed as repo-reality drift rather than as direct MMIO survey proof
- the helper-local safety boundary itself remains the same: the MMIO packet still blocks live mappings, live region mutation, live device-tree walking, live arch memtype state transitions, live DMA-backed helpers, and live scatterlist ownership

## Why this gap matters

The roadmap allows a helper-first `lib/devres.c` foothold.
It does not justify stale validator-first or shared-build claims after the repo packet has narrowed.
Leaving the survey on retired checker names makes the MMIO lane look more integrated than current `master` actually proves.

## Next bounded step

Refresh `Documentation/zigux/phase13-devres-survey.md` so its scope, exact live readback, gates, and follow-up text match the shipped current-master packet:

- `scripts\zigux/check_phase13_devres_shared_lifetime_packet.zig`
- `scripts\zigux/check_phase13_devres_dma_boundary.zig`
- `scripts\zigux/check_phase13_devres_mmio_packet.zig`

Keep `zigux/tests/phase13_build.zig` and any older validator-first helper names framed as repo-reality gaps until they actually return on current `master`.
