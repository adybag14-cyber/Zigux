# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and starter UAPI boundary that still sits inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=shared-abi-slice-owns-linux-header-governance-export-uapi-packet-owns-starter-boundary-wording-only`
- `PHASE3_C_HEADER_GROWTH_RULE=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-layout-replay-plus-shared-review-surface-refresh`
- `PHASE3_LAYOUT_REPLAY_OWNERSHIP=export-uapi-packet-owns-focused-starter-boundary-layout-replay`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=388ec06b094bae6be0efaf3166fc0f0a7780708e`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=e02f56f5904557a49646d8302746fb00cc397ce0`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_UAPI_DEV_T_BLOB_SHA=f346882bd50b5c2f8473a8f72be51bfd8117fcb4`
- `PHASE3_LINUX_HEADER_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_HEADER_BLOB_SHA=c8cfd9590d2d0039ad087bb020a236fdc0a2b4ff`
- `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
- `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_EXPORT_UAPI_BEHAVIOR_PATH=zigux/tests/phase3_export_uapi.zig`
- `PHASE3_EXPORT_UAPI_BEHAVIOR_BLOB_SHA=e03024ac87277a28d4eb3c1760641194ad53d211`
- `PHASE3_EXPORT_UAPI_BUILD_PATH=zigux/tests/phase3_export_uapi_build.zig`
- `PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA=8e13ad58d753202edd303348ab09f05c390427ba`
- `PHASE3_EXPORT_UAPI_LAYOUT_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA=4cfbe2db34fd29a44dac6b9716f9655d2c35e2e0`
- `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA=60e8275d6aaec4b3059bbf732e350526111c02ce`
- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_VALIDATOR_BLOB_SHA=cd1087f21efa480006c08d02966974ca6722606e`

## Live Boundary

The blob markers above are the authoritative packet-local evidence for the currently shipped export shim, starter UAPI helpers, Linux-facing aggregation header, canonical ABI header, direct export/UAPI behavior replay, direct behavior build wrapper, focused layout replay, focused layout build wrapper, and dedicated packet-local validator in this current-head public GitHub fallback readback. The dedicated Linux `zigux.h` governance note remains a coupled review surface for this packet, but it is not itself part of the blob-pinned boundary-artifact list above.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared `Header`, `HeaderCompatibility`, `HeaderAcceptance`, `HeaderEvaluation`, and `CompatibilityDecision` types plus the boundary-header helpers from `zigux/uapi/version.zig`, by exposing explicit `evaluateHeader()` and `compatibilityStatus()` relays for status-based callers, and by normalizing explicit success or errno-style export status values without widening into a larger runtime-facing shim family.
- `zigux/uapi/version.zig` keeps the first UAPI starter contract reviewable through canonical versus future-compatible boundary-header helpers plus compact `acceptHeader()`, `canonicalizeHeader()`, and `evaluateHeader()` paths that keep requested-header size deltas and acceptance evidence explicit beside the canonical header.
- `zigux/uapi/dev_t.zig` starts the next top-level UAPI family by relaying the curated `dev_t` codec, major or minor range checks, and bounded last-in-range computation through a small exported starter surface instead of widening the boundary packet through more header-only or relay-only churn.
- `zigux/tests/phase3_export_uapi.zig` plus `zigux/tests/phase3_export_uapi_build.zig` keep the direct starter-boundary behavior replay explicit by exercising canonical-header parity, future-compatible acceptance, explicit compatibility-status relays, and the new `dev_t` encode or range parity beside the shared ABI packet rather than leaving those starter semantics implied only by prose or the wider dump route.
- `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig` keep the focused layout replay explicit by pinning the named `export_shim.Header` relay beside boundary-header size, field offsets, compatibility predicates, compatibility classification, accepted-header canonicalization, compatibility-status relays, and the new `dev_t` constant plus last-in-range boundary parity across the export shim and starter UAPI helpers.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` still fail-closes on the boundary-header starter surfaces, the survey note, the Linux-facing header, the focused layout replay, the shared review surfaces, and the workflow hooks that already gate this packet. The new `dev_t` starter family currently becomes reviewable through the direct behavior replay, the focused layout replay, and the shared ABI manifest before a follow-through validator refresh lands.
- `include/linux/zigux.h` remains the Linux-facing aggregation header for already-landed Phase 3 boundary helpers, including the explicit `zigux_status_ok()` and `zigux_status_err()` relay surface plus the landed `dev_t` bit-width and mask constants that the curated `dev_t` packet still depends on.
- `include/zigux/abi.h` remains the canonical ABI layout source of truth for `struct zigux_boundary_header`, `struct zigux_export_status`, and the shared version and status flags those starter helpers depend on.
- `Documentation/zigux/phase3-linux-zigux-header-governance.md` keeps the shared-versus-packet-local ownership split explicit so `include/linux/zigux.h` growth still requires shared ABI proof instead of collapsing into header-only progress or being miscounted as export/UAPI closure by implication.

