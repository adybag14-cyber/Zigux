# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export shim, curated binding, and starter UAPI boundary evidence that still lives inside the bounded Phase 3 ABI substrate packet on live `master`.

## Status

- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test`
- `PHASE3_EXPORT_UAPI_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_KERNEL_EXPORT_SHIM_GOVERNANCE_NOTE=Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `PHASE3_ABI_H_BOUNDARY_NOTE=Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `PHASE3_ABI_H_PATH=include/zigux/abi.h`
- `PHASE3_BINDING_VERSION_PATH=zigux/bindings/version.zig`
- `PHASE3_BINDING_DEV_T_PATH=zigux/bindings/dev_t.zig`
- `PHASE3_BINDING_HEADER_FAMILY_PATH=zigux/bindings/header_family.zig`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_DEV_T_STARTER_PACKET_MANIFEST=zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `PHASE3_DEV_T_STARTER_PACKET_CHECK=scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `PHASE3_DEV_T_STARTER_PACKET_RUN=python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_ZIGUX_H_GOVERNANCE_NOTE=Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_SHARED_TESTS_BUILD_PATH=zigux/tests/build.zig`
- `PHASE3_SHARED_VALIDATE_SELFTEST_PATH=scripts/zigux/validate_phase3_selftest.py`
- `PHASE3_SHARED_CHECK_RUNNER_PATH=scripts/zigux/run-phase3-checks.py`
- `PHASE3_SHARED_VALIDATE_MAKE_ROUTE=make -C zigux phase3-validate`
- `PHASE3_SHARED_PHASE_MAKE_ROUTE=make -C zigux phase3`
- `PHASE3_EXPORT_SHIM_BUILD_PATH=zigux/tests/phase3_export_shim_build.zig`
- `PHASE3_EXPORT_SHIM_DEDICATED_GATE=zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig`
- `PHASE3_EXPORT_SHIM_DEDICATED_MAKE_ROUTE=make -C zigux phase3-export-shim-test`
- `PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_LAYOUT_SHARED_GATE=zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_DEDICATED_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_LAYOUT_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout`
- `PHASE3_LAYOUT_DEDICATED_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout-test`
- `PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c`
- `PHASE3_C_HEADER_SMOKE_CHECK=scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_C_HEADER_SMOKE_SELF_TEST=python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test`
- `PHASE3_C_HEADER_SMOKE_GATE=python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py`
- `PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py`

## Live Boundary

The packet-local validator, focused export-shim replay handoff, dedicated layout-build handoff, dedicated dev_t starter manifest-plus-checker pair, returned shared `include/zigux/abi.h` boundary header plus adjacent `abi.h` boundary note, aggregate `phase3-validate` and `phase3` make routes, and catalog-selftest guard are now present and should stay aligned with this survey rather than being tracked as missing companions or blocked follow-through.

On current `master`, this packet stays narrow and explicit:

- `zigux/kernel/export_shim.zig` keeps the export boundary reviewable through `canonicalHeader`, `headerIsCanonical`, `headerIsCompatible`, `requestedExtraBytes`, `validateBoundaryHeader`, `versionMatchesCurrent`, `validateVersion`, and the status-tagged `validateDeviceFields` plus `validateDeviceNumber` relays.
- That same starter export surface also now carries the status-tagged `validateDeviceRange` relay plus the bounded `encodeDeviceNumber` and `decodeDeviceNumber` bridge without widening into broader UAPI growth.
- `Documentation/zigux/phase3-kernel-export-shim-governance.md` keeps the kernel-facing ownership note for the live `export_shim` relay families explicit, so review does not have to infer that owner map from the broader ABI slice or shared reminder packet alone.
- `include/zigux/abi.h` remains the shared C-facing ABI header path that this starter export/UAPI packet still reads through for boundary-header helpers, facility-tagged export-status relays, and the paired `Documentation/zigux/phase3-abi-h-boundary-next-step.md` owner note without turning this survey into the broader shared ABI lane.
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md` keeps the adjacent shared `include/zigux/abi.h` owner note explicit beside this export/UAPI survey, so the starter export shim and starter UAPI packet do not imply the shared ABI header is untracked.
- `zigux/bindings/version.zig` and `zigux/bindings/dev_t.zig` keep the curated Zig-facing binding side of the same starter boundary explicit through current-version compatibility checks, status-tagged version validation, layout parity, `dev_t` packing helpers, and range validation that mirror the shipped UAPI packet without widening it.
- `zigux/bindings/header_family.zig` keeps the starter header-family relay companion explicit as the narrow binding surface that ties the current version helpers, boundary-header predicates, and `dev_t` status wrappers together without inventing a second export surface.
- `zigux/uapi/version.zig` keeps the starter boundary-header contract explicit through the current ABI version fields, `matchesCurrent`, and the status-tagged `validate()` compatibility gate that mirrors `include/linux/zigux.h`.
- `zigux/uapi/dev_t.zig` keeps the bounded chrdev validation and range checks readable beside the shared `include/zigux/dev_t.h` contract.
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json` and `scripts/zigux/check-phase3-dev-t-starter-packet.py` keep the same starter `version.zig` plus `dev_t.zig` packet fail-closed through manifest-backed inventory, packet-local marker checks, the dedicated `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test` route, and the direct `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py` replay.
- `include/linux/zigux.h` keeps the C-facing boundary helpers aligned with the shared ABI header, the curated binding companions, and the starter `dev_t` packet, including `zigux_uapi_boundary_header_*()` relays, the status-tagged `zigux_uapi_validate_boundary_header()` gate, the Linux-facing `zigux_boundary_header_*()` compatibility aliases, and the relay `zigux_validate_boundary_header()` as thin wrappers instead of a second ownership root.
- `zigux/tests/phase3_export_shim_build.zig` now carries the focused `phase3-export-shim-test` replay handoff, so the export-shim starter packet is directly runnable through `zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig` and `make -C zigux phase3-export-shim-test`.
- `zigux/tests/phase3_export_uapi_layout.zig` stays wired through the shared tests-root route in `zigux/tests/build.zig`, where `addPhase3ExportUapiLayout(...)` imports `header_family_binding`, `uapi_dev_t`, `uapi_version`, `dev_t_binding`, `version_binding`, `export_shim`, and the shared ABI-backed surface they compare, so the layout, version, boundary-header, device-number, and header-family relays remain reviewable through `zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`.
- `zigux/tests/phase3_export_uapi_layout_build.zig` now carries the dedicated `phase3-export-uapi-layout-test` replay handoff, so the same starter layout packet is directly runnable through `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig` and `make -C zigux phase3-export-uapi-layout-test`.
- `zigux/tests/phase3_export_uapi_c_header_smoke.c` together with `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` keeps the named C-facing boundary-header helpers, the exported boundary-header validation relay, the version relay, and the starter `dev_t` validation wrappers directly compile- and run-proofed through both `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test` and `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`.
- `zigux/Makefile` now keeps `phase3-validate` wired to `python3 scripts/zigux/validate_phase3_selftest.py` plus `python3 scripts/zigux/run-phase3-checks.py`, and keeps `phase3` wired to that aggregate validation route plus the dedicated export/UAPI, low-level-wrapper, test, policy-dump, and dump replays, so this packet stays reachable through the same shared Phase 3 entrypoints the roadmap expects for bounded validation before wider expansion.

