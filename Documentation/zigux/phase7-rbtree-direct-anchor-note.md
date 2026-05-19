# Phase 7 Rbtree Direct Anchor Note

Current direct-readback Phase 7 rbtree packet is publicly visible again through:

- `Documentation/zigux/phase7-rbtree-slice.md`
- `lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `zigux/tests/phase7_build.zig`
- `scripts/zigux/validate-phase7.py`

Fresh public GitHub fallback reread in this slot confirmed the slice note, helper, dedicated test, survey, manifest, fixture pair, parity checker, shared build file, and shared validator are visible again on current `master`.

Repo-reality warning for the still-missing Phase 7 shared wrapper routes:

- `zigux/Makefile` still lacks dedicated `phase7-*` wrapper markers
- `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps

Keep the current Phase 7 rbtree reminder surface tied to the fully returned helper-local packet plus the returned shared build and validator evidence.

- `string_helpers` remains the Phase 7 fully checker-backed sibling packet and should stay explicit rather than being folded into a generic missing-helper story.
- `cmdline` and `argv_split` keep their own helper-local packet ownership and should stay separate from this rbtree reminder.
- Do not widen this note into make-wrapper or workflow-recovery claims until a fresh same-lane reread proves those shared non-owner routes returned on current `master`.
