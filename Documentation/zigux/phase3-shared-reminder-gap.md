# Phase 3 Shared Reminder Gap

This note records the remaining shared-reminder drift for Phase 3 on live `master`.

Current `master` already narrows the validator-facing Phase 3 packet to the bounded starter header-family and `dev_t` slice recorded in `Documentation/zigux/phase3-abi-slice.md` and `Documentation/zigux/phase3-validator-support-surface.md`.

## Current starter packet to preserve

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `scripts/zigux/validate-phase3-validator-support-surface.py`

## Shared reminder surfaces still broader than current tree

- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`

Those shared reminder surfaces still describe a wider validator, export/UAPI layout, low-level-wrapper, catalog, or shared replay packet than the current starter packet proves on live `master`.

## Representative broader routes that still read as gaps

- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/kernel/export_shim.zig`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`

## Follow-up

Narrow the shared reminder surfaces above so they agree with the current starter packet and keep the broader Phase 3 routes framed as repo-reality gaps until fresh current-tree-backed evidence lands.

## Scope

This note is limited to the remaining shared-reminder truthfulness gap. It does not re-materialize the broader validator packet or replay the stale saved slug-sanity patch.