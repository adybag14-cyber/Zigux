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
- `PHASE3_CURRENT_RBTREE_STATUS=phase7-helper-exists-but-phase3-interop-slice-is-missing`
- `PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors`
- `PHASE3_INTEROP_GAP=rbtree-interop-slice-still-missing`
- `PHASE3_NEXT_BOUNDED_STEP=roadmap-backed-rbtree-interop-survey-or-slice-before-more-chrdev-growth`

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
- `zigux/tests/phase3_low_level_wrappers.zig` plus `zigux/tests/phase3_low_level_wrappers_build.zig` now keep that atomic, barrier, and MMIO packet reviewable on its own focused replay path, including the scoped MMIO entry points routed back through the declared narrow unsafe layer
- `zigux/unsafe/narrow.zig` keeps the unsafe boundary narrow and named
- `zigux/helpers/bitmap_view.zig` and `zigux/helpers/cpumask_view.zig` provide the first roadmap-backed reusable interop seam

The live tree also contains additional bounded interop helpers beyond the roadmap's initial anchor list:

- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig`
- `zigux/helpers/err_ptr.zig`, `xa_value.zig`, `xarray_slot_view.zig`, `idr_slot_view.zig`
- `zigux/helpers/ida_bitmap_view.zig`, `ida_alloc_view.zig`, `ida_range_view.zig`, `ida_range_set_view.zig`, `ida_policy_view.zig`

The largest adjacent growth, though, is now the `chrdev_*` planning ladder. Current `master` no longer stops at one or two exploratory helpers here:

- early chrdev planning is already published through `zigux/helpers/cdev_add_plan.zig`, `cdev_lookup_plan.zig`, `chrdev_open_plan.zig`, `chrdev_fops_plan.zig`, and `chrdev_route_plan.zig`
- the same ladder already continues through `zigux/helpers/chrdev_io_plan.zig`, `chrdev_xfer_plan.zig`, `chrdev_complete_plan.zig`, and `chrdev_notify_plan.zig`
- later slices already widen that planning family further into notification acknowledgement and windowing surfaces such as `zigux/helpers/chrdev_notify_ack_plan.zig` and `chrdev_notify_ack_window_plan.zig`
- the documentation packet mirrors that spread with published slice notes such as `Documentation/zigux/phase3-cdev-add-slice.md`, `phase3-chrdev-open-slice.md`, `phase3-chrdev-fops-slice.md`, `phase3-chrdev-route-slice.md`, `phase3-chrdev-io-slice.md`, `phase3-chrdev-complete-slice.md`, `phase3-chrdev-notify-slice.md`, `phase3-chrdev-notify-ack-slice.md`, and `phase3-chrdev-notify-ack-window-slice.md`
- `include/zigux/abi.h` and `zigux/bindings/abi.zig` now carry a matching expansion of chrdev planning flags, views, and summaries far beyond the original four roadmap anchors

Those slices are real repo state, but they should not be confused with closure of the original roadmap anchors or with closure of the broader Phase 3 destination around export shims and UAPI.

## Current Gap

The largest roadmap-backed interop gap is still `lib/rbtree.c`.

Why this remains a real gap:

- the roadmap names `lib/rbtree.c` as a Phase 3 anchor
- the current repo has no `zigux/helpers/rbtree_*` Phase 3 interop helper family
- the current repo has no `Documentation/zigux/phase3-rbtree-*.md` slice note
- the current repo has no `zigux/tests/phase3_rbtree_*.zig` parity packet
- the existing `Documentation/zigux/phase7-rbtree-slice.md` is useful evidence for the Phase 7 runtime-helper lane, but it is not a substitute for a Phase 3 boundary-facing interop slice

There is also a smaller but still explicit boundary gap around UAPI scope:

- the roadmap destination list includes `zigux/uapi/` as part of the permanent Phase 3 boundary
- the current repo still only exposes the bounded `zigux/uapi/version.zig` surface
- that version-and-boundary-header surface is appropriate for the current ABI substrate, but it is not full closure of the broader UAPI destination the roadmap leaves room for later

## Drift Note

The live Phase 3 tree has now grown far beyond a small side branch of `chrdev_*` planning helpers.

Current repo reality is that the exploratory chrdev packet already stretches from `cdev_add` and `chrdev_open` through route and IO planning, transfer and completion planning, notification planning, and the later notify-ack and ack-window layers, with matching ABI and binding surface growth in `include/zigux/abi.h` and `zigux/bindings/abi.zig`.

That growth is real repo state, but it still exceeds the small named anchor set in the roadmap and should be treated as adjacent exploratory surface, not as proof that the core Phase 3 roadmap contract is complete. The current repo reality is therefore:

- the ABI substrate is real
- the low-level wrapper packet is real and now has its own focused replay gate
- the export shim is real but still intentionally narrow
- the current UAPI boundary is real but still version-and-boundary-header only
- bitmap and cpumask interop are real
- several additional interop slices are real
- the chrdev planning ladder is real and much broader than the original anchor list
- the roadmap-backed `rbtree` boundary is still missing
- more `chrdev_*` slice growth should wait until the roadmap-backed gap is explicitly addressed

## Next Bounded Step

The next honest Phase 3 step is one roadmap-backed `rbtree` boundary task, not another new `chrdev_*` layer.

Two acceptable bounded follow-ons from the current repo state are:

- a `phase3-rbtree` survey that maps `lib/rbtree.c` into a reviewable boundary packet with explicit non-goals
- a small `rbtree` interop slice with one curated view type, one committed parity fixture, and one shared `run-phase3-checks.py --slug ...` replay path