Current `master` now directly serves `scripts/zigux/phase3_catalog.py` as the bounded Phase 3 catalog helper, `scripts/zigux/check-phase3-catalog-selftest.py` as the dedicated guard that keeps the catalog helper's export/UAPI self-test markers fail-closed, `zigux/tests/fixtures/phase3_abi_manifest.json` as the shared manifest-backed inventory companion, `zigux/tests/phase3_dev_t_starter_packet_manifest.json` as the starter-packet inventory companion, `scripts/zigux/check-phase3-dev-t-starter-packet.py` as the starter-packet checker, `scripts/zigux/validate_phase3_selftest.py` plus `scripts/zigux/run-phase3-checks.py` as the aggregate shared validation route behind `make -C zigux phase3-validate`, `Documentation/zigux/phase3-linux-zigux-header-governance.md` as the returned Linux-header ownership note for this packet, and `include/zigux/abi.h` as the shared ABI header path that this survey still has to name truthfully when it describes the current boundary.

## Next Safe Step

Keep this lane parked on the same bounded starter packet.

Current `master` now carries `zigux/tests/phase3_dev_t_starter_packet_manifest.json`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `zigux/tests/phase3_export_shim_build.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `include/zigux/abi.h`, the `phase3-export-shim-test`, `phase3-export-uapi-layout`, and `phase3-export-uapi-layout-test` make routes in `zigux/Makefile`, the direct C smoke replay plus its dedicated self-test route, the kernel-facing governance note, the adjacent `abi.h` boundary note, the shared manifest-backed inventory companion, the aggregate `phase3-validate` and `phase3` make routes, and the dedicated catalog-selftest guard beside the shared tests-root replay. There is no remaining packet-local missing companion, missing focused export-shim replay handoff, missing dedicated layout-build handoff, or missing aggregate replay entrypoint left to close inside this survey.

Reopen this lane only if this survey, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `include/zigux/abi.h`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/tests/phase3_dev_t_starter_packet_manifest.json`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `zigux/tests/phase3_export_shim_build.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/Makefile`, `scripts/zigux/validate_phase3_selftest.py`, `scripts/zigux/run-phase3-checks.py`, or `scripts/zigux/check-phase3-catalog-selftest.py` drifts again around those same-family paths.

## Scope

This survey stays packet-local to the shipped starter export shim, its dedicated governance note at `Documentation/zigux/phase3-kernel-export-shim-governance.md`, the adjacent shared ABI header note at `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, the shared `include/zigux/abi.h` boundary header path, the curated `zigux/bindings/version.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/header_family.zig` companions, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the focused `zigux/tests/phase3_export_shim_build.zig` replay handoff, the focused `zigux/tests/phase3_export_uapi_layout.zig` replay plus the dedicated `zigux/tests/phase3_export_uapi_layout_build.zig` handoff, the direct `zigux/tests/phase3_export_uapi_c_header_smoke.c` plus `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` C smoke route, the dedicated `zigux/tests/phase3_dev_t_starter_packet_manifest.json` inventory companion plus `scripts/zigux/check-phase3-dev-t-starter-packet.py` checker, the shared tests-root route in `zigux/tests/build.zig`, the `phase3-export-shim-test`, `phase3-export-uapi-layout`, and `phase3-export-uapi-layout-test` make routes in `zigux/Makefile`, the aggregate shared validation route in `scripts/zigux/validate_phase3_selftest.py`, `scripts/zigux/run-phase3-checks.py`, `make -C zigux phase3-validate`, and `make -C zigux phase3`, the bounded catalog helper at `scripts/zigux/phase3_catalog.py`, the dedicated catalog-selftest guard at `scripts/zigux/check-phase3-catalog-selftest.py`, the shared manifest-backed inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, the returned Linux-header governance note at `Documentation/zigux/phase3-linux-zigux-header-governance.md`, and the packet-local validator at `scripts/zigux/validate-phase3-export-uapi-survey.py`.

It does not claim a larger UAPI family than the current starter packet actually ships.
