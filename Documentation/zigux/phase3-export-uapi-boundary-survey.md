# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim, curated binding, and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test`
- `PHASE3_EXPORT_UAPI_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_BINDING_VERSION_PATH=zigux/bindings/version.zig`
- `PHASE3_BINDING_DEV_T_PATH=zigux/bindings/dev_t.zig`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_ZIGUX_H_GOVERNANCE_NOTE=Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_SHARED_TESTS_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_CHECK_RUNNER_PATH=scripts/zigux/run-phase3-checks.py`
- `PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c`
- `PHASE3_C_HEADER_SMOKE_CHECK=scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_C_HEADER_SMOKE_GATE=python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py`
- `PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py`

## Live Boundary

The packet-local validator is now present and should stay aligned with this survey rather than being tracked as a missing companion.

On current `master`, this packet stays narrow and explicit:

- `zigux/kernel/export_shim.zig` keeps the export boundary reviewable through `canonicalHeader`, `headerIsCanonical`, `headerIsCompatible`, `requestedExtraBytes`, `validateBoundaryHeader`, `versionMatchesCurrent`, `validateVersion`, and the status-tagged `validateDeviceFields` plus `validateDeviceNumber` relays.
- That same starter export surface also now carries the status-tagged `validateDeviceRange` relay plus the bounded `encodeDeviceNumber` and `decodeDeviceNumber` bridge without widening into broader UAPI growth.
- `zigux/bindings/version.zig` and `zigux/bindings/dev_t.zig` keep the curated Zig-facing binding side of the same starter boundary explicit through current-version compatibility checks, status-tagged version validation, layout parity, `dev_t` packing helpers, and range validation that mirror the shipped UAPI packet without widening it.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through the current ABI version fields, `matchesCurrent`, and the status-tagged `validate()` compatibility gate that mirrors `include/linux/zigux.h`.
- `zigux/uapi/dev_t.zig` keeps the bounded chrdev validation and range checks readable beside the shared `include/zigux/dev_t.h` contract.
- `include/linux/zigux.h` keeps the C-facing boundary helpers aligned with the shared ABI header, the curated binding companions, and the starter `dev_t` packet, including `zigux_uapi_boundary_header_extends_boundary()`, `zigux_uapi_boundary_header_requested_extra_bytes()`, and `zigux_uapi_boundary_header_canonicalize()`, the status-tagged `zigux_uapi_validate_boundary_header()` gate, the Linux-facing `zigux_boundary_header_extends_boundary()`, `zigux_boundary_header_requested_extra_bytes()`, and `zigux_boundary_header_canonicalize()` compatibility aliases, the Linux-facing `zigux_uapi_validate_dev_t_fields()`, `zigux_uapi_validate_dev_t_components()`, and `zigux_uapi_validate_dev_t_range()` wrappers, and the relay `zigux_validate_boundary_header()` as thin wrappers instead of a second ownership root.
- `zigux/tests/phase3_export_uapi_layout.zig` together with `zigux/tests/phase3_export_uapi_layout_build.zig` keeps the `BoundaryHeader`, `ExportStatus`, starter version-compatibility relay, starter boundary-header validation relay, device-number bridge contract, and header-family relay visible on the direct replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.
- `zigux/tests/phase3_export_uapi_c_header_smoke.c` together with `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` now keeps the named C-facing boundary-header helpers, the exported boundary-header validation relay, the version relay, and the starter `dev_t` validation wrappers directly compile- and run-proofed through `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`.

Current `master` now directly serves `scripts/zigux/phase3_catalog.py` as the bounded Phase 3 catalog helper, `zigux/tests/fixtures/phase3_abi_manifest.json` as the same-family manifest-backed inventory companion, `Documentation/zigux/phase3-linux-zigux-header-governance.md` as the returned Linux-header ownership note for this packet, and `scripts/zigux/check-phase3-catalog-selftest.py` as the dedicated guard that keeps the catalog helper's export/UAPI self-test markers fail-closed.

## Current Gap

Current `master` no longer shows the older packet-local compile-wiring gap: the shared tests-root replay route in `zigux/tests/build.zig` now imports `header_family_binding` inside `addPhase3ExportUapiLayout(...)`, so the shared `phase3-export-uapi-layout` route and the dedicated `phase3-export-uapi-layout-test` route agree on the live starter packet wiring.

The dedicated replay route `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` remains the smallest focused compile gate for this packet, but it no longer stands in for missing shared-route wiring.

The packet now also keeps a direct C-facing smoke proof for the Linux-header relays, so the remaining gap here is no longer missing shared-route wiring, missing compile evidence for the named C boundary helpers, or missing proof that the exported boundary-header validation relay is callable from C.

The shared Phase 3 validator runner at `scripts/zigux/run-phase3-checks.py` keeps this dedicated export/UAPI survey replay inside the existing `phase3-validate` packet without needing to describe a still-blocked shared tests-root compile handoff.

Against the roadmap, the remaining gap here is still broader unfinished Phase 3 interop-substrate coverage outside this starter packet, not a missing export/UAPI companion, missing shared-route wiring, or missing starter boundary-header validation relay inside the packet itself.

This survey should keep the manifest-backed ABI inventory, the returned linux-header governance note, the returned catalog-selftest guard, the live curated binding companions, the already-shipped starter boundary-header validation relay, the already-shipped starter `dev_t` validation relays, the shared tests-root replay wiring, and the direct C smoke replay explicit as shipped same-family evidence so the roadmap's permanent boundary does not get understated as shim-plus-UAPI only.

## Scope

This survey stays packet-local to the shipped starter export shim, the curated `zigux/bindings/version.zig` and `zigux/bindings/dev_t.zig` companions, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig` replay pair, the direct `zigux/tests/phase3_export_uapi_c_header_smoke.c` plus `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` C smoke route, the shared tests-root route in `zigux/tests/build.zig`, the shared Phase 3 validator runner at `scripts/zigux/run-phase3-checks.py`, the bounded catalog helper at `scripts/zigux/phase3_catalog.py`, the dedicated catalog-selftest guard at `scripts/zigux/check-phase3-catalog-selftest.py`, the shared manifest-backed inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, the returned Linux-header governance note at `Documentation/zigux/phase3-linux-zigux-header-governance.md`, and the packet-local validator at `scripts/zigux/validate-phase3-export-uapi-survey.py`.

It does not claim a larger UAPI family or broader export/UAPI-only replay routes than the current starter packet actually ships.
