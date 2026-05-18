# Phase 13 devres Slice

This bounded Phase 13 slice keeps `lib/devres.c` visible as a shared-helper anchor without overstating what current `master` actually ships.

Current repo reality for this lane stays intentionally narrow:
  * the docs-side slice note is still present so the Phase 13 owner split can keep `devres` separate from `libfs`, `landlock`, and adjacent notifier evidence
  * `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` remain repo-reality gaps rather than described here as shipped current-`master` evidence
  * `scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket beside that paired survey, helper, manifest, and broader direct replay packet, while the older `scripts/zigux/check-phase13-devres-packet.py` wording should stay treated as stale history rather than as the active checker label
  * `zigux/tests/phase13_devres_dma_coherent.zig` now materializes one direct replay surface for the planning-only DMA and scatterlist boundary, but it still does not by itself claim live DMA helper delivery, live scatterlist ownership, or `sg_table` lifecycle control

This slice therefore keeps the roadmap-owned helper destination visible without claiming that the broader direct helper packet already landed on current `master`. The bounded current evidence is the direct DMA-boundary replay plus the planner note, while the paired survey, helper, manifest, and broader direct replay packet stay explicit repo-reality gaps.

The next honest bounded step in this same lane is to compare the DMA-boundary replay and planner note together on current `master` before widening anything else, and only rematerialize the paired survey, helper, manifest, and broader direct replay packet if the repo state genuinely supports it.
