# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on the Lane 27 branch relative to live `master`.

Live `master` still carries one bounded `dev_t` starter packet, one focused helper-local `err_ptr` / `xarray` interop slice, and one focused helper-local policy slice. This branch adds one focused helper-local bitmap/cpumask interop slice with both starter-packet and fixture-backed parity coverage. It does not currently ship the broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.

## Current starter packet present on live `master`

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

## Focused helper slice present on live `master`

- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/phase3_errptr_xarray_dump_build.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray.py`

## Focused bitmap/cpumask slice present on this branch

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `include/zigux/bitmap_cpumask.h`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`

## Focused policy slice present on live `master`

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

## Review boundary

Keep the shared Phase 3 reminder packet anchored to those four bounded slices until additional validator, export-boundary, or shared replay proof lands.

Do not treat the current `dev_t` starter packet, its manifest-backed replay guard, its direct Zig compile replay, the helper-local fixture-backed parity packets for `err_ptr` / `xarray` and bitmap/cpumask, plus the focused policy slice as evidence that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes already ship on live `master`.

## Sampled broader gaps still absent on live `master`

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
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Shared reminder follow-up

`Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` should keep the same bounded four-slice reminder wording that the dedicated slice notes and this validator-support note now carry on this branch.

Keep any remaining follow-up focused on shared reminder or scripts-root inventory truthfulness if one of those broader surfaces drifts again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.

## Scope

This note is limited to the validator-support posture for the bounded starter packet and helper-local slices above. It keeps the directly readable starter packet, the machine-readable manifests, the direct compile replay, the two helper-local fixture-backed parity packets, and the focused policy slice explicit, marks representative broader validator and export-boundary routes as current gaps, and records the remaining shared-reminder follow-up without claiming a wider shipped Phase 3 packet.
