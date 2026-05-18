# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on live `master`.

Current `master` now carries one bounded `dev_t` starter packet with paired bindings and export-shim companions, one focused helper-local `err_ptr` / `xarray` interop slice with starter-plus-dump coverage, one bounded `xarray_slot` helper-local slice with shared starter and dump routes, one focused policy slice with the current narrow-unsafe companion, and one adjacent low-level-wrapper reminder packet. It does not currently ship the broader catalog, export/UAPI survey, IDR, IDA, or all-up Phase 3 completion packet that older reminder surfaces still imply.

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

## Focused helper slices present on `master`

- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/phase3_errptr_xarray_dump_build.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `scripts/zigux/check-phase3-errptr-xarray.py`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/phase3_xarray_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `scripts/zigux/check-phase3-xarray-slot.py`
- `zigux/tests/build.zig`
- `zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig`
- `zig build phase3-xarray-slot-dump --build-file zigux/tests/build.zig`

## Focused policy and wrapper packet present on `master`

- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

## Review boundary

Keep the shared Phase 3 validator posture anchored to those bounded starter, helper, xarray-slot, policy, and wrapper surfaces until broader validator or survey proof lands.

Do not treat the current starter packet, the `err_ptr` / `xarray` dump packet, the xarray-slot starter-plus-dump packet, the low-level-wrapper reminder packet, or the narrow-unsafe companion as evidence that the broader Phase 3 catalog, export/UAPI survey stack, IDR family, IDA family, or all-up validation routes already ship on `master`.

## Shared reminder follow-up

`Documentation/zigux/phase3-shared-reminder-gap.md` now records that the remaining shared reminder drift is the xarray-slot undercount in `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md`.

`scripts/zigux/README.md` remains a separate scripts-root inventory surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.

Keep any next same-lane follow-up focused on those shared reminder surfaces rather than reopening the landed helper-local or fixture-backed xarray-slot packet.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet, the helper-local `err_ptr` / `xarray` slice, the xarray-slot helper-local slice and its shared starter-plus-dump routes, the focused policy slice, and the adjacent low-level-wrapper packet explicit. It does not claim that the broader Phase 3 catalog, export/UAPI survey family, IDR family, IDA family, or all-up validation routes have returned.
