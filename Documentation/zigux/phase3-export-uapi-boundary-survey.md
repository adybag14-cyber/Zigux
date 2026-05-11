# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-packet-local-replay-readback-plus-shared-review-surface-refresh`
- `PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-packet-local-and-shared-phase3-build-route-wording-for-the-starter-surface`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=082b86e38f1842bd97eaf4993788c910b092810e`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=c1ce4e6ff9ce19689e582491fd6a49d498b64306`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_UAPI_DEV_T_BLOB_SHA=bfbe71603907b2b951e4eebe29a007d9d761999c`
- `PHASE3_EXPORT_UAPI_TEST_PATH=zigux/tests/phase3_export_uapi.zig`
- `PHASE3_EXPORT_UAPI_BUILD_PATH=zigux/tests/phase3_export_uapi_build.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_SHARED_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_MAKEFILE_PATH=zigux/Makefile`
- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_WORKFLOW_PATH=.github/workflows/zigux-bootstrap.yml`

## Live Boundary

The blob markers above are the packet-local evidence for the currently shipped starter export shim plus starter UAPI companions on the latest inspected `master` head. The current packet also ships dedicated export/UAPI replay files again, while the compile and review route still stays shared through `zigux/tests/build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` rather than widening into an isolated Phase 3 workflow branch.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared header and compatibility types from `zigux/uapi/version.zig`, by exposing the explicit `compatibilityStatus()` relay for status-based callers, and by keeping success-versus-errno export status normalization reviewable.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through canonical-versus-future-compatible helpers, accepted-header classification, and canonicalization logic without widening into a deeper runtime-owned ABI claim.
- `zigux/uapi/dev_t.zig` is now part of the shipped starter UAPI packet on current `master`, keeping the bounded chrdev encode, decode, and range checks readable beside the shared `include/zigux/dev_t.h` and `zigux/bindings/dev_t.zig` contract.
- `zigux/tests/phase3_export_uapi.zig`, `zigux/tests/phase3_export_uapi_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` now provide the packet-local behavior and layout replay surfaces for this exact starter export/UAPI boundary.
- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-abi`, and `make -C zigux phase3` remain the shared compile and replay routes that cover this packet on live `master`.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` is the dedicated packet-local checker that keeps this survey aligned with the shipped starter boundary files, the packet-local replay surfaces, and the shared replay route.

## Review Ownership

The Phase 3 roadmap still wants a narrow and explicit permanent C/Zigux boundary. On current `master`, this packet stays honest only if the export/UAPI lane owns the starter wording and replay reminders without pretending the packet is still version-only or shared-build-only after real packet-local growth has landed.

- the export/UAPI packet owns this survey note, its packet-local validator, the dedicated `phase3_export_uapi*` replay files, and the wording that points reviewers at both the packet-local replay pair and the shared `phase3-test` route.
- the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the export shim, the starter UAPI companions, and the directly coupled replay files that are readable in the current export/UAPI lane.
- any future top-level export or UAPI growth should land with a refreshed survey, one packet-local replay readback, one shared build-route readback, and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.

## Current Gap

The current export/UAPI lane now has real packet-local growth that some older reminders can still understate.

- current `master` already ships `zigux/uapi/dev_t.zig` and the dedicated `phase3_export_uapi*` replay files again, so this packet should not collapse back to version-only or shared-build-only wording.
- the next same-family truthfulness follow-through belongs in any broader shared reminder surface that still summarizes the export/UAPI starter boundary without the landed `dev_t` companion or the dedicated replay files.
- if a future run grows this packet again, refresh this survey and its packet-local checker in the same bounded step so the review surface does not lag the tree.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, the dedicated `phase3_export_uapi*` replay files, and the shared Phase 3 compile route that currently exercises them. It does not claim broader header-governance growth, a larger UAPI family, or deeper runtime ownership beyond the readable starter packet on the current inspected head.
