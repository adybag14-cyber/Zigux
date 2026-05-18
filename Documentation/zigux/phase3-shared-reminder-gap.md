# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the landed notifier binding companion plus one bounded kernel-export-shim note and focused export/UAPI layout replay explicit, but the shared docs-root and tests-root Phase 3 summaries drift in opposite directions: Documentation/zigux/README.md still overclaims absent export/UAPI survey and manifest companions while zigux/tests/README.md still frames the returned notifier-binding and layout replay packet as broader gaps`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, Documentation/zigux/phase3-kernel-export-shim-governance.md, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; repeated authenticated reads still return missing for Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, scripts/zigux/validate-phase3-export-uapi-survey.py, and zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=refresh one shared summary surface at a time, starting with Documentation/zigux/README.md so it swaps the absent export/UAPI survey and manifest claims for the returned phase3-kernel-export-shim-governance.md note, zigux/bindings/notifier_abi.zig, and the focused phase3_export_uapi_layout replay pair, then follow with the tests-root Phase 3 summary once the docs-root wording is honest again`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
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
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` now keeps the kernel-facing export shim packet explicit without implying the broader export/UAPI survey stack has returned.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with the bounded current-tree-backed starter, helper, policy, notifier-binding, and focused layout-replay packet.
- `Documentation/zigux/README.md` is now the highest-value shared reminder drift because it still treats `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` as live docs-root evidence even though authenticated reads still return them missing.
- `zigux/tests/README.md` still needs a separate tests-root refresh so it stops treating `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, and the focused export/UAPI layout replay as broader gaps.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up if that broader surface drifts again.

## Sampled Missing Wider Packet Members

- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Current Gap

The earlier shared-reminder drift is no longer just a tests-root undercount.

Current `master` does ship the notifier binding companion, the bounded kernel-export-shim governance note, and the focused export/UAPI layout replay pair, but the shared docs-root Phase 3 summary still overclaims absent export/UAPI survey and manifest companions while the shared tests-root summary still undercounts the returned notifier-binding and layout-replay packet. Future follow-through in this shared-summary lane should stay limited to those two reminder surfaces unless a fresh reread finds another same-packet drift.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, policy, notifier-binding, kernel-export-shim, and focused export/UAPI layout replay surfaces; marks the remaining docs-root and tests-root reminder drift explicitly; samples wider packet members that remain absent; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that the broader Phase 3 export/UAPI survey, shared validator, catalog, IDR, IDA, or low-level-wrapper packet has returned.