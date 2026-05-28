# Phase 3 Linux `zigux.h` Header Governance

This note restores the dedicated ownership and boundary-note companion for `include/linux/zigux.h` inside the bounded Phase 3 ABI and interop substrate.

## Scope

- `PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_ZIGUX_H_BLOB_SHA=5ac94dbb0dcb1d629c7eb8f5991745f25515a485`
- `PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only`
- `PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_ZIGUX_H_EXPORT_UAPI_SURVEY=Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed ABI, boundary-header compatibility, starter dev_t review surfaces, and starter interop-policy and rbtree predicate relays only`
- `PHASE3_ZIGUX_H_HEADER_FAMILY_MACROS=ZIGUX_UAPI_ABI_MAJOR, ZIGUX_UAPI_ABI_MINOR, ZIGUX_UAPI_HEADER_FAMILY_REVISION, ZIGUX_UAPI_DEV_T_PACKET_PRESENT, and ZIGUX_UAPI_INVALID_ARGUMENT stay starter relay markers in include/linux/zigux.h rather than becoming new canonical owner definitions`
- this note governs how the Linux-facing aggregation header may grow without turning header churn into fake Phase 3 progress

## Ownership

- canonical ABI layout and boundary-header ownership stay in `include/zigux/abi.h`
- canonical starter `dev_t` ownership stays in `include/zigux/dev_t.h`
- starter Zig-side boundary companions stay in `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig`
- the shared packet summary stays in `Documentation/zigux/phase3-abi-slice.md`
- packet-local export/UAPI reminder wording stays in `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `include/linux/zigux.h` remains the Linux-facing relay and aggregation header for already-landed ABI, boundary-header, starter `dev_t`, and starter interop-policy and rbtree review surfaces only

## Growth Rule

- new top-level helper families should not land in `include/linux/zigux.h` by themselves
- growth in this header is only reviewable when the same bounded change keeps the canonical owner headers, the shared Phase 3 packet notes, and the manifest-backed inventory aligned
- helper naming churn, alias-only growth, or relay-only expansion without packet-local proof should be treated as reviewability risk rather than Phase 3 closure
- if a new boundary family needs its own ownership note, that note should land before or with the new header surface instead of being implied by aggregation here

## Current State

- live `include/linux/zigux.h` aggregates `<zigux/abi.h>` and `<zigux/dev_t.h>` instead of restating canonical struct or `dev_t` ownership locally
- the current header keeps the starter header-family relay markers `ZIGUX_UAPI_ABI_MAJOR`, `ZIGUX_UAPI_ABI_MINOR`, `ZIGUX_UAPI_HEADER_FAMILY_REVISION`, `ZIGUX_UAPI_DEV_T_PACKET_PRESENT`, and `ZIGUX_UAPI_INVALID_ARGUMENT` reviewable as Linux-facing aggregation markers rather than second ownership roots
- the current header exports a bounded version relay through `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and the status-tagged `zigux_uapi_validate_version()` gate
- the current header exports a bounded boundary-header relay through `zigux_uapi_boundary_header_current()`, `zigux_uapi_boundary_header_compatible()`, `zigux_uapi_boundary_header_has_current_abi_version()`, `zigux_uapi_boundary_header_is_canonical()`, `zigux_uapi_boundary_header_is_compatible()`, `zigux_uapi_boundary_header_extends_boundary()`, `zigux_uapi_boundary_header_requested_extra_bytes()`, `zigux_uapi_boundary_header_canonicalize()`, and the status-tagged `zigux_uapi_validate_boundary_header()` gate
- the current header keeps starter interop-policy reviewability narrow through `zigux_uapi_default_interop_policy()`, `zigux_uapi_panic_mode_is_known()`, `zigux_uapi_allocator_mode_is_known()`, `zigux_uapi_unsafe_scope_is_known()`, `zigux_uapi_interop_policy_reserved_clear()`, `zigux_uapi_interop_policy_is_recognized()`, and the status-tagged `zigux_uapi_validate_interop_policy()` relay
- the current header keeps starter rbtree-root reviewability narrow through `zigux_uapi_rbtree_root_view_is_cached()`, `zigux_uapi_rbtree_root_view_has_leftmost()`, `zigux_uapi_rbtree_root_view_is_valid()`, `zigux_uapi_rbtree_root_view_canonicalize()`, and the status-tagged `zigux_uapi_validate_rbtree_root_view()` relay
- the current header also keeps the Linux-facing compatibility aliases `zigux_boundary_header_make()`, `zigux_boundary_header_make_compatible()`, `zigux_boundary_header_is_current_abi_version()`, `zigux_boundary_header_is_compatible_size()`, `zigux_boundary_header_is_canonical_size()`, `zigux_boundary_header_is_compatible()`, `zigux_boundary_header_is_canonical()`, `zigux_boundary_header_extends_boundary()`, `zigux_boundary_header_requested_extra_bytes()`, `zigux_boundary_header_canonicalize()`, and `zigux_validate_boundary_header()` as thin relays rather than second ownership roots
- the current header keeps starter `dev_t` reviewability narrow through `zigux_uapi_dev_t_fields_is_valid()`, the status-tagged `zigux_uapi_validate_dev_t_fields()` and `zigux_uapi_validate_dev_t_components()` relays, `zigux_uapi_dev_t_fields_range_is_valid()`, and the status-tagged `zigux_uapi_validate_dev_t_range()` relay

## Boundary

- `include/linux/zigux.h` may aggregate already-approved entry points, but it should not become a second source of truth for canonical ABI layout, version ownership, or `dev_t` limits
- when the Linux-facing relay needs boundary-header helpers, keep them as thin named relays over the canonical ABI header and the shipped starter UAPI companions rather than moving semantic ownership here
- when this Linux-facing relay needs starter header-family macros, keep them as aggregation markers over the already-landed ABI and `dev_t` owner surfaces rather than treating `include/linux/zigux.h` as the new canonical owner
- when the Linux-facing relay needs status-tagged version or `dev_t` validation helpers, keep the starter UAPI companions and canonical owner headers as the single source of truth for the underlying status semantics, limits, and field meaning
- when the Linux-facing relay needs starter interop-policy or rbtree predicate helpers, keep `include/zigux/abi.h` as the single source of truth for the underlying semantics and let `include/linux/zigux.h` remain a thin Linux-facing relay surface
- when the Linux-facing relay needs `dev_t` validation helpers, keep `include/zigux/dev_t.h` as the single source of truth for the underlying limits and field meaning
- if an already-landed review surface is rehomed into `include/linux/zigux.h`, refresh this note, the shared Phase 3 slice note, and the manifest-backed inventory in the same bounded change so the owner map stays explicit
- export/UAPI starter work may reference this header, but the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly

## Non-Goals

- this note does not claim a broader UAPI family
- this note does not claim new helper-family delivery
- this note does not claim runtime, allocator, scheduler, or driver-port progress
- this note does not justify header growth without directly coupled Phase 3 packet evidence
