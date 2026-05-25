# Phase 3 ABI Header-Family Survey

This note keeps the current bounded Phase 3 ABI header-family packet truthful on `master` without widening into broader shared replay or later Phase 3 route claims.

## Scope

- `PHASE3_ABI_HEADER_FAMILY_SURVEY_PATH=Documentation/zigux/phase3-abi-header-family-survey.md`
- `PHASE3_ABI_HEADER_FAMILY_VALIDATOR_PATH=scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `PHASE3_ABI_HEADER_FAMILY_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test`
- `PHASE3_ABI_HEADER_FAMILY_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `PHASE3_ABI_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_ABI_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_ABI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py`
- `PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_VERSION_BINDING_PATH=zigux/bindings/version.zig`
- `PHASE3_DEV_T_BINDING_PATH=zigux/bindings/dev_t.zig`
- `PHASE3_HEADER_FAMILY_BINDING_PATH=zigux/bindings/header_family.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- the survey is limited to already-landed header-family version, boundary-header, starter `dev_t`, and shared header-family binding relay surfaces

## Current Header-Family Packet

- `include/linux/zigux.h` keeps the Linux-facing header-family relay bounded to `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and `zigux_uapi_validate_version()` rather than introducing a second semantic owner.
- That same Linux-facing relay keeps the header-family boundary surface reviewable through `zigux_uapi_boundary_header_current()`, `zigux_uapi_boundary_header_compatible()`, `zigux_uapi_boundary_header_has_current_abi_version()`, `zigux_uapi_boundary_header_is_canonical()`, `zigux_uapi_boundary_header_is_compatible()`, `zigux_uapi_boundary_header_extends_boundary()`, `zigux_uapi_boundary_header_requested_extra_bytes()`, and `zigux_uapi_boundary_header_canonicalize()`.
- The Linux-facing relay also keeps the compatibility aliases `zigux_boundary_header_make()`, `zigux_boundary_header_make_compatible()`, `zigux_boundary_header_is_current_abi_version()`, `zigux_boundary_header_is_compatible_size()`, `zigux_boundary_header_is_canonical_size()`, `zigux_boundary_header_is_compatible()`, `zigux_boundary_header_is_canonical()`, `zigux_boundary_header_extends_boundary()`, `zigux_boundary_header_requested_extra_bytes()`, and `zigux_boundary_header_canonicalize()` explicit as thin relays over the canonical owner headers.
- `include/zigux/abi.h` remains the canonical owner for `zigux_boundary_header`, `zigux_export_status`, `zigux_default_header()`, `zigux_compatible_header()`, `zigux_abi_version_is_current()`, `zigux_header_is_canonical()`, `zigux_header_is_compatible()`, `zigux_header_extends_boundary()`, `zigux_header_requested_extra_bytes()`, and `zigux_header_canonicalize()`.
- `include/zigux/dev_t.h` remains the canonical owner for the starter `dev_t` limits, `zigux_dev_t_fields_make()`, `zigux_mkdev()`, `zigux_major()`, `zigux_minor()`, `zigux_dev_t_fields_is_valid()`, and `zigux_dev_t_fields_range_is_valid()`.
- `zigux/uapi/version.zig` and `zigux/bindings/version.zig` keep the current version packet aligned through `current()`, `matchesCurrent()`, the `hasCurrent*` helper family, and the shared size, alignment, and field-offset constants.
- `zigux/uapi/dev_t.zig` and `zigux/bindings/dev_t.zig` keep the starter `dev_t` packet aligned through `init()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validate()`, and `validateRange()`.
- `zigux/bindings/header_family.zig` now keeps the shared header-family binding relay explicit through `currentVersion()`, `versionMatchesCurrent()`, `currentBoundaryHeader()`, `compatibleBoundaryHeader()`, `boundaryHeaderHasCurrentAbiVersion()`, `boundaryHeaderIsCanonicalSize()`, `boundaryHeaderIsCompatibleSize()`, `boundaryHeaderRequestedExtraBytes()`, `canonicalizeBoundaryHeader()`, `validateBoundaryHeaderStatus()`, `initDevTFields()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validateVersionStatus()`, `validateDevTFieldsStatus()`, `validateDevTComponentsStatus()`, and `validateDevTRangeStatus()` without creating a third semantic owner beside the canonical headers and starter bindings.
- `zigux/tests/phase3_export_uapi_layout.zig` together with `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the current version relay, canonical boundary-header relay, starter `dev_t` relay, and status-tagged export shim edges visible on the direct replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.
- Current `master` now directly serves this survey note, the packet-local validator, the shared Phase 3 slice note, the manifest-backed ABI inventory, the catalog helper, the catalog-selftest guard, and `zigux/bindings/header_family.zig` as explicit same-family companions for the bounded header-family packet.

## Boundary

- `zigux/bindings/header_family.zig` is now part of this bounded packet and should stay aligned with `include/linux/zigux.h`, `include/zigux/abi.h`, `include/zigux/dev_t.h`, the shared ABI slice note, this survey, the focused layout replay, and the manifest-backed inventory rather than being treated as still missing current-master evidence.
- this survey does not widen Phase 3 into allocator, MMIO, notifier, xarray, scheduler, or driver-port claims
- header-family growth should keep `include/zigux/abi.h`, `include/zigux/dev_t.h`, `include/linux/zigux.h`, `zigux/bindings/header_family.zig`, the shared ABI slice note, this survey, and the manifest-backed inventory aligned in the same bounded change
- any later same-family work should refresh this survey as follow-through rather than turning already-landed relay coverage into fake Phase 3 closure

## Current Gap

Current `master` no longer has a packet-local repo-reality gap for the bounded header-family survey follow-through itself. The bounded packet now includes the landed shared header-family binding relay at `zigux/bindings/header_family.zig` beside `zigux/bindings/abi.zig`, `zigux/bindings/version.zig`, `zigux/bindings/dev_t.zig`, the canonical headers, the focused export-or-UAPI layout replay, the manifest-backed inventory, the catalog helper, the catalog-selftest guard, and the packet-local survey validator.

The same bounded packet also now carries the binding-local boundary-header and status relay surface through `boundaryHeaderHasCurrentAbiVersion()`, `boundaryHeaderIsCanonicalSize()`, `boundaryHeaderIsCompatibleSize()`, `canonicalizeBoundaryHeader()`, `validateBoundaryHeaderStatus()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, and `validateDevTComponentsStatus()`, so restating the survey as if it only covered the older narrower helper set would undercount the live shared binding surface on `master`.

The remaining wider same-family work is no longer the header-family binding relay itself. Keep any broader shared replay, docs-root reminder, or later export/UAPI follow-through on their own bounded lanes instead of implying that the already-landed header-family relay is still missing.
