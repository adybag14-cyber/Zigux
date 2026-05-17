# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on live `master`.

Current `master` now carries one bounded `dev_t` starter packet, two focused helper-local interop slices, and one focused helper-local policy slice. It does not currently ship the broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.

## Current starter packet present on `master`

- `Documentation/zigux/phase3-abi-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`

## Focused helper interop slices present on `master`

- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `Documentation/zigux/phase3-list-hlist-slice.md`
- `include/zigux/list_hlist.h`
- `zigux/uapi/list_hlist.zig`
- `zigux/bindings/list_hlist.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/tests/phase3_list_hlist_starter_packet.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_manifest.json`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `scripts/zigux/check-phase3-list-hlist.py`
- `python3 scripts/zigux/check-phase3-list-hlist.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist.py`

## Focused policy slice present on `master`

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`

## Review boundary

Keep the shared Phase 3 reminder packet anchored to those four current-tree-backed slices until additional validator, export-boundary, or shared replay proof lands.

Do not treat the current starter packet, its manifest-backed replay guards, the two focused helper interop slices, plus the focused policy slice as evidence that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes already ship on `master`.

## Sampled broader gaps still absent on `master`

The following representative Phase 3 routes still read as absent on the live tree and should be treated as repo-reality gaps rather than shipped validator support:

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/kernel/export_shim.zig`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Shared reminder follow-up

`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still carry broader shared Phase 3 reminder language than the directly readable slices on current `master`.

Keep the remaining shared reminder follow-up focused on narrowing those broader shared surfaces so they stay anchored to `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-list-hlist-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, this note, the manifest-backed starter packets, and the dedicated replay routes until additional current-tree-backed validator or export-boundary proof lands.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet, the focused helper interop slices, the focused policy slice, and their machine-readable manifests explicit, marks representative broader validator and export-boundary routes as current gaps, and records the remaining shared-reminder follow-up without claiming a wider shipped Phase 3 packet.