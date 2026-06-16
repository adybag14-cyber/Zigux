# Phase 13 devres MMIO Validate-Route Gap

## Scope

This note records the current Phase 13 `devres` MMIO route-truthfulness gap on `master`.

It stays inside reminder-surface and checker-local validation truthfulness. It does not reopen older direct `devres` MMIO replay claims, live DMA ownership, scatterlist lifecycle ownership, or broader release-summary rewrites.

## Current Drift

Current `master` now keeps the narrower helper-first `devres` packet explicit through these shipped surfaces:

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `scripts\zigux/check_phase13_devres_dma_boundary.zig`
- `scripts\zigux/check_phase13_devres_mmio_packet.zig`
- `lib/devres.zig`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`

Current reread also shows `zigux/Makefile` is present again on `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`.

That leaves one narrower route gap: the repo ships the historically named `scripts\zigux/check_phase13_devres_mmio_packet.zig`, but current `master` still does not materialize `scripts\zigux/validate_phase13_release.zig`, `scripts\zigux/check_phase13_devres_packet.zig`, `scripts\zigux/check_phase13_devres_packet_alignment.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, or the shared `zigux/tests/phase13_build.zig` route.

## Why It Matters

Phase 13 in the roadmap is still the shared-helper tranche around `lib/devres.c`. The live devres packet is now narrower and helper-first, so any scripts-root or contributor-facing reminder has to keep the returned `zigux/Makefile` file distinct from the still-missing Phase 13 make routes, and it has to treat `scripts\zigux/check_phase13_devres_mmio_packet.zig` as a shipped current checker without pretending that the older direct MMIO replay or release-validator packet already returned.

## Next Bounded Step

Leave this note parked unless a future reread shows `scripts/zigux/README.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `scripts\zigux/check_phase13_devres_mmio_packet.zig`, or `zigux/Makefile` drifting away from this narrower route picture.

If the same family reopens, first compare those seven surfaces together and land at most one reminder-surface or checker-local truthfulness repair without widening into helper behavior.
