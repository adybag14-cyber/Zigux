# Phase 13 devres Slice

This bounded Phase 13 slice keeps `lib/devres.c` visible as a shared-helper anchor without overstating what current `master` actually ships.

Current repo reality for this lane stays intentionally narrow:
  * the docs-side slice note is still present so the Phase 13 owner split can keep `devres` separate from `libfs`, `landlock`, and adjacent notifier evidence
  * `Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary against the direct DMA-boundary replay, the planning-only `dmam_alloc_coherent()` note and manifest, and the helper-first scatterlist slice without claiming that the older `lib/devres.zig` packet already landed on current `master`
  * `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` remain repo-reality gaps rather than described here as shipped current-`master` evidence
  * `scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket beside that broader helper, manifest, and direct replay packet, while the older `scripts/zigux/check-phase13-devres-packet.py` wording should stay treated as stale history rather than as the active checker label
  * `zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only: they do not claim live DMA helper delivery, live scatterlist ownership, or `sg_table` lifecycle control

This slice therefore keeps the roadmap-owned helper destination visible without claiming that the broader direct helper packet already landed on current `master`. The bounded current evidence is the survey note, the direct DMA-boundary replay, the planning-only `dmam_alloc_coherent()` note and manifest, and the helper-first scatterlist helper plus replay, while the broader direct helper packet stays an explicit repo-reality gap.

The next honest bounded step in this same lane is to compare those survey, planner, replay, and helper surfaces together on current `master` before widening anything else, and only rematerialize the broader helper, manifest, checker, and direct replay packet if the repo state genuinely supports it.
