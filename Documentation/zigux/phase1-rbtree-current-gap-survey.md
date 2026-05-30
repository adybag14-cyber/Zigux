# Phase 1 rbtree Current Gap Survey

This note records the current `tools/lib/rbtree.zig` gap that still keeps the Phase 1 rbtree direct-anchor lane open. It is survey evidence only; it does not reopen the closed Phase 1 helper tranche or claim broader Phase 1 route readiness.

## Grounding

- Roadmap anchor: Phase 1 requires low-risk host-side helper ports in `tools/lib/*.zig`, mixed-language helper build support, golden-output parity tests, and clear ownership for Zig helpers beside their C originals.
- Bootstrap-ledger anchor: the Phase 1 helper train includes `tools/lib/rbtree.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/build.zig`, `scripts/zigux/validate-phase1.py`, and later Phase 1 parity fixtures and artifact diff gates.
- Current helper readback: `tools/lib/rbtree.zig` at `b8cc3d811028922be412f40cfddfd8da82ea6d8c` still contains the ordered Linux-style alias and cached-root alias coverage, but it does not yet expose the non-cached low-level Linux-style alias wrappers.

## Current Gap

- `PHASE1_RBTREE_CURRENT_SURVEY_STATUS=helper_gap_open`
- `PHASE1_RBTREE_CURRENT_HELPER_BLOB=b8cc3d811028922be412f40cfddfd8da82ea6d8c`
- `PHASE1_RBTREE_MISSING_LOW_LEVEL_ALIASES=rb_link_node,rb_insert_color,rb_erase,rb_erase_init`
- `PHASE1_RBTREE_MISSING_TEST_ANCHOR=test "rbtree low-level Linux-style aliases mirror node-state helpers"`
- `PHASE1_RBTREE_EXISTING_HELPER_ANCHORS=ordered_linux_style_aliases,cached_root_aliases,cached_root_insert_miss,leftmost_sync,singleton_erase,replacement,detach,reseed`

The live manifest and review packet already name `low_level_alias_anchor`, but the helper file does not yet carry the low-level alias wrapper surface itself. Treat that as the current repo gap, not as completed helper parity.

## Next Bounded Step

- `PHASE1_RBTREE_NEXT_BOUNDED_STEP=apply the already-scoped non-cached low-level alias helper patch for rb_link_node, rb_insert_color, rb_erase, and rb_erase_init plus the direct low-level alias test once a trustworthy patch-capable current-head write path is available; otherwise keep this survey and its checker aligned with current helper reality`

Do not widen this lane into shared Phase 1 closure routes, Phase 7 runtime rbtree work, or adjacent bitmap, find_bit, or string direct-anchor helpers.
