# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on this branch relative to live `master`.

Live `master` still carries one bounded `dev_t` starter packet with paired `dev_t` and version bindings plus a directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` interop slice with both starter-packet and fixture-backed parity coverage, and one focused helper-local policy slice. This branch adds one focused helper-local bitmap/cpumask starter packet without widening into the broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.

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
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all`

## Focused helper slice present on live `master`

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
- `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- `zig build phase3-bitmap-cpumask-starter-packet-test --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

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
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`

## Review boundary

Keep the shared Phase 3 reminder packet anchored to those four bounded slices until additional validator, broader export/UAPI layout, or shared replay proof lands.

Do not treat the current `dev_t` starter packet, its manifest-backed replay guard, its direct Zig compile replay, the helper-local fixture-backed `err_ptr` / `xarray` parity packet, this bitmap/cpumask starter packet, plus the focused policy slice as evidence that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes already ship on live `master`.

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

`Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still describe the narrower current-`master` three-slice posture and therefore need a separate same-lane wording refresh before this branch can claim a four-slice shared reminder packet.

`Documentation/zigux/phase3-shared-reminder-gap.md` remains the direct-readback record for the current three-slice shared reminder state on live `master` and should stay separate from this branch-local starter-packet restack.

`scripts/zigux/README.md` remains parked on the older scripts-root absent-route wording around the broader inventory, so keep that shared scripts-root reminder follow-up separate from this validator-support note and refresh it only inside the scripts-root inventory lane.

Keep any remaining follow-up focused on either the docs-root/tests-root/review-checklist wording repair, the fixture-backed bitmap/cpumask parity packet, or the separate scripts-root inventory truthfulness packet if one of those broader surfaces drifts again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.

## Scope

This note is limited to the current validator-support posture for Phase 3 on this branch. It keeps the directly readable starter packet, the machine-readable manifests, the direct compile replay, the starter export shim companion, the helper-local fixture-backed `err_ptr` / `xarray` parity packet, the branch-local bitmap/cpumask starter packet, and the focused policy slice explicit, marks representative broader validator and export-boundary routes as current gaps, and leaves the shared reminder plus fixture-backed bitmap/cpumask follow-through explicit without claiming a wider shipped Phase 3 packet.