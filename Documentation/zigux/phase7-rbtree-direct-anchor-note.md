# Phase 7 Rbtree Direct Anchor Note

Current direct-readback Phase 7 rbtree helper packet does not publicly materialize on current `master`.

In this slot, the directly readable same-lane truthfulness packet is limited to:

- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`

Fresh authenticated GitHub reread in this slot returned 404 for these previously claimed returned surfaces:

- `Documentation/zigux/phase7-rbtree-slice.md`
- `lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `zigux/tests/phase7_build.zig`
- `scripts/zigux/validate-phase7.py`

Repo-reality warning for the still-missing Phase 7 shared wrapper routes:

- `zigux/Makefile` still lacks dedicated `phase7-*` wrapper markers
- `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps

Keep the current Phase 7 rbtree reminder surface tied to missing-helper truthfulness rather than a returned-packet claim.

- `string_helpers` remains the Phase 7 fully landed sibling packet and should stay explicit rather than being folded into a generic missing-helper story.
- `cmdline` and `argv_split` keep their own helper-local packet ownership and should stay separate from this rbtree reminder.
- Do not widen this note into make-wrapper or workflow-recovery claims until a fresh same-lane reread proves one concrete rbtree helper-local surface has rematerialized on current `master`.
