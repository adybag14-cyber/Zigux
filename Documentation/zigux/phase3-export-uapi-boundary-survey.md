# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.
## Status
- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-review-surface-refresh`
- `PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=16a778addd1759fa04e26ffedd00d5a9d326cf28`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=69309fb8a83dffbfc3e4b21dd0d6859dc94eb41b`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_UAPI_DEV_T_BLOB_SHA=f57b282749dde9f0c6a0bd93b2d7d91f05d37d0e`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_DEV_T_HEADER_BLOB_SHA=135ac5b7636b2442722f9c435feed04263b3f6bd`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_ZIGUX_H_BLOB_SHA=fe08aa35b39b1eb00520a6e24c0243c2070f2e81`
- `PHASE3_SHARED_MANIFEST_GAP=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_MAKE=make -C zigux phase3-export-uapi-layout-test`
- `PHASE3_SHARED_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_COMPILE_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_SHARED_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_SHARED_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_SHARED_INTEROP_ROUTE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_SHARED_INTEROP_MAKE=make -C zigux phase3-interop`
- `PHASE3_SHARED_ABI_MAKE=make -C zigux phase3-abi`
- `PHASE3_SHARED_AGGREGATE_MAKE=make -C zigux phase3`
- `PHASE3_SHARED_MAKEFILE_PATH=zigux/Makefile`
- `PHASE3_LINUX_HEADER_GOVERNANCE_GAP=Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `PHASE3_EXPORT_UAPI_VALIDATOR_GAP=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_WORKFLOW_PATH=.github/workflows/zigux-bootstrap.yml`
## Live Boundary
The blob markers above are the packet-local evidence for the currently shipped starter export shim plus starter UAPI companions on the latest inspected `master` head.
On current `master`, this packet stays narrow: the compile, dump, and aggregate routes still run through the shared Phase 3 build surfaces, while one focused layout replay now keeps the exact `BoundaryHeader` and `ExportStatus` contract explicit without reopening a broader export/UAPI-only test family.
- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared header, compatibility, and evaluation types from `zigux/uapi/version.zig`, by exposing the explicit `evaluateHeader()`, `compatibilityStatus()`, and `requestedExtraBytes()` relays for status-based callers, by exposing status-tagged `validateDeviceNumber()`, `validateDeviceRange()`, `encodeDeviceNumber()`, and `lastDeviceNumberInRange()` helpers plus the pure `decodeDeviceNumber()` view over the shipped starter `zigux/uapi/dev_t.zig` companion, and by keeping success-versus-errno export status normalization reviewable.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through canonical-versus-future-compatible helpers, accepted-header classification, explicit requested-extra-byte accounting for accepted headers, and canonicalization logic without widening into a deeper runtime-owned ABI claim.
- `include/linux/zigux.h` keeps the C-facing relay aligned with that starter contract through the named `zigux_boundary_header_make()` canonical constructor, `zigux_boundary_header_make_compatible()` forward-compatible constructor, the thin `zigux_boundary_header_is_current_abi_version()`, `zigux_boundary_header_is_compatible_size()`, and `zigux_boundary_header_is_canonical_size()` predicates, and the direct `zigux_boundary_header_is_compatible()` plus `zigux_boundary_header_is_canonical()` whole-header acceptance relays, without turning the Linux-facing header into a second ABI home.
- `zigux/uapi/dev_t.zig` is now part of the shipped starter UAPI packet on current `master`, keeping the bounded chrdev validation, encode, decode, and range checks readable beside the shared `include/zigux/dev_t.h` contract and `zigux/bindings/dev_t.zig` mirror.
- `zigux/tests/phase3_export_uapi_layout.zig` together with `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the starter `BoundaryHeader` and `ExportStatus` size, alignment, and field-offset contract visible on the direct replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` and the Linux-style `make -C zigux phase3-export-uapi-layout-test` convenience route, without widening into new helper chains or a second export namespace.
- repeated authenticated current-`master` reads still return missing for `zigux/tests/fixtures/phase3_abi_manifest.json`, so keep the focused layout replay pair, the shared dump anchor, and the shared build routes explicit here without implying that a dedicated export/UAPI manifest has returned beside them.
- `zigux/tests/phase3_abi_dump.zig` together with `zig build phase3-dump --build-file zigux/tests/build.zig` keeps the shared ABI dump readable beside this starter export/UAPI packet, so reviewers can still inspect the current boundary without reviving the removed export/UAPI-only replay files.
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` is the focused exact-shape replay for this starter boundary; `make -C zigux phase3-export-uapi-layout-test`, `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `zig build phase3-test --build-file zigux/tests/build.zig`, `zig build phase3-dump --build-file zigux/tests/build.zig`, `make -C zigux phase3-abi`, `make -C zigux phase3-interop`, and `make -C zigux phase3` remain the shared interop, compile, dump, and replay routes that cover the broader starter export/UAPI packet on live `master`.
- repeated authenticated current-`master` reads still return missing for `scripts/zigux/validate-phase3-export-uapi-survey.py`, so this directly readable survey plus the focused layout replay pair should stay explicit without implying that the dedicated packet-local validator has returned.
## Review Ownership

The Phase 3 roadmap still wants a narrow and explicit permanent C/Zigux boundary. On current `master`, this packet stays honest only if the export/UAPI lane owns the starter wording without implying dedicated packet-local replay files or governance notes that are not part of the live packet.
- `Documentation/zigux/phase3-kernel-export-shim-governance.md` owns the kernel-facing relay ownership for `zigux/kernel/export_shim.zig`, while this survey owns its own wording, the focused layout replay reminder, and the shared `phase3-export-uapi-layout-test`, `phase3-interop`, `phase3-test`, and `phase3-dump` route reminders that prove the currently shipped starter surface.
- repeated authenticated current-`master` reads still return missing for `Documentation/zigux/phase3-linux-zigux-header-governance.md`, so keep the readable `include/linux/zigux.h` boundary constructors and predicates explicit here without presenting that missing governance note as shipped packet evidence.
- the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the export shim, the starter UAPI companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused layout replay pair, the direct `phase3-export-uapi-layout-test` convenience route, the shared dump anchor, and the shared replay routes that are readable in the current export/UAPI lane.
- any future top-level export or UAPI growth should land with a refreshed survey, the kernel-facing governance note when `zigux/kernel/export_shim.zig` changes, and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.
## Current Gap
The Phase 3 roadmap still requires a narrow and explicit export shim plus starter UAPI boundary.
On the current inspected `master`, the packet-local layout-proof gap and the direct convenience-route gap are now closed: this note pins the readable starter packet around `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, and `include/zigux/dev_t.h`, while the focused layout replay pair now stays reachable through both the direct Zig build step and the Linux-style `phase3-export-uapi-layout-test` route beside the existing shared compile and dump routes.
The remaining repo-reality gaps visible from this lane are the missing packet-local validator, the missing linux-header governance note, and the missing shared manifest-backed inventory: repeated authenticated current-`master` reads still return missing for `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, and `zigux/tests/fixtures/phase3_abi_manifest.json`, so the survey note itself has to stay truthful about those missing companions rather than presenting them as shipped starter-boundary evidence.
- current `master` already ships `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and `zigux/tests/phase3_export_uapi_layout.zig`, and the dedicated survey, the kernel-facing governance note, the focused layout replay, and the direct `phase3-export-uapi-layout-test` route now keep that starter packet aligned.
- `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, and `zigux/tests/fixtures/phase3_abi_manifest.json` are still repo-reality gaps on current `master`, so shared reminder follow-through should keep the survey note explicit as an adjacent readable surface while leaving those missing packet-local companions framed as missing until a fresh reread proves they returned.
- the next adjacent same-family follow-up is therefore a shared reminder repair, not another packet-local helper or route addition: reread `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, and this survey together, then land one bounded reminder refresh so the dedicated export/UAPI survey itself stops being framed as a missing broader route while the still-missing packet-local validator, linux-header governance note, and manifest-backed inventory stay explicit as gaps.
- the remaining same-lane rule is to keep the focused layout replay, the direct `phase3-export-uapi-layout-test` route, and the shared interop, build, dump, and manifest wording accurate, and to avoid claiming broader dedicated export/UAPI test families or new helper chains unless those files actually land beside the starter packet.
- broader Phase 3 completion still depends on the shared ABI slice, the bindings and governance packet, and any future top-level export or UAPI entry points staying explicit instead of treating this starter export/UAPI packet as whole-phase closure.
- if a future run grows this packet again, reopen the lane only for that concrete starter-boundary change and refresh this survey plus one shared reminder surface in the same bounded step.
## Scope
This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig` replay pair, the direct `make -C zigux phase3-export-uapi-layout-test` convenience route, the shared `zigux/tests/phase3_abi_dump.zig` dump anchor, and the shared Phase 3 interop, compile, and dump routes that currently exercise them.
It does not claim broader header-governance growth, a larger UAPI family, dedicated export/UAPI-wide compile routes beyond the focused layout replay target, a returned packet-local validator that current `master` still does not materialize, a returned linux-header governance note or manifest-backed inventory that current `master` still does not materialize, or deeper runtime ownership beyond the readable starter packet on the current inspected head.