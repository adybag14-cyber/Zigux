# Phase 7 Rbtree Direct Anchor Note

Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`: `Documentation/zigux/phase7-rbtree-slice.md` and `scripts/zigux/check-phase7-rbtree-parity.py` now sit beside the already returned `tools/lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, survey, and manifest, while helper-local ownership still stays on `tools/lib/rbtree.zig` and the dedicated fixture pair still does not publicly materialize there yet.

In this slot, the directly readable same-lane truthfulness packet is limited to:

- `Documentation/zigux/phase7-rbtree-slice.md`
- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `tools/lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`

Fresh authenticated GitHub reread in this slot directly returned:

- `Documentation/zigux/phase7-rbtree-slice.md`
- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `tools/lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`
- `scripts/zigux/check-phase7-rbtree-parity.py`

Fresh current-master reread in this slot also confirmed these shared or roadmap-aligned non-owner surfaces:

- `lib/rbtree.zig`
- `scripts/zigux/check-phase7-build-wiring.py`
- `scripts/zigux/validate-phase7.py`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

`zigux/tests/phase7_build.zig` needed the public blob and raw GitHub fallback in this slot after the authenticated GitHub contents bridge returned `404` for that path, so keep it explicit as returned shared non-owner build evidence without overstating authenticated whole-file coverage for this one surface.

Machine-readable fallback provenance stays explicit through `public_fallback_non_owner_paths` in `zigux/tests/phase7_rbtree_manifest.json`, which currently names only `zigux/tests/phase7_build.zig` because the other listed shared or roadmap-aligned non-owner surfaces still rematerialized through authenticated rereads in this slot.

Fresh authenticated GitHub reread in this slot still returned `404` for these dedicated companion surfaces:

- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

Repo-reality warning for the still-missing dedicated Phase 7 rbtree wrapper routes:

- `zigux/Makefile` now returns shared `phase7-validate`, but it still lacks dedicated `phase7-rbtree-test:`, `phase7-rbtree-survey:`, `phase7-test:`, and aggregate `phase7:` wrapper markers
- `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps

Keep the current Phase 7 rbtree reminder surface tied to the returned tool-root helper, the dedicated slice note, the dedicated replay companion, the returned survey and manifest, the parity checker, the readable `lib/rbtree.zig` roadmap-path companion, and the directly readable shared build, validator, and workflow evidence, while still not claiming the dedicated fixture pair as returned helper-local ownership.

- `string_helpers` remains the Phase 7 fully landed sibling packet and should stay explicit rather than being folded into a generic missing-helper story.
- `cmdline` and `argv_split` keep their own helper-local packet ownership and should stay separate from this rbtree reminder.
- Do not widen this note into dedicated make-wrapper or workflow-recovery claims until a fresh same-lane reread proves one more concrete still-missing rbtree companion surface such as `zigux/tests/fixtures/phase7_rbtree.json` or `zigux/tests/fixtures/phase7_rbtree_c_harness.c` has rematerialized on current `master`.
