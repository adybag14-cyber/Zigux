# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the landed notifier binding companion plus one focused export-or-UAPI layout replay explicit in the dedicated ABI note, but the shared docs-root and tests-root Phase 3 summaries still undercount that returned surface, so the earlier shared-reminder sentence drift is not fully closed yet`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, zigux/tests/phase3_export_uapi_layout_build.zig, and scripts/zigux/check-phase3-dev-t-starter-packet.py; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; however Documentation/zigux/README.md and zigux/tests/README.md still describe the older narrower three-slice reminder packet and still list zigux/bindings/notifier_abi.zig plus the focused export/UAPI layout replay as broader gaps instead of returned current-master evidence`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=refresh only the shared Phase 3 summaries in Documentation/zigux/README.md and zigux/tests/README.md so they explicitly include zigux/bindings/notifier_abi.zig, the starter export shim companion, and zigux/tests/phase3_export_uapi_layout.zig plus zigux/tests/phase3_export_uapi_layout_build.zig, while keeping the broader validator, catalog, and survey routes framed as gaps`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md` now reflects the returned notifier binding companion and the focused export/UAPI layout replay on current `master`.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with that bounded current-tree-backed packet.
- `Documentation/zigux/README.md` still needs a docs-root Phase 3 summary refresh so it stops treating `zigux/bindings/notifier_abi.zig` and the focused export/UAPI layout replay as broader gaps.
- `zigux/tests/README.md` still needs the same tests-root Phase 3 summary refresh for that returned shared ABI surface.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up if that broader surface drifts again.

## Sampled Missing Wider Packet Members

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Current Gap

The earlier shared-reminder sentence drift is only partially closed on current `master`.

The dedicated ABI and validator-support notes now record the landed notifier binding companion and the focused export/UAPI layout replay honestly, but the shared docs-root and tests-root Phase 3 summaries still undercount that returned packet and still frame those paths as broader gaps. Future follow-through in this shared-summary lane should stay limited to those two reminder surfaces unless a fresh reread finds another same-packet drift.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, policy, notifier-binding, export-shim, and focused export/UAPI layout replay surfaces; marks the remaining docs-root and tests-root reminder drift explicitly; samples wider packet members that remain absent; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that the broader Phase 3 validator, survey, catalog, IDR, IDA, or low-level-wrapper packet has returned.
