# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-review-surface-refresh`
- `PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=082b86e38f1842bd97eaf4993788c910b092810e`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=c1ce4e6ff9ce19689e582491fd6a49d498b64306`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_UAPI_DEV_T_BLOB_SHA=bfbe71603907b2b951e4eebe29a007d9d761999c`
- `PHASE3_SHARED_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_MAKEFILE_PATH=zigux/Makefile`
- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_WORKFLOW_PATH=.github/workflows/zigux-bootstrap.yml`

## Live Boundary

The blob markers above are the packet-local evidence for the currently shipped starter export shim plus starter UAPI companions on the latest inspected `master` head. On current `master`, this packet stays narrow and routes through the shared Phase 3 build and review surfaces rather than through a dedicated export/UAPI-only replay pair.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared header and compatibility types from `zigux/uapi/version.zig`, by exposing the explicit `compatibilityStatus()` relay for status-based callers, and by keeping success-versus-errno export status normalization reviewable.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through canonical-versus-future-compatible helpers, accepted-header classification, and canonicalization logic without widening into a deeper runtime-owned ABI claim.
- `zigux/uapi/dev_t.zig` is now part of the shipped starter UAPI packet on current `master`, keeping the bounded chrdev encode, decode, and range checks readable beside the shared `include/zigux/dev_t.h` and `zigux/bindings/dev_t.zig` contract.
- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-abi`, and `make -C zigux phase3` remain the shared compile and replay routes that cover this starter export/UAPI packet on live `master`.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` is the dedicated packet-local checker that keeps this survey aligned with the shipped starter boundary files and the shared replay route.

## Review Ownership

The Phase 3 roadmap still wants a narrow and explicit permanent C/Zigux boundary. On current `master`, this packet stays honest only if the export/UAPI lane owns the starter wording without implying dedicated packet-local replay files that are not part of the live manifest-backed ABI packet.

- the export/UAPI packet owns this survey note, its packet-local validator, and the wording that points reviewers at the shared `phase3-test` route for the currently shipped starter surface.
- the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the export shim, the starter UAPI companions, and the shared replay route that are readable in the current export/UAPI lane.
- any future top-level export or UAPI growth should land with a refreshed survey and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.

## Current Gap

The current export/UAPI lane has real starter-UAPI growth in `zigux/uapi/dev_t.zig`, but some reminder surfaces can still overstate the packet beyond what the live manifest-backed ABI packet shows.

- current `master` already ships `zigux/uapi/dev_t.zig`, so this packet should not collapse back to version-only wording.
- current `master` does not need to claim dedicated `phase3_export_uapi*` replay files unless those files land in the shared ABI packet and its aligned reminder surfaces together.
- if a future run grows this packet again, refresh this survey and its packet-local checker in the same bounded step so the review surface does not lag the tree.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, and the shared Phase 3 compile route that currently exercises them. It does not claim broader header-governance growth, a larger UAPI family, dedicated export/UAPI-only replay files, or deeper runtime ownership beyond the readable starter packet on the current inspected head.
