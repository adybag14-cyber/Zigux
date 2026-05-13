# Phase 13 Devres Resource Lifetime Survey

Lane: `P13-Y05`
Phase: `Phase 13`
Roadmap anchor set: `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, `security/landlock/syscalls.c`
Surveyed commit: `master-readback-2026-05-13`

## Repo Reality

The Phase 13 roadmap still calls for resource lifetime helpers under `lib/devres.zig`, but current `master` no longer matches the older placeholder-only story. The active devres lifetime packet already ships a helper-first surface through:

- `lib/devres.zig`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- the shared `make -C zigux phase13-validate` replay handle

That shipped packet keeps the current lifetime-focused helper scope explicit instead of pretending the broader shared `zigux/tests/phase13_build.zig` bundle has returned on current `master`.

## Current Lifetime Packet

The current helper-first lifetime packet already covers:

- managed `devm_ioremap()` acquisition planning, including retained release records on success and free-on-failure cleanup
- pointer-exact `devm_iounmap()` call planning with release-miss warning shaping
- bounded `devm_ioremap_uc()` and `devm_ioremap_wc()` wrapper planning
- pure `__devm_ioremap_resource()` request-region and remap-failure shaping without claiming live MMIO side effects
- bounded `devm_of_iomap()` translated-resource handoff and optional size reporting without claiming live OF tree walks
- helper-local `devm_arch_io_reserve_memtype_wc()` and `devm_arch_phys_wc_add()` detach-time bookkeeping planners without claiming live arch memtype mutation

The current boundary is also clearer than the older survey wording allowed: the active packet still blocks live MMIO mappings, live device-tree walking, live arch memtype state transitions, live DMA-backed helper coverage, and live scatterlist ownership. The adjacent coherent-DMA replay is current evidence, but it remains adjacent boundary proof rather than a claim that `lib/devres.zig` already owns DMA or scatterlist lifecycle.

## Governance Note

This lane should now treat the older placeholder wording and the older `scripts/zigux/check-phase13-devres-packet.py` reference as stale packet drift. The authoritative current governance packet is the helper-first devres slice already backed by the manifest, the direct replay, the direct reviewability companion, the coherent-DMA boundary replay, and `scripts/zigux/check-phase13-devres-packet-alignment.py`.

## Next Bounded Step

Keep the next Phase 13 devres follow-through inside the current helper-local lifetime packet: prefer one same-packet governance, survey, manifest, or reviewability refresh that keeps the shipped `devm_iounmap()`, `devm_of_iomap()`, WC memtype, and phys-WC token planners aligned with the direct replay pair and the DMA boundary shard. Do not widen this survey back into placeholder language, shared-build resurrection claims, or live DMA or scatterlist parity claims that current `master` still blocks.
