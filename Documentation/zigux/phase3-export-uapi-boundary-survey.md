# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`
- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-review-surface-refresh`
- `PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=1e51196e063f0d1c8acb082ef226c32f804fcd34`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_VERSION_BLOB_SHA=393694bf5d3ab3eaf1e8ea81f2cec073b40a50eb`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_UAPI_DEV_T_BLOB_SHA=536d5a3d1444714f402ef01e6c8153c04b117e97`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_DEV_T_HEADER_BLOB_SHA=07656c97320edf4f3b68ac33c7cd307e08598615`
- `PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_SHARED_MANIFEST_BLOB_SHA=e8dbeb18c54dd2be8a73160e9283cc801622f480`
- `PHASE3_SHARED_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_SHARED_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_SHARED_INTEROP_ROUTE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_SHARED_INTEROP_MAKE=make -C zigux phase3-interop`
- `PHASE3_SHARED_MAKEFILE_PATH=zigux/Makefile`
- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_WORKFLOW_PATH=.github/workflows/zigux-bootstrap.yml`

## Live Boundary

The blob markers above, together with the shared Phase 3 manifest marker, are the packet-local evidence for the currently shipped starter export shim plus starter UAPI companions on the latest inspected `master` head. On current `master`, this packet stays narrow and routes through the shared Phase 3 build and review surfaces rather than through a dedicated export/UAPI-only replay pair.

- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared header and compatibility types from `zigux/uapi/version.zig`, by exposing the explicit `compatibilityStatus()` and `requestedExtraBytes()` relays for status-based callers, by adding status-tagged `dev_t` encode and range relays over the shipped starter `zigux/uapi/dev_t.zig` companion, and by keeping success-versus-errno export status normalization reviewable.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through canonical-versus-future-compatible helpers, accepted-header classification, explicit requested-extra-byte accounting for accepted headers, and canonicalization logic without widening into a deeper runtime-owned ABI claim.
- `include/linux/zigux.h` keeps the C-facing relay aligned with that starter contract through the named `zigux_boundary_header_make()` canonical constructor and the new `zigux_boundary_header_make_compatible()` forward-compatible constructor, without turning the Linux-facing header into a second ABI home.
- `zigux/uapi/dev_t.zig` is now part of the shipped starter UAPI packet on current `master`, keeping the bounded chrdev encode, decode, and range checks readable beside the shared `include/zigux/dev_t.h` contract and `zigux/bindings/dev_t.zig` mirror.
- `zigux/tests/fixtures/phase3_abi_manifest.json` keeps the shared Phase 3 inventory explicit for `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, this survey, and the shared dump and build route anchors, so reviewers can see the starter boundary remains manifest-backed without reintroducing retired export/UAPI-only replay files.
- `zigux/tests/phase3_abi_dump.zig` together with `zig build phase3-dump --build-file zigux/tests/build.zig` keeps the shared ABI dump readable beside this starter export/UAPI packet, so reviewers can still inspect the current boundary without reviving the removed export/UAPI-only replay files.
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `zig build phase3-test --build-file zigux/tests/build.zig`, `zig build phase3-dump --build-file zigux/tests/build.zig`, `make -C zigux phase3-abi`, `make -C zigux phase3-interop`, and `make -C zigux phase3` remain the shared interop, compile, dump, and replay routes that cover this starter export/UAPI packet on live `master`.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` is the dedicated packet-local checker that keeps this survey aligned with the shipped starter boundary files and the shared replay route.

## Review Ownership

The Phase 3 roadmap still wants a narrow and explicit permanent C/Zigux boundary. On current `master`, this packet stays honest only if the export/UAPI lane owns the starter wording without implying dedicated packet-local replay files that are not part of the live manifest-backed ABI packet.

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` owns the kernel-facing relay ownership for `zigux/kernel/export_shim.zig`, while this survey owns its own wording, its packet-local validator, and the shared `phase3-interop`, `phase3-test`, and `phase3-dump` route reminders that prove the currently shipped starter surface.
- `Documentation/zigux/phase3-linux-zigux-header-governance.md` still owns the Linux-facing aggregation-header growth rules for `include/linux/zigux.h`, whose starter boundary-header relays now expose both the canonical and forward-compatible constructor names needed to keep the C-facing side aligned with the shipped UAPI contract.
- the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the export shim, the starter UAPI companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the shared manifest marker, the shared dump anchor, and the shared replay routes that are readable in the current export/UAPI lane.
- any future top-level export or UAPI growth should land with a refreshed survey, the kernel-facing governance note when `zigux/kernel/export_shim.zig` changes, and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.

## Current Gap

The Phase 3 roadmap still requires a narrow and explicit export shim plus starter UAPI boundary. On the current inspected `master`, the same-lane survey drift is closed: this note now pins the shared manifest-backed starter packet around `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, and `include/zigux/dev_t.h`, while the Linux-facing relay now exposes a named future-compatible boundary-header constructor and the kernel-facing relay now keeps the shipped starter `dev_t` encode and range decisions status-tagged inside `zigux/kernel/export_shim.zig`. That does not close the broader Phase 3 permanent-boundary roadmap work. Current `master` still keeps `include/linux/zigux.h` as a small aggregation header, while the wider ABI substrate, curated bindings, helper-policy packet, and any future top-level export or UAPI growth remain shared Phase 3 follow-through outside this survey lane.

- current `master` already ships `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, and `zigux/tests/fixtures/phase3_abi_manifest.json`, and the dedicated survey, kernel-facing governance note, header-governance note, header-family survey, and manifest-backed inventory now keep that starter packet aligned, including the explicit accepted-header extension-byte accounting exposed through the starter version helper, the export shim relay, the kernel-facing relay over the shipped starter `dev_t` encode and range surface, and the C-facing compatible-header constructor.
- the remaining same-lane rule is to keep the shared interop, build, dump, and manifest wording accurate and to avoid claiming dedicated `phase3_export_uapi*` replay files unless those files actually land alongside the shared ABI packet and its reminder surfaces.
- broader Phase 3 completion still depends on the shared ABI slice, the bindings and governance packet, and any future top-level export or UAPI entry points staying explicit instead of treating this starter export/UAPI packet as whole-phase closure.
- if a future run grows this packet again, reopen the lane only for that concrete starter-boundary change and refresh this survey plus one shared reminder surface in the same bounded step.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the shared `zigux/tests/fixtures/phase3_abi_manifest.json` inventory marker, the shared `zigux/tests/phase3_abi_dump.zig` dump anchor, and the shared Phase 3 interop, compile, and dump routes that currently exercise them. It does not claim broader header-governance growth, a larger UAPI family, dedicated export/UAPI-only replay files, or deeper runtime ownership beyond the readable starter packet on the current inspected head.
