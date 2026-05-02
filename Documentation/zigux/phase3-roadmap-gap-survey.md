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
- `PHASE3_CURRENT_RBTREE_STATUS=phase3-survey-exists-but-phase3-interop-slice-is-missing`
- `PHASE3_CURRENT_RBTREE_SURVEY=Documentation/zigux/phase3-rbtree-interop-survey.md`
- `PHASE3_CURRENT_RBTREE_EVIDENCE=Documentation/zigux/phase3-rbtree-interop-survey.md,tools/lib/rbtree.zig,lib/rbtree.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors`
- `PHASE3_INTEROP_GAP=rbtree-interop-slice-still-missing`
- `PHASE3_NEXT_BOUNDED_STEP=small-phase3-rbtree-interop-slice-before-more-chrdev-growth`

## Roadmap Contract

Phase 3 is supposed to define the permanent C and Zigux boundary around four named anchors:

- `rust/exports.c`
- `lib/bitmap.c`
- `lib/rbtree.c`
- `lib/cpumask.c`

The roadmap-backed substrate requirements are also explicit:

- export shims
- curated bindings
- layout assertions
- panic and allocator policy
- approved atomic, barrier, and MMIO wrappers
- a narrow unsafe surface

The recommended Phase 3 destinations also explicitly include `zigux/kernel/` and `zigux/uapi/`, so both the export shim and the current UAPI surface matter when judging whether the boundary is honestly represented.

## Live Repo Reality

The current tree already carries the bounded ABI substrate and the first reusable interop helpers that the roadmap expects:

- `include/zigux/abi.h` and `include/linux/zigux.h` define the curated C-facing boundary
- `zigux/bindings/abi.zig` mirrors that boundary on the Zig side
- `zigux/kernel/export_shim.zig` keeps the export status surface explicit, and it now also keeps the boundary-header constructor and compatibility path reviewable without widening into a broader export namespace
- `zigux/uapi/version.zig` keeps one minimal UAPI surface aligned to the ABI version, and it now also exposes the boundary-header constructor and compatibility check without widening into a broader UAPI shim family
- `zigux/helpers/layout_assert.zig`, `panic_policy.zig`, `allocator_policy.zig`, `atomic.zig`, `barrier.zig`, and `mmio.zig` cover the low-level policy and wrapper packet
- `zigux/tests/phase3_low_level_wrappers.zig` plus `zigux/tests/phase3_low_level_wrappers_build.zig` keep that atomic, barrier, and MMIO packet reviewable on its own focused replay path, including the scoped MMIO entry points routed back through the declared narrow unsafe layer
- `zigux/unsafe/narrow.zig` keeps the unsafe boundary narrow and named
- `zigux/helpers/bitmap_view.zig` and `zigux/helpers/cpumask_view.zig` provide the first roadmap-backed reusable interop seam

The live tree also contains additional bounded interop helpers beyond the roadmap's initial anchor list:

- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig`
- `zigux/helpers/err_ptr.zig`, `xa_value.zig`, `xarray_slot_view.zig`, `idr_slot_view.zig`
- `zigux/helpers/ida_bitmap_view.zig`, `ida_alloc_view.zig`, `ida_range_view.zig`, `ida_range_set_view.zig`, `ida_policy_view.zig`

The repo also already carries real `rbtree` evidence outside the still-missing Phase 3 boundary-facing slice:

- `tools/lib/rbtree.zig` and `Documentation/zigux/phase1-closure.md` record the earlier host-helper parity packet
- `lib/rbtree.zig`, `Documentation/zigux/phase7-rbtree-slice.md`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` record the later runtime-helper packet and its survey-backed review surface
- `Documentation/zigux/phase3-rbtree-interop-survey.md` now maps that evidence back to the original Phase 3 roadmap anchor and keeps the remaining boundary-facing gap explicit
- that evidence matters because the remaining gap is not "no rbtree work exists"; it is specifically that no Phase 3 helper, dump, fixture, or slice packet exists yet

The largest adjacent growth, though, is still the `chrdev_*` planning ladder. That packet remains real repo state, but it still exceeds the small named anchor set in the roadmap and should be treated as adjacent exploratory surface, not as proof that the core Phase 3 roadmap contract is complete.

## Current Gap

The largest roadmap-backed interop gap is still `lib/rbtree.c`.

Why this remains a real gap:

- the roadmap names `lib/rbtree.c` as a Phase 3 anchor
- the repo now has a dedicated Phase 3 `rbtree` survey note, but it still has no boundary-facing helper packet for that anchor
- the current repo still has no `zigux/helpers/rbtree*.zig` interop helper family
- the current repo still has no `Documentation/zigux/phase3-rbtree-slice.md` slice note
- the current repo still has no `zigux/tests/phase3_rbtree*.zig` dump, fixture, or parity packet
- the existing Phase 1 host-helper evidence and the later Phase 7 helper packet are useful anchors, but neither is a substitute for a Phase 3 boundary-facing interop slice

There is also a smaller but still explicit boundary gap around UAPI scope:

- the roadmap destination list includes `zigux/uapi/` as part of the permanent Phase 3 boundary
- the current repo still only exposes the bounded `zigux/uapi/version.zig` surface
- that version-and-boundary-header surface is appropriate for the current ABI substrate, but it is not full closure of the broader UAPI destination the roadmap leaves room for later

## Drift Note

The live Phase 3 tree has grown well beyond the original four-anchor roadmap packet.

Current repo reality is therefore:

- the ABI substrate is real
- the low-level wrapper packet is real and has its own focused replay gate
- the export shim is real but still intentionally narrow
- the current UAPI boundary is real but still version-and-boundary-header only
- bitmap and cpumask interop are real
- several additional interop slices are real
- the broader `chrdev_*` planning ladder is real and much wider than the original anchor list
- the dedicated Phase 3 `rbtree` survey is now real
- the roadmap-backed `rbtree` boundary-facing slice is still missing
- more `chrdev_*` slice growth should wait until that roadmap-backed gap is explicitly addressed

## Next Bounded Step

The next honest Phase 3 step is one small `rbtree` interop slice, not another new `chrdev_*` layer.

A bounded follow-on from the current repo state should include:

- one curated `rbtree` boundary-facing helper or view type
- one committed dump or parity fixture packet
- one explicit replay path that keeps the slice reviewable without widening into a full balancing or mutation port
