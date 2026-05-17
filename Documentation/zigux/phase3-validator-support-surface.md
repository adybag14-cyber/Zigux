# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on live `master`.

Current `master` now carries one bounded `dev_t` starter packet and its directly readable header-family companions. It does not currently ship the broader validator, export/UAPI layout, low-level-wrapper, catalog, or shared Phase 3 replay packet that older reminder surfaces still name.

## Current starter packet present on `master`

- `Documentation/zigux/phase3-abi-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`

## Review boundary

Keep the shared Phase 3 reminder packet anchored to that starter header-family and `dev_t` binding slice until additional current-tree-backed validator or export-boundary proof lands.

Do not treat the current starter packet as evidence that the broader Phase 3 ABI substrate, export/UAPI layout packet, low-level-wrapper packet, catalog wiring, or shared replay routes already ship on `master`.

## Sampled broader gaps still absent on `master`

The following representative Phase 3 routes still read as absent on the live tree and should be treated as repo-reality gaps rather than shipped validator support:

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/kernel/export_shim.zig`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Shared reminder follow-up

`Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still carry broader shared Phase 3 reminder language than the directly readable starter packet on current `master`.

Keep the remaining shared reminder follow-up focused on narrowing those broad reminder surfaces so they stay anchored to `Documentation/zigux/phase3-abi-slice.md`, this note, and the `dev_t` starter replay route until additional current-tree-backed validator or export-boundary proof lands.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet explicit, marks representative broader validator and export-boundary routes as current gaps, and records the remaining shared-reminder follow-up without claiming a wider shipped Phase 3 packet.