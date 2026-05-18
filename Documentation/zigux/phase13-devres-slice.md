# Phase 13 devres Slice

This bounded Phase 13 slice keeps `lib/devres.c` visible as a shared-helper anchor without overstating what current `master` actually ships.

Current repo reality for this lane stays intentionally narrow:
  * the docs-side slice note is still present so the Phase 13 owner split can keep `devres` separate from `libfs`, `landlock`, and adjacent notifier evidence
  * `Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary against the direct DMA-boundary replay, the planner note and manifest, the newly landed pure `dmam_alloc_coherent()` helper, and the helper-first scatterlist slice without claiming live DMA side effects or scatterlist ownership
  * `lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface, while the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps
  * `scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket beside that broader direct helper packet, while the current landed helper-first packet is tracked through the dedicated planner note, manifest, replay, and survey wording
  * `zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only: this slice does not claim live DMA helper delivery, live scatterlist ownership, or `sg_table` lifecycle control

This slice therefore keeps the roadmap-owned helper destination visible without claiming that the broader direct helper packet already landed on current `master`. The bounded current evidence is the survey note, the planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, and the helper-first scatterlist helper plus replay, while the broader direct helper packet stays an explicit repo-reality gap.

The next honest bounded step in this same lane family is to compare those survey, planner, helper, replay, and scatterlist surfaces together on current `master` before widening anything else, and only rematerialize the broader direct helper packet if the repo state genuinely supports it.
