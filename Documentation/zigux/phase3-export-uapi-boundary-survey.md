# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and starter UAPI boundary that still sits inside the bounded Phase 3 ABI substrate packet on live `master`.
## Status
  * `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
  * `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=shared-abi-slice-owns-linux-header-governance-export-uapi-packet-owns-starter-boundary-wording-only`
  * `PHASE3_C_HEADER_GROWTH_RULE=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`
  * `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-layout-replay-plus-shared-review-surface-refresh`
  * `PHASE3_LAYOUT_REPLAY_OWNERSHIP=export-uapi-packet-owns-focused-starter-boundary-layout-replay`
  * `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
  * `PHASE3_EXPORT_SHIM_BLOB_SHA=c04698d10959a6020f33ac6df85083ccf833d9db`
  * `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
  * `PHASE3_UAPI_VERSION_BLOB_SHA=f07b3a87bab362782467309d06549d3a4c2c16d0`
  * `PHASE3_LINUX_HEADER_PATH=include/linux/zigux.h`
  * `PHASE3_LINUX_HEADER_BLOB_SHA=c8cfd9590d2d0039ad087bb020a236fdc0a2b4ff`
  * `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
  * `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
  * `PHASE3_EXPORT_UAPI_BEHAVIOR_PATH=zigux/tests/phase3_export_uapi.zig`
  * `PHASE3_EXPORT_UAPI_BEHAVIOR_BLOB_SHA=cdab0a73918b200cbc1bb8c6c7a82b9c8004be4c`
  * `PHASE3_EXPORT_UAPI_BUILD_PATH=zigux/tests/phase3_export_uapi_build.zig`
  * `PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA=6672282bd70bcf7025627a669301f421ef8530ce`
  * `PHASE3_EXPORT_UAPI_LAYOUT_PATH=zigux/tests/phase3_export_uapi_layout.zig`
  * `PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA=b76e6ae686ea7e8baa600f4f29b5925b3bb64e00`
  * `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
  * `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA=2d62e73e1b87ac05fe6713a99ab3b7612f871420`
  * `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
  * `PHASE3_EXPORT_UAPI_VALIDATOR_BLOB_SHA=d7ce54ceb9b55c15a0d5323532e18b127059eb3a`
## Live Boundary

The blob markers above are the authoritative packet-local evidence for the currently shipped export shim, starter UAPI helpers, behavior replay, behavior-build companion, focused layout replay, layout-build companion, packet-local validator, Linux-facing aggregation header, and canonical ABI header in this current-head public GitHub fallback readback.
  * `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared `Header`, `HeaderCompatibility`, and `HeaderAcceptance` types plus the boundary-header helpers from `zigux/uapi/version.zig`, by exposing an explicit `compatibilityStatus()` relay for status-based callers, and by normalizing explicit success or errno-style export status values.
  * `zigux/uapi/version.zig` keeps the starter UAPI version contract reviewable through canonical versus future-compatible boundary-header helpers plus a compact `acceptHeader()` and `evaluateHeader()` path that return compatibility classification beside the canonical header without widening into a broader UAPI packet.
  * `zigux/tests/phase3_export_uapi.zig` keeps the bounded behavior replay explicit by pinning canonical versus compatible boundary-header behavior, explicit `compatibilityStatus()` relays, and the current `dev_t` starter encode-and-range parity proof inside one packet-local test surface.
  * `zigux/tests/phase3_export_uapi_build.zig` keeps compile behavior reviewable by wiring `abi_bindings`, `dev_t_bindings`, `uapi_version`, `uapi_dev_t`, and `export_shim` into a dedicated `phase3-export-uapi-tests` build step.
  * `zigux/tests/phase3_export_uapi_layout.zig` keeps the focused layout replay explicit by pinning the named `export_shim.Header` relay beside boundary-header size, field offsets, compatibility predicates, compatibility classification, accepted-header canonicalization, and compatibility-status relays across the export shim and starter UAPI helper.
  * `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the focused layout compile coverage explicit by wiring the layout replay through its own dedicated `phase3-export-uapi-layout-tests` build step.
  * `scripts/zigux/validate-phase3-export-uapi-survey.py` fail-closes the survey packet against these exact export-shim, starter-UAPI, behavior, layout, build-companion, validator, and shared-review surfaces.
  * `include/linux/zigux.h` remains the Linux-facing aggregation header for already-landed Phase 3 boundary helpers, including the explicit `zigux_status_ok()` and `zigux_status_err()` relay surface.
  * `include/zigux/abi.h` remains the canonical ABI layout source of truth for `struct zigux_boundary_header`, `struct zigux_export_status`, and the shared version and status flags those starter helpers depend on.
## Review Ownership

The Phase 3 roadmap wants one blessed export surface with explicit ownership and human review. The current packet stays honest only if that review split stays narrow and explicit.
  * the export/UAPI packet owns the starter boundary wording, the packet-local validator, the bounded behavior and layout replays, and their directly coupled build companions for this surface.
  * the shared ABI slice in `Documentation/zigux/phase3-abi-slice.md` and the shared header-governance note in `Documentation/zigux/phase3-linux-zigux-header-governance.md` still own the broader `include/linux/zigux.h` aggregation rule, so this packet-local survey proves only the starter export/UAPI subset it directly replays rather than claiming the whole Linux-facing header.
  * helper-local slices still own semantic growth once a new helper family stops being just starter export/UAPI boundary plumbing.
  * on current `master`, the required shared review-surface refresh should keep this packet-local survey explicit beside `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/README.md`, and `scripts/zigux/README.md` so the starter export/UAPI boundary does not collapse back into an implied header-only claim.
  * any new top-level export/UAPI entry point should land with a resurvey of this note, a matching replay or build-companion refresh, and one shared review-surface refresh instead of being implied by broader Phase 3 header growth alone.
## Current Gap

The Phase 3 roadmap calls for the first permanent C/Zigux boundary through explicit export shims, curated bindings, and a narrow `zigux/uapi/` starter. Live `master` now satisfies that starter packet, but it still stops intentionally short of broader UAPI growth.
  * `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`, so the current UAPI surface is no longer version-only even though it still remains a narrow starter family rather than a broader exported boundary.
  * `zigux/tests/phase3_export_uapi.zig`, `zigux/tests/phase3_export_uapi_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and the packet-local validator already replay that bounded `dev_t`-adjacent follow-up and its compile surfaces, but the packet still stops short of broader UAPI family growth beyond the boundary-header and `dev_t` starters.
  * the export shim still operates as a relay plus status-normalization layer; it does not yet claim broader header governance, generated bindings growth, or new Linux-facing entry points beyond the already-landed starter helpers.
  * any future top-level export/UAPI family beyond `version.zig` and `dev_t.zig` should land with its own matching replay and shared review-surface refresh instead of being implied by broader header aggregation alone.
  * `include/linux/zigux.h` now aggregates many approved Phase 3 helper families, so any new top-level export/UAPI entry point has to land with a fresh shared-ABI readback and an explicit packet-local resurvey instead of being implied by that broader header.
  * the shared review surface for this packet is intentionally narrow, so future growth should refresh the dedicated survey, the focused layout replay, and one shared review surface together rather than relying on header growth alone to imply review coverage.
## Scope

This survey stays packet-local to the shipped export-shim and starter UAPI boundary. It does not claim broader header governance, generated bindings growth, or new helper families outside the bounded Phase 3 ABI packet.
