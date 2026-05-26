# Phase 3 `rbtree` Interop Gap Survey

This note records the current roadmap-backed `rbtree` gap inside the bounded Phase 3 ABI lane.

## Scope

- `PHASE3_RBTREE_GAP_ROADMAP_ANCHOR=lib/rbtree.c`
- `PHASE3_RBTREE_GAP_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_RBTREE_GAP_CATALOG_PATH=scripts/zigux/phase3_catalog.py`
- this note is limited to current repo-reality reporting for the still-missing `rbtree` interop slice

## Current Repo Reality

- Current `master` already carries bounded Phase 3 starter and replay surfaces for the shared ABI header, header-family relay, policy helpers, low-level wrappers, export/UAPI replay, bitmap/cpumask, list/hlist, err_ptr/xarray, and xarray-slot follow-through.
- Current `master` does not yet carry a dedicated `rbtree` helper, binding, focused replay, checker, manifest packet, or slice note inside the same Phase 3 interop family.
- That means the shared ABI packet is still a bounded starter surface rather than the broader permanent boundary implied by the Phase 3 roadmap anchors.

## Gap

The highest-value same-lane repo-reality gap is not another reminder rewrite. It is the absence of a focused `lib/rbtree.c`-backed interop slice beside the already-landed bitmap/cpumask, list/hlist, err_ptr/xarray, and xarray-slot packets.

## Next Safe Step

- Add one bounded `rbtree` packet only: a helper or binding surface, one focused replay route, one checker, one manifest entry, and one slice note.
- Keep the work scoped to the Phase 3 ABI lane rather than widening into broader subsystem closure claims.

## Boundary

- Do not treat this note as Phase 3 completion.
- Reopen it only when current `master` lands a dedicated `rbtree` packet or when the roadmap anchor changes.
