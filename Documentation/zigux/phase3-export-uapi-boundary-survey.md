# Phase 3 Export Shim and UAPI Boundary Survey

This survey records the current Phase 3 export-shim and starter UAPI boundary against the roadmap's ABI and interop substrate goals.

## Status Markers

- `PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test`
- `PHASE3_EXPORT_UAPI_VALIDATOR_RUN=python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_INTEROP_POLICY_RELAY=zigux/kernel/export_shim.zig -> validateInteropPolicy`
- `PHASE3_EXPORT_SHIM_RBTREE_RELAY=zigux/kernel/export_shim.zig -> validateRbtreeRootView`
- `PHASE3_ABI_H_PATH=include/zigux/abi.h`
- `PHASE3_ABI_H_BOUNDARY_NOTE=Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_LINUX_ZIGUX_H_GOVERNANCE_NOTE=Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `PHASE3_BINDING_VERSION_PATH=zigux/bindings/version.zig`
- `PHASE3_BINDING_DEV_T_PATH=zigux/bindings/dev_t.zig`
- `PHASE3_BINDING_HEADER_FAMILY_PATH=zigux/bindings/header_family.zig`
- `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
- `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
- `PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h`
- `PHASE3_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_EXPORT_SHIM_BUILD_PATH=zigux/tests/phase3_export_shim_build.zig`
- `PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig`
- `PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c`
- `PHASE3_C_HEADER_SMOKE_WORKFLOW_ROUTE=.github/workflows/zigux-bootstrap.yml`
- `PHASE3_DEV_T_STARTER_PACKET_CHECK=scripts/zigux/check-phase3-dev-t-starter-packet.py`

## Roadmap Alignment

Phase 3 calls for the permanent C/Zigux boundary: explicit export shims, curated bindings, layout assertions, explicit policy surfaces, and a narrow unsafe boundary. Within this lane, current `master` has the starter export/UAPI packet in place rather than a broader Phase 3 completion claim.

The landed boundary is still narrow and reviewable:

- `zigux/kernel/export_shim.zig` exposes boundary-header, version, and `dev_t` validation relays plus focused interop-policy and rbtree-root status helpers instead of widening into a larger runtime surface.
- `include/zigux/abi.h` and `include/linux/zigux.h` hold the public C-facing header contract and the Linux-facing UAPI aliases for the same starter packet.
- `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/header_family.zig` provide the curated Zig-side view of that same boundary.
- `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/tests/phase3_export_shim_build.zig`, and `zigux/tests/phase3_export_uapi_c_header_smoke.c` keep the packet replayable from both Zig and C-facing entry points, while `.github/workflows/zigux-bootstrap.yml` now runs the direct C smoke route as its own Phase 3 bootstrap step.

## Current Boundary Gap

The remaining gap in this lane is not a missing starter packet. The current gap is that the export/UAPI boundary is still limited to the starter header-family, version, and `dev_t` UAPI packet plus focused interop-policy and rbtree-root status relays.

Current `master` does not yet turn this lane into:

- a broader generated-or-curated UAPI family beyond the shipped starter packet
- a wider export-shim surface beyond the landed boundary-header, version, `dev_t`, interop-policy, and rbtree-root relays
- full Phase 3 closure for policy, low-level wrapper, or other interop slices that live on adjacent lanes

`PHASE3_EXPORT_UAPI_GAP=broader curated UAPI families and wider export-shim coverage beyond the landed starter packet and focused runtime relays remain open`

## Verification Routes

- `PHASE3_EXPORT_SHIM_DEDICATED_GATE=zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig`
- `PHASE3_LAYOUT_SHARED_GATE=zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`
- `PHASE3_LAYOUT_DEDICATED_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_C_HEADER_SMOKE_GATE=python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `PHASE3_C_HEADER_SMOKE_WORKFLOW_GATE=.github/workflows/zigux-bootstrap.yml -> Run current Phase 3 export/UAPI C header smoke`
- `PHASE3_SHARED_VALIDATE_SELFTEST_PATH=scripts/zigux/validate_phase3_selftest.py`
- `PHASE3_SHARED_CHECK_RUNNER_PATH=scripts/zigux/run-phase3-checks.py`
- `PHASE3_SHARED_VALIDATE_MAKE_ROUTE=make -C zigux phase3-validate`
- `PHASE3_SHARED_PHASE_MAKE_ROUTE=make -C zigux phase3`

## Next Safe Step

Keep this lane bounded to export-shim and starter UAPI truthfulness. Reopen it only when one of these drifts:

- the survey or validator
- the starter export/UAPI headers or bindings
- the focused export-shim, layout, or C-smoke replay routes

Do not use this lane to claim broader Phase 3 completion.
