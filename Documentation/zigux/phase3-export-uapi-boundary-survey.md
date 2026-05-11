# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-build-route-readback-plus-shared-review-surface-refresh`
- `PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=082b86e38f1842bd97eaf4993788c910b092810e`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=c1ce4e6ff9ce19689e582491fd6a49d498b64306`
- `PHASE3_SHARED_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_MAKEFILE_PATH=zigux/Makefile`
- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_WORKFLOW_PATH=.github/workflows/zigux-bootstrap.yml`

## Live Boundary

The blob markers above are the packet-local evidence for the currently shipped starter export shim and starter UAPI helper on the latest inspected `master` head. The compile and review route for this exact surface is shared through `zigux/tests/build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` rather than a dedicated export/UAPI-only build file on current `master`.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared header and compatibility types from `zigux/uapi/version.zig`, by exposing the explicit `compatibilityStatus()` relay for status-based callers, and by keeping success-versus-errno export status normalization reviewable.
- `zigux/uapi/version.zig` keeps the starter UAPI version contract explicit through canonical-versus-future-compatible boundary-header helpers, accepted-header classification, and canonicalization logic without widening into a broader UAPI family claim.
- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-abi`, and `make -C zigux phase3` are the currently shipped compile and replay routes that cover this starter surface on live `master`.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` is the dedicated packet-local checker that keeps this survey aligned with the shipped starter boundary files and the shared replay route.

## Review Ownership

The Phase 3 roadmap still wants a narrow and explicit permanent C/Zigux boundary. On current `master`, this packet stays honest only if the export/UAPI lane owns the starter wording and shared-build-route reminders without overstating missing dedicated replay files.

- the export/UAPI packet owns this survey note, its packet-local validator, and the wording that points reviewers at the shared `phase3-test` replay route for the starter export boundary.
- the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the starter export shim plus starter UAPI version helper that are directly readable in the current export/UAPI lane.
- any future top-level export or UAPI growth should land with a refreshed survey, one shared build-route readback, and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.

## Current Gap

The current export/UAPI lane is intentionally smaller than some older reminders still suggest.

- the latest inspected `master` head no longer exposes dedicated `zigux/tests/phase3_export_uapi*.zig` build or replay files in this packet, so the honest compile evidence for now is the shared `phase3-test` route rather than a packet-local build entrypoint.
- the packet also should not imply a separate Linux-header-governance note or broader starter-UAPI family beyond `zigux/uapi/version.zig` unless those surfaces are readable and shipped again on current `master`.
- if a future run restores dedicated export/UAPI-only replay files, the next step in this lane should be to resurvey this note and retighten the checker around those newly shipped packet-local surfaces.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter UAPI version helper, and the shared Phase 3 compile route that currently exercises them. It does not claim broader header governance, wider UAPI family growth, or missing packet-local replay files that are not readable on the current inspected head.
