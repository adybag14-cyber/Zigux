# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and starter UAPI boundary that still sits inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`
- `PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=61513b232951d2f0fa5167fc7c90fa982f5949d1`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=c3c05ea2384bba3882d7a79312f429ef3ec88ca0`
- `PHASE3_LINUX_HEADER_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_HEADER_BLOB_SHA=c8cfd9590d2d0039ad087bb020a236fdc0a2b4ff`
- `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
- `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`

## Live Boundary

The blob markers above are the authoritative packet-local evidence for the currently shipped export shim, starter UAPI helper, Linux-facing aggregation header, and canonical ABI header in this connector-only run.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared boundary-header helpers from `zigux/uapi/version.zig` and by normalizing explicit success or errno-style export status values.
- `zigux/uapi/version.zig` keeps the starter UAPI version contract reviewable through canonical versus future-compatible boundary-header helpers without widening into a broader UAPI packet.
- `include/linux/zigux.h` remains the Linux-facing aggregation header for already-landed Phase 3 boundary helpers, including the explicit `zigux_status_ok()` and `zigux_status_err()` relay surface.
- `include/zigux/abi.h` remains the canonical ABI layout source of truth for `struct zigux_boundary_header`, `struct zigux_export_status`, and the shared version and status flags those starter helpers depend on.

## Current Gap

The Phase 3 roadmap calls for the first permanent C/Zigux boundary through explicit export shims, curated bindings, and a narrow `zigux/uapi/` starter. Live `master` now satisfies that starter packet, but it still stops intentionally short of broader UAPI growth.

- `zigux/uapi/` still ships only `version.zig`, so the current UAPI surface remains a starter boundary-header contract rather than a wider exported family.
- the export shim still operates as a relay plus status-normalization layer; it does not yet claim broader header governance, generated bindings growth, or new Linux-facing entry points beyond the already-landed starter helpers.
- `include/linux/zigux.h` now aggregates many approved Phase 3 helper families, so any new top-level export/UAPI entry point has to land with a fresh shared-ABI readback and an explicit packet-local resurvey instead of being implied by that broader header.

## Scope

This survey stays packet-local to the shipped export-shim and starter UAPI boundary. It does not claim broader header governance, generated bindings growth, or new helper families outside the bounded Phase 3 ABI packet.
