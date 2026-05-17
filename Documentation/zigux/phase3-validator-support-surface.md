# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface for the directly readable packet under review.

The current packet carries one bounded `dev_t` starter packet with paired `dev_t` and version bindings plus a directly readable export shim companion, two focused helper-local interop slices (`err_ptr` / `xarray` value-tag interop and `xarray slot` classification), and one focused helper-local policy slice. It does not currently ship the broader validator, export/UAPI layout, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.

## Current starter packet present

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

## Focused helper interop slices present

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
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/phase3_xarray_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `scripts/zigux/check-phase3-xarray-slot.py`
- `python3 scripts/zigux/check-phase3-xarray-slot.py --self-test`
- `python3 scripts/zigux/check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig`

## Focused policy slice present

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

Keep the shared Phase 3 reminder packet anchored to those four current-tree-backed slices until additional validator, broader export/UAPI layout, or shared replay proof lands.

Do not treat the current starter packet, its manifest-backed replay guards, its direct Zig compile replays, its starter export shim companion, its helper-local fixture-backed parity packets, plus the focused policy slice as evidence that the broader Phase 3 ABI substrate, export/UAPI layout packet, catalog wiring, IDR/IDA family, or shared replay routes already ship.

## Sampled broader gaps still absent

The following representative Phase 3 routes should still be treated as repo-reality gaps rather than shipped validator support:

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

If this packet lands, `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` will need one narrow truthfulness pass so they describe the bounded four-slice Phase 3 posture already recorded in `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.

Keep that follow-up focused on those three shared reminder surfaces so they stop describing only the older three-slice posture, and keep any separate scripts-root inventory work outside this validator-support note.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet, the machine-readable manifests, the direct compile replays, the starter export shim companion, the focused helper slices, and the focused policy slice explicit, marks representative broader validator and export-boundary routes as current gaps, and records the next narrow shared-reminder follow-up without claiming a wider shipped Phase 3 packet.
