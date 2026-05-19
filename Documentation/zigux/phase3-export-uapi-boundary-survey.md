# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test`
- `PHASE3_EXPORT_UAPI_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py`
- `PHASE3_EXPORT_UAPI_ACTIVE_GAP=scripts/zigux/check-phase3-catalog-selftest.py`
- `PHASE3_EXPORT_UAPI_ACTIVE_GAP=Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `PHASE3_EXPORT_UAPI_ACTIVE_GAP=zigux/tests/fixtures/phase3_abi_manifest.json`

## Live Boundary

The packet-local validator is now present and should stay aligned with this survey rather than being tracked as a missing companion.

On current `master`, this packet stays narrow and explicit:

- `zigux/kernel/export_shim.zig` keeps the export boundary reviewable through `canonicalHeader`, `headerIsCanonical`, `headerIsCompatible`, `requestedExtraBytes`, and the status-tagged `validateDeviceNumber` relay.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through the current ABI version fields and `matchesCurrent`.
- `zigux/uapi/dev_t.zig` keeps the bounded chrdev validation and range checks readable beside the shared `include/zigux/dev_t.h` contract.
- `include/linux/zigux.h` keeps the C-facing boundary helpers aligned with the shared ABI header and the starter `dev_t` packet.
- `zigux/tests/phase3_export_uapi_layout.zig` together with `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the `BoundaryHeader` and `ExportStatus` size, alignment, and field-offset contract visible on the direct replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.

Current `master` does directly serve `scripts/zigux/phase3_catalog.py` as the bounded Phase 3 catalog helper, but that one helper should not be used to imply that the separate catalog-selftest guard or manifest-backed ABI inventory have returned.

## Current Gap

The remaining repo-reality gaps for this packet are still the separate catalog-selftest guard, the linux-header governance note, and the shared manifest-backed inventory:

- `scripts/zigux/check-phase3-catalog-selftest.py`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

This survey should stay truthful about those missing companions rather than presenting them as shipped starter-boundary evidence.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig` replay pair, the bounded catalog helper at `scripts/zigux/phase3_catalog.py`, and the packet-local validator at `scripts/zigux/validate-phase3-export-uapi-survey.py`.

It does not claim a returned Phase 3 catalog-selftest guard, a returned linux-header governance note, or a returned manifest-backed ABI inventory that current `master` still does not materialize.
