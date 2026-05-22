# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim, curated binding, and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test`
- `PHASE3_EXPORT_UAPI_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE=Documentation/zigux/phase3-kernel-export-shim-governance.md`
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
- `PHASE3_LAYOUT_SHARED_GATE=zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_DEDICATED_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout`
- `PHASE3_LAYOUT_DEDICATED_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout-test`
- `PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c`
- `PHASE3_C_HEADER_SMOKE_CHECK=scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_C_HEADER_SMOKE_GATE=python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py`
- `PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py`

## Live Boundary

The packet-local validator, dedicated layout-build handoff, and catalog-selftest guard are now present and should stay aligned with this survey rather than being tracked as missing companions or blocked follow-through.

On current `master`, this packet stays narrow and explicit:

- `zigux/kernel/export_shim.zig` keeps the export boundary reviewable through `canonicalHeader`, `headerIsCanonical`, `headerIsCompatible`, `requestedExtraBytes`, `validateBoundaryHeader`, `versionMatchesCurrent`, `validateVersion`, and the status-tagged `validateDeviceFields` plus `validateDeviceNumber` relays.
- That same starter export surface also now carries the status-tagged `validateDeviceRange` relay plus the bounded `encodeDeviceNumber` and `decodeDeviceNumber` bridge without widening into broader UAPI growth.
- `Documentation/zigux/phase3-kernel-export-shim-governance.md` keeps the kernel-facing ownership note for the live `export_shim` relay families explicit, so review does not have to infer that owner map from the broader ABI slice or shared reminder packet alone.
- `zigux/bindings/version.zig` and `zigux/bindings/dev_t.zig` keep the curated Zig-facing binding side of the same starter boundary explicit through current-version compatibility checks, status-tagged version validation, layout parity, `dev_t` packing helpers, and range validation that mirror the shipped UAPI packet without widening it.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through the current ABI version fields, `matchesCurrent`, and the status-tagged `validate()` compatibility gate that mirrors `include/linux/zigux.h`.
- `zigux/uapi/dev_t.zig` keeps the bounded chrdev validation and range checks readable beside the shared `include/zigux/dev_t.h` contract.
- `include/linux/zigux.h` keeps the C-facing boundary helpers aligned with the shared ABI header, the curated binding companions, and the starter `dev_t` packet, including `zigux_uapi_boundary_header_*()` relays, the status-tagged `zigux_uapi_validate_boundary_header()` gate, the Linux-facing `zigux_boundary_header_*()` compatibility aliases, and the relay `zigux_validate_boundary_header()` as thin wrappers instead of a second ownership root.
- `zigux/tests/phase3_export_uapi_layout.zig` stays wired through the shared tests-root route in `zigux/tests/build.zig`, where `addPhase3ExportUapiLayout(...)` imports `header_family_binding`, `uapi_dev_t`, `uapi_version`, `dev_t_binding`, `version_binding`, and `export_shim`, so the layout, version, boundary-header, device-number, and header-family relays remain reviewable through `zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`.
- `zigux/tests/phase3_export_uapi_layout_build.zig` now carries the dedicated `phase3-export-uapi-layout-test` replay handoff, so the same starter layout packet is directly runnable through `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` and `make -C zigux phase3-export-uapi-layout-test`.
- `zigux/tests/phase3_export_uapi_c_header_smoke.c` together with `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` keeps the named C-facing boundary-header helpers, the exported boundary-header validation relay, the version relay, and the starter `dev_t` validation wrappers directly compile- and run-proofed through `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`.

Current `master` now directly serves `scripts/zigux/phase3_catalog.py` as the bounded Phase 3 catalog helper, `zigux/tests/fixtures/phase3_abi_manifest.json` as the same-family manifest-backed inventory companion, `Documentation/zigux/phase3-linux-zigux-header-governance.md` as the returned Linux-header ownership note for this packet, and `scripts/zigux/check-phase3-catalog-selftest.py` as the dedicated guard that keeps the catalog helper's export/UAPI self-test markers fail-closed.

## Next Safe Step

Keep this lane parked on the same bounded starter packet.

Current `master` now carries `zigux/tests/phase3_export_uapi_layout_build.zig`, the `phase3-export-uapi-layout-test` make route in `zigux/Makefile`, the direct C smoke replay, the kernel-facing governance note, the manifest-backed inventory companion, and the dedicated catalog-selftest guard beside the shared tests-root replay. There is no remaining packet-local missing companion or missing dedicated layout-build handoff left to close inside this survey.

Reopen this lane only if this survey, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/Makefile`, or `scripts/zigux/check-phase3-catalog-selftest.py` drifts again around those same-family paths.

## Scope

This survey stays packet-local to the shipped starter export shim, its dedicated governance note at `Documentation/zigux/phase3-kernel-export-shim-governance.md`, the curated `zigux/bindings/version.zig` and `zigux/bindings/dev_t.zig` companions, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused `zigux/tests/phase3_export_uapi_layout.zig` replay plus the dedicated `zigux/tests/phase3_export_uapi_layout_build.zig` handoff, the direct `zigux/tests/phase3_export_uapi_c_header_smoke.c` plus `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` C smoke route, the shared tests-root route in `zigux/tests/build.zig`, the `phase3-export-uapi-layout` and `phase3-export-uapi-layout-test` make routes in `zigux/Makefile`, the shared Phase 3 validator runner at `scripts/zigux/run-phase3-checks.py`, the bounded catalog helper at `scripts/zigux/phase3_catalog.py`, the dedicated catalog-selftest guard at `scripts/zigux/check-phase3-catalog-selftest.py`, the shared manifest-backed inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, the returned Linux-header governance note at `Documentation/zigux/phase3-linux-zigux-header-governance.md`, and the packet-local validator at `scripts/zigux/validate-phase3-export-uapi-survey.py`.

It does not claim a larger UAPI family than the current starter packet actually ships.
