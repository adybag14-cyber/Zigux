# Phase 3 Roadmap Gap Survey

This note records the current Phase 3 ABI and interop gap between the roadmap contract and the live Zigux tree.

## Status

- `PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c`
- `PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig`
- `PHASE3_CURRENT_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header`
- `PHASE3_CURRENT_UAPI=zigux/uapi/version.zig`
- `PHASE3_CURRENT_UAPI_SCOPE=version-and-boundary-header`
- `PHASE3_UAPI_BOUNDARY_GAP=version-and-boundary-header-surface-is-still-below-full-uapi-shim-destination`
- `PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig`
- `PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig`
- `PHASE3_CURRENT_RBTREE_STATUS=phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing`
- `PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,zigux/helpers/rbtree_view.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase3-rbtree-slice.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_manifest.json,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors`
- `PHASE3_INTEROP_GAP=curated-rbtree-c-binding-surface-still-missing`
- `PHASE3_NEXT_BOUNDED_STEP=curated-rbtree-boundary-header-and-parity-fixture-before-more-chrdev-growth`

## Current Gap

The largest roadmap-backed interop gap is no longer the total absence of a Phase 3 `rbtree` helper family.

That helper packet now exists through:

- `zigux/helpers/rbtree_view.zig`
- `Documentation/zigux/phase3-rbtree-slice.md`
- `zigux/tests/phase3_rbtree_survey.zig`
- `zigux/tests/phase3_rbtree_manifest.json`

The remaining honest gap is narrower:

- there is still no curated `rbtree` record in `include/zigux/abi.h`
- there is still no matching `zigux/bindings/abi.zig` layout type for a Phase 3 `rbtree` boundary packet
- there is still no C-vs-Zig parity fixture for a Phase 3 `rbtree` boundary shape

That is a better state than before, because the repo now has a real helper-local Phase 3 `rbtree` packet, but the header-and-binding contract is still pending.

## Next Bounded Step

The next honest Phase 3 move is one small curated `rbtree` boundary contract in the shared ABI packet before more char-device expansion:

- one header-and-binding shape
- one focused parity fixture
- one validator-backed note refresh
