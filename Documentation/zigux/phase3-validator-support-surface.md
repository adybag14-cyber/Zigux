# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on live `master`.

Current `master` now carries one bounded `dev_t` starter packet with paired `dev_t` and version bindings plus a directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` interop slice with both starter-packet and fixture-backed parity coverage, one focused helper-local policy slice with a reusable layout guard and bounded narrow-surface cross-check, and one adjacent export/UAPI layout replay pair. It does not currently ship the broader export/UAPI survey, catalog, or shared Phase 3 replay packet that older reminder surfaces still name, even though the shared `scripts/zigux/validate-phase3.py` validator entrypoint and `scripts/zigux/check-phase3-abi.py` shared ABI checker are directly readable on current `master`.

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
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`

## Adjacent export/UAPI layout replay present on `master`

- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`

## Review boundary

Keep the shared Phase 3 reminder packet anchored to those three current-tree-backed slices until additional broader export/UAPI survey or shared replay proof lands.

Do not treat the current starter packet, its manifest-backed replay guard, its direct Zig compile replay, its starter export shim companion, its helper-local fixture-backed parity packet, the focused policy slice, the directly readable shared validator entrypoint, or the adjacent export/UAPI layout replay pair as evidence that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes already ship on `master`.

## Sampled broader gaps still absent on `master`

The following representative Phase 3 routes still read as absent on the live tree and should be treated as repo-reality gaps rather than shipped validator support:

- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/phase3_catalog.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py` together with the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, but those two shared validation surfaces should not be used here to imply that the broader validator-support, export/UAPI survey, catalog, or shared replay packet has returned.

Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.

## Shared reminder follow-up

`Documentation/zigux/README.md` now reflects that bounded three-slice posture together with the returned notifier binding companion and adjacent export/UAPI layout replay, and should stay aligned with `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and this note.

`zigux/tests/README.md` now aligns with that bounded starter, notifier-binding, focused export/UAPI layout replay, and low-level-wrapper reminder packet, so shared-summary follow-through can stay separate from this validator-support note unless a fresh reread finds new same-packet drift on current `master`.

`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root shared reminder packet while keeping scripts-root inventory follow-through separate.

`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.

Keep any remaining follow-up focused on separate scripts-root inventory drift or a fresh shared-summary reread only if that broader surface changes again. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet, the machine-readable manifests, the direct compile replay, the starter export shim companion, the helper-local fixture-backed parity packet, the focused policy slice, the separately readable shared validator entrypoint and shared ABI checker, and the adjacent export/UAPI layout replay pair explicit; marks representative broader export-boundary survey, catalog, and shared replay routes as current gaps; records the separately landed low-level-wrapper packet without promoting it into broader validator support; and records the shared docs-root and tests-root reminders as aligned while keeping scripts-root follow-through separate. This note does not claim that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.