# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-review-surface-refresh`
- `PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=87fce1eb48ab80d58282d011a9819ab1e11169bd`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=393694bf5d3ab3eaf1e8ea81f2cec073b40a50eb`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_UAPI_DEV_T_BLOB_SHA=536d5a3d1444714f402ef01e6c8153c04b117e97`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_DEV_T_HEADER_BLOB_SHA=07656c97320edf4f3b68ac33c7cd307e08598615`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_ZIGUX_H_BLOB_SHA=6ca555f450d674aaf13cb617e364c76ee921a954`
- `PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_SHARED_MANIFEST_BLOB_SHA=9021b513f3090c87effac4375b03fea5584a3ee0`
- `PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_SHARED_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_COMPILE_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_SHARED_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_SHARED_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_SHARED_INTEROP_ROUTE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_SHARED_INTEROP_MAKE=make -C zigux phase3-interop`
- `PHASE3_SHARED_ABI_MAKE=make -C zigux phase3-abi`
- `PHASE3_SHARED_AGGREGATE_MAKE=make -C zigux phase3`
- `PHASE3_SHARED_MAKEFILE_PATH=zigux/Makefile`
- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_WORKFLOW_PATH=.github/workflows/zigux-bootstrap.yml`

## Live Boundary

The blob markers above, together with the shared Phase 3 manifest marker, are the packet-local evidence for the currently shipped starter export shim plus starter UAPI companions on the latest inspected `master` head. On current `master`, this packet stays narrow: the compile, dump, and aggregate routes still run through the shared Phase 3 build surfaces, while one focused layout replay now keeps the exact `BoundaryHeader` and `ExportStatus` contract explicit without reopening a broader export/UAPI-only test family.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared header, compatibility, and evaluation types from `zigux/uapi/version.zig`, by exposing the explicit `evaluateHeader()`, `compatibilityStatus()`, and `requestedExtraBytes()` relays for status-based callers, by adding status-tagged `dev_t` encode and range relays plus the pure `decodeDeviceNumber()` view over the shipped starter `zigux/uapi/dev_t.zig` companion, and by keeping success-versus-errno export status normalization reviewable.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through canonical-versus-future-compatible helpers, accepted-header classification, explicit requested-extra-byte accounting for accepted headers, and canonicalization logic without widening into a deeper runtime-owned ABI claim.
- `include/linux/zigux.h` keeps the C-facing relay aligned with that starter contract through the named `zigux_boundary_header_make()` canonical constructor, `zigux_boundary_header_make_compatible()` forward-compatible constructor, the thin `zigux_boundary_header_is_current_abi_version()`, `zigux_boundary_header_is_compatible_size()`, and `zigux_boundary_header_is_canonical_size()` predicates, and the direct `zigux_boundary_header_is_compatible()` plus `zigux_boundary_header_is_canonical()` whole-header acceptance relays, without turning the Linux-facing header into a second ABI home.
- `zigux/uapi/dev_t.zig` is now part of the shipped starter UAPI packet on current `master`, keeping the bounded chrdev encode, decode, and range checks readable beside the shared `include/zigux/dev_t.h` contract and `zigux/bindings/dev_t.zig` mirror.
- `zigux/tests/phase3_export_uapi_layout.zig` together with `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the starter `BoundaryHeader` and `ExportStatus` size, alignment, and field-offset contract visible on the direct replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, without widening into new helper chains or a second export namespace.
- `zigux/tests/fixtures/phase3_abi_manifest.json` keeps the shared Phase 3 inventory explicit for `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, this survey, the focused layout replay pair, and the shared dump and build route anchors, so reviewers can see the starter boundary remains manifest-backed without reintroducing retired export/UAPI-only replay files.
- `zigux/tests/phase3_abi_dump.zig` together with `zig build phase3-dump --build-file zigux/tests/build.zig` keeps the shared ABI dump readable beside this starter export/UAPI packet, so reviewers can still inspect the current boundary without reviving the removed export/UAPI-only replay files.
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` is the focused exact-shape replay for this starter boundary; `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `zig build phase3-test --build-file zigux/tests/build.zig`, `zig build phase3-dump --build-file zigux/tests/build.zig`, `make -C zigux phase3-abi`, `make -C zigux phase3-interop`, and `make -C zigux phase3` remain the shared interop, compile, dump, and replay routes that cover the broader starter export/UAPI packet on live `master`.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` is the dedicated packet-local checker that keeps this survey aligned with the shipped starter boundary files and the shared replay route.

## Review Ownership

The Phase 3 roadmap still wants a narrow and explicit permanent C/Zigux boundary. On current `master`, this packet stays honest only if the export/UAPI lane owns the starter wording without implying dedicated packet-local replay files that are not part of the live manifest-backed ABI packet.

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` owns the kernel-facing relay ownership for `zigux/kernel/export_shim.zig`, while this survey owns its own wording, its packet-local validator, the focused layout replay reminder, and the shared `phase3-interop`, `phase3-test`, and `phase3-dump` route reminders that prove the currently shipped starter surface.
- `Documentation/zigux/phase3-linux-zigux-header-governance.md` still owns the Linux-facing aggregation-header growth rules for `include/linux/zigux.h`, whose starter boundary-header relays now expose both the canonical and forward-compatible constructor names needed to keep the C-facing side aligned with the shipped UAPI contract.
- the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the export shim, the starter UAPI companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused layout replay pair, the shared manifest marker, the shared dump anchor, and the shared replay routes that are readable in the current export/UAPI lane.
- any future top-level export or UAPI growth should land with a refreshed survey, the kernel-facing governance note when `zigux/kernel/export_shim.zig` changes, and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.

## Current Gap

The Phase 3 roadmap still requires a narrow and explicit export shim plus starter UAPI boundary. On the current inspected `master`, the packet-local layout-proof gap is now closed: this note pins the shared manifest-backed starter packet around `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, and `include/zigux/dev_t.h`, while the focused layout replay pair keeps the exact `BoundaryHeader` and `ExportStatus` contract visible beside the existing shared compile and dump routes. The remaining repo-reality gap visible from this lane is not missing layout proof but broader starter-boundary growth: `zigux/uapi/` still stays at the bounded version-plus-`dev_t` surface, and the shared Linux-style routes still own the broader compile and dump packet around that starter boundary.

- current `master` already ships `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/fixtures/phase3_abi_manifest.json`, and the dedicated survey, kernel-facing governance note, header-governance note, header-family survey, manifest-backed inventory, and focused layout replay now keep that starter packet aligned, including the explicit accepted-header extension-byte accounting exposed through the starter version helper, the kernel-facing evaluation and status relays in `zigux/kernel/export_shim.zig`, the starter decode view over `dev_t`, the C-facing canonical and compatible-header constructors, the thin ABI-version, size, and whole-header compatibility predicates, and the dedicated `include/linux/zigux.h` blob marker that keeps the Linux-facing relay evidence explicit beside the starter UAPI file markers.
- the remaining same-lane rule is to keep the focused layout replay, the shared interop, build, dump, and manifest wording accurate, and to avoid claiming broader dedicated export/UAPI test families or new helper chains unless those files actually land beside the starter packet.
- the next adjacent same-lane follow-up is to wire the focused layout replay through shared convenience routes only if a fresh repo reread shows that the already-shipped starter packet needs that extra direct replay in the default Make path instead of keeping it as a focused direct build step.
- broader Phase 3 completion still depends on the shared ABI slice, the bindings and governance packet, and any future top-level export or UAPI entry points staying explicit instead of treating this starter export/UAPI packet as whole-phase closure.
- if a future run grows this packet again, reopen the lane only for that concrete starter-boundary change and refresh this survey plus one shared reminder surface in the same bounded step.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig` replay pair, the shared `zigux/tests/fixtures/phase3_abi_manifest.json` inventory marker, the shared `zigux/tests/phase3_abi_dump.zig` dump anchor, and the shared Phase 3 interop, compile, and dump routes that currently exercise them. It does not claim broader header-governance growth, a larger UAPI family, dedicated export/UAPI-wide compile routes, or deeper runtime ownership beyond the readable starter packet on the current inspected head.
