# Phase 13 devres Slice

This bounded Phase 13 slice keeps `lib/devres.c` visible as a shared-helper anchor, but current `master` does not yet materialize the direct `lib/devres.zig` starter or the older helper-packet replay set that earlier notes sometimes summarized.

Current repo reality for this lane is intentionally narrow:
  * the docs-side slice note is still present so the Phase 13 owner split can keep `devres` separate from `libfs`, `landlock`, and adjacent notifier evidence
  * `scripts/zigux/check-phase13-devres-packet-alignment.py` remains the shipped lane-local checker name, but its paired survey, manifest, and direct replay packet are not materialized in this checkout
  * direct companions such as `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json` should stay recorded as repo-reality gaps rather than described here as already shipped helper evidence

This slice therefore does not claim managed `__devm_ioremap()` bookkeeping, exact `devm_iounmap()` pointer matching, `__devm_ioremap_resource()` planning, `devm_of_iomap()` bridging, arch WC detach planners, live MMIO side effects, live DMA ownership, scatterlist ownership, or broader devres-group teardown behavior on current `master`.

The next honest bounded step in this same lane is to either materialize one direct `devres` starter surface or trim any broader shared reminder that still treats those missing direct companions as shipped current-`master` evidence.
