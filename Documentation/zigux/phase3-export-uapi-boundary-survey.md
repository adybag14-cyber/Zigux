# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and starter UAPI boundary that still sits inside the bounded Phase 3 ABI substrate packet on live `master`.
## Status
  * `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
  * `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`
  * `PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`
  * `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-layout-replay-plus-shared-review-surface-refresh`
  * `PHASE3_LAYOUT_REPLAY_OWNERSHIP=export-uapi-packet-owns-shared-boundary-header-layout-replay`
  * `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
  * `PHASE3_EXPORT_SHIM_BLOB_SHA=c04698d10959a6020f33ac6df85083ccf833d9db`
  * `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
  * `PHASE3_UAPI_VERSION_BLOB_SHA=f07b3a87bab362782467309d06549d3a4c2c16d0`
  * `PHASE3_LINUX_HEADER_PATH=include/linux/zigux.h`
  * `PHASE3_LINUX_HEADER_BLOB_SHA=c8cfd9590d2d0039ad087bb020a236fdc0a2b4ff`
  * `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
  * `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
  * `PHASE3_EXPORT_UAPI_LAYOUT_PATH=zigux/tests/phase3_export_uapi_layout.zig`
  * `PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA=b76e6ae686ea7e8baa600f4f29b5925b3bb64e00`
## Live Boundary

The blob markers above are the authoritative packet-local evidence for the currently shipped export shim, starter UAPI helper, Linux-facing aggregation header, canonical ABI header, and focused layout replay in this current-head public GitHub fallback readback.
  * `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared `Header`, `HeaderCompatibility`, and `HeaderAcceptance` types plus the boundary-header helpers from `zigux/uapi/version.zig`, by exposing an explicit `compatibilityStatus()` relay for status-based callers, and by normalizing explicit success or errno-style export status values.
  * `zigux/uapi/version.zig` keeps the starter UAPI version contract reviewable through canonical versus future-compatible boundary-header helpers plus a compact `acceptHeader()` path that returns compatibility classification beside the canonical header without widening into a broader UAPI packet.
  * `zigux/tests/phase3_export_uapi_layout.zig` keeps the focused layout replay explicit by pinning the named `export_shim.Header` relay beside boundary-header size, field offsets, compatibility predicates, compatibility classification, accepted-header canonicalization, and compatibility-status relays across the export shim and starter UAPI helper.
  * `include/linux/zigux.h` remains the Linux-facing aggregation header for already-landed Phase 3 boundary helpers, including the explicit `zigux_status_ok()` and `zigux_status_err()` relay surface.
  * `include/zigux/abi.h` remains the canonical ABI layout source of truth for `struct zigux_boundary_header`, `struct zigux_export_status`, and the shared version and status flags those starter helpers depend on.
## Review Ownership

The Phase 3 roadmap wants one blessed export surface with explicit ownership and human review. The current packet stays honest only if that review split stays narrow and explicit.
  * the export/UAPI packet owns the starter boundary wording, the shared header relay contract, and the focused `zigux/tests/phase3_export_uapi_layout.zig` replay for this surface.
  * the shared ABI slice in `Documentation/zigux/phase3-abi-slice.md` still owns the broader `include/linux/zigux.h` aggregation rule, so this packet-local survey proves only the starter export/UAPI subset it directly replays rather than claiming the whole Linux-facing header.
  * helper-local slices still own semantic growth once a new helper family stops being just starter export/UAPI boundary plumbing.
  * on current `master`, the required shared review-surface refresh should keep this packet-local survey explicit beside `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/README.md`, and `scripts/zigux/README.md` so the starter export/UAPI boundary does not collapse back into an implied header-only claim.
  * any new top-level export/UAPI entry point should land with a resurvey of this note, a matching `phase3_export_uapi_layout` replay update, and one shared review-surface refresh instead of being implied by broader Phase 3 header growth alone.
## Current Gap

The Phase 3 roadmap calls for the first permanent C/Zigux boundary through explicit export shims, curated bindings, and a narrow `zigux/uapi/` starter. Live `master` now satisfies that starter packet, but it still stops intentionally short of broader UAPI growth.
  * `zigux/uapi/` still ships only `version.zig`, so the current UAPI surface remains a starter boundary-header contract rather than a wider exported family.
  * `zigux/tests/phase3_export_uapi.zig` and `zigux/tests/phase3_export_uapi_build.zig` already stage a `dev_t`-adjacent follow-up, but the live `zigux/uapi/` tree still has no `zigux/uapi/dev_t.zig`, so that behavior packet is a boundary-gap cue rather than shipped UAPI closure.
  * the export shim still operates as a relay plus status-normalization layer; it does not yet claim broader header governance, generated bindings growth, or new Linux-facing entry points beyond the already-landed starter helpers.
  * the next safe packet-local step is either landing one real `zigux/uapi/dev_t.zig` family with its matching replay and shared review-surface refresh or trimming the staged `phase3_export_uapi` behavior packet back to the version-only starter, rather than letting review surfaces imply wider UAPI coverage than the tree actually ships.
  * `include/linux/zigux.h` now aggregates many approved Phase 3 helper families, so any new top-level export/UAPI entry point has to land with a fresh shared-ABI readback and an explicit packet-local resurvey instead of being implied by that broader header.
  * the shared review surface for this packet is intentionally narrow, so future growth should refresh the dedicated survey, the focused layout replay, and one shared review surface together rather than relying on header growth alone to imply review coverage.
## Scope

This survey stays packet-local to the shipped export-shim and starter UAPI boundary. It does not claim broader header governance, generated bindings growth, or new helper families outside the bounded Phase 3 ABI packet.
