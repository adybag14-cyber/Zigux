# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on live `master`.

Current `master` now carries one bounded `dev_t` starter packet with paired `dev_t` and version bindings plus a directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` interop slice with both starter-packet and fixture-backed parity coverage, and one focused helper-local policy slice. It does not currently ship the broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.

## Current starter packet present on `master`

- `Documentation/zigux/phase3-abi-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all`

## Focused helper slice present on `master`

- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/phase3_errptr_xarray_dump_build.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray.py`
- `python3 scripts/zigux/check-phase3-errptr-xarray.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig`

## Focused policy slice present on `master`

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`

## Review boundary

Keep the shared Phase 3 reminder packet anchored to those three current-tree-backed slices until additional validator, broader export/UAPI layout, or shared replay proof lands.

Do not treat the current starter packet, its manifest-backed replay guard, its direct Zig compile replay, its starter export shim companion, its helper-local fixture-backed parity packet, plus the focused policy slice as evidence that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes already ship on `master`.

## Sampled broader gaps still absent on `master`

The following representative Phase 3 routes still read as absent on the live tree and should be treated as repo-reality gaps rather than shipped validator support:

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Shared reminder follow-up

`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now all reflect that bounded three-slice posture and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.

`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the earlier shared-reminder sentence drift is closed on current `master`.

`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.

Keep any remaining follow-up focused on separate scripts-root inventory drift if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet, the machine-readable manifests, the direct compile replay, the starter export shim companion, the helper-local fixture-backed parity packet, and the focused policy slice explicit, marks representative broader validator and export-boundary routes as current gaps, records the now-aligned docs-root, checklist, and tests-root reminder surfaces, and keeps scripts-root follow-through separate. This note does not claim that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.