## Review Ownership

The Phase 3 roadmap wants one blessed export surface with explicit ownership and human review. The current packet stays honest only if that review split stays narrow and explicit.

- the export/UAPI packet owns the starter boundary wording, the direct `phase3_export_uapi.zig` replay, the focused `phase3_export_uapi_layout.zig` replay, and the directly coupled `scripts/zigux/validate-phase3-export-uapi-survey.py` gate for this surface; it does not own the broader Linux-header aggregation rule.
- the shared ABI slice in `Documentation/zigux/phase3-abi-slice.md` still owns the broader `include/linux/zigux.h` aggregation rule, so this packet-local survey proves only the starter export/UAPI subset it directly replays rather than claiming the whole Linux-facing header.
- helper-local slices still own semantic growth once a new helper family stops being starter export/UAPI boundary plumbing.
- on current `master`, the required shared review-surface refresh should keep this packet-local survey explicit beside `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/README.md`, and `scripts/zigux/README.md` so the starter export/UAPI boundary does not collapse back into an implied header-only claim.
- any new top-level export/UAPI entry point should land with a resurvey of this note, a matching direct `phase3_export_uapi.zig` or focused `phase3_export_uapi_layout.zig` replay update, the paired build-wrapper refresh when that replay surface changes, a validator refresh when its bounded evidence list changes, and one shared review-surface refresh instead of being implied by broader Phase 3 header growth alone.

## Current Gap

The Phase 3 roadmap calls for the first permanent C/Zigux boundary through explicit export shims, curated bindings, and a narrow `zigux/uapi/` starter. Live `master` now carries the boundary-header starter plus the first small `dev_t` starter family, so the remaining gap is no longer missing export/UAPI scaffolding; it is missing the next separately owned export-facing boundary family that can grow beyond this starter without collapsing back into shared header aggregation.

- `zigux/uapi/` now ships `version.zig` and `dev_t.zig`, so the current UAPI surface is no longer only the boundary-header contract, but it is still a starter packet rather than a wider exported family.
- the broader shared ABI slice already carries curated boundary roots in `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/notifier_abi.zig`, so the remaining export/UAPI gap is specifically the absence of the next export-facing family, not the absence of a general bindings substrate.
- the export shim still operates as a relay, explicit compatibility-evaluation wrapper, and status-normalization layer; it does not yet establish another separately owned top-level boundary family, new export-facing header, or wider generated-or-curated entry-point root beyond the shipped starter helpers.
- the next safe packet-local step is one more top-level boundary family under `zigux/uapi/` that lands with both direct behavior and focused layout replay coverage, the paired build-wrapper refresh when those replay surfaces change, manifest inclusion, a validator refresh when the packet-local evidence list changes, a shared review-surface refresh, and the corresponding `Documentation/zigux/phase3-linux-zigux-header-governance.md` refresh.
- `include/linux/zigux.h` now aggregates many approved Phase 3 helper families, so any new top-level export/UAPI entry point still has to land with a fresh shared-ABI readback and an explicit packet-local resurvey instead of being implied by this packet alone or by broader header growth.
- the shared review surface for this packet remains intentionally narrow, so future growth should refresh the dedicated survey, the focused layout replay, the packet-local validator evidence when that bounded gate changes, the Linux `zigux.h` governance note when aggregation ownership changes, and one shared review surface together rather than relying on header growth alone to imply review coverage.

## Scope

This survey stays packet-local to the shipped export-shim and starter UAPI boundary. It does not claim broader header governance, generated bindings growth, or new helper families outside the bounded Phase 3 ABI packet.
