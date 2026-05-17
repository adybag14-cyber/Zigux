# Phase 13 devres Slice

This bounded Phase 13 slice keeps `lib/devres.c` visible as a shared-helper anchor. Current `master` now materializes the direct `lib/devres.zig` starter plus the paired direct replay packet, while the DMA and scatterlist boundary evidence stays separate from broader live-side-effect claims.

Current repo reality for this lane is intentionally helper-first:
  * the docs-side slice note is still present so the Phase 13 owner split can keep `devres` separate from `libfs`, `landlock`, and adjacent notifier evidence
  * `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` now ship the bounded direct helper packet on current `master`
  * `scripts/zigux/check-phase13-devres-packet-alignment.py` is the current lane-local checker for that direct packet, while the older `scripts/zigux/check-phase13-devres-packet.py` wording should stay treated as stale history rather than as the active checker label
  * `zigux/tests/phase13_devres_dma_coherent.zig` remains the direct replay surface for the planning-only DMA and scatterlist boundary, but it still does not by itself claim live DMA helper delivery, live scatterlist ownership, or `sg_table` lifecycle control

This slice therefore claims only the bounded helper-first surface already present on current `master`: managed `__devm_ioremap()` bookkeeping, exact `devm_iounmap()` pointer matching, pure `devm_ioremap_uc()` and `devm_ioremap_wc()` wrapper planners, `__devm_ioremap_resource()` planning-time region bookkeeping, `devm_of_iomap()` translation handoff, and arch WC detach planners. It still does not claim live MMIO side effects, live region reservation or release-region mutation, live DMA ownership, scatterlist ownership, or broader devres-group teardown behavior.

The next honest bounded step in this same lane is to compare the direct helper packet and the DMA-boundary shard together on current `master` before widening anything else, and only trim broader shared reminders if they drift from that shipped helper-first surface.