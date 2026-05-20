# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the shared ABI catalog helper plus manifest-backed inventory companion, and the shared tests-root plus scripts-root Phase 3 summaries now reflect those returns while the docs-root Phase 3 reminder still stays narrower`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, Documentation/zigux/phase3-kernel-export-shim-governance.md, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; it also confirms the bounded low-level-wrapper packet through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; current master also directly serves the packet-local export/UAPI survey note through Documentation/zigux/phase3-export-uapi-boundary-survey.md together with the packet-local validator scripts/zigux/validate-phase3-export-uapi-survey.py and the focused layout replay pair zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig; current master also directly serves the dedicated header-family survey follow-through through Documentation/zigux/phase3-abi-header-family-survey.md together with scripts/zigux/validate-phase3-abi-header-family-survey.py; current master also directly serves the shared ABI catalog helper through scripts/zigux/phase3_catalog.py together with the manifest-backed ABI inventory through zigux/tests/fixtures/phase3_abi_manifest.json; current master also directly serves Documentation/zigux/phase3-linux-zigux-header-governance.md as the bounded Linux-header ownership note for include/linux/zigux.h; zigux/tests/README.md now keeps Documentation/zigux/phase3-export-uapi-boundary-survey.md and scripts/zigux/validate-phase3-export-uapi-survey.py explicit as returned tests-root evidence, scripts/zigux/README.md now also keeps the dedicated validator-support validator, the returned header-family survey follow-through, and the shared ABI manifest inventory companion explicit, while Documentation/zigux/README.md still keeps a narrower direct-readback Phase 3 packet and does not yet surface the returned validator-support, err_ptr/xarray, or xarray_slot reminder family with the same explicitness`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=refresh Documentation/zigux/README.md so the docs-root Phase 3 reminder explicitly carries the returned validator-support, err_ptr/xarray, xarray_slot, and shared catalog companion surfaces without overstating broader shared replay or wider header-family returns`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
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
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` now keeps the kernel-facing export shim packet explicit without implying the broader export/UAPI survey stack has returned.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with the bounded current-tree-backed starter, helper, policy, notifier-binding, separately readable shared validator entrypoint, shared ABI catalog helper, manifest-backed ABI inventory, returned linux-header governance note, returned header-family survey follow-through, and focused layout-replay packet.
- `Documentation/zigux/phase3-abi-header-family-survey.md` together with `scripts/zigux/validate-phase3-abi-header-family-survey.py` now stays explicit as returned same-family follow-through rather than as a sampled missing wider member.
- `Documentation/zigux/README.md` still keeps a narrower Phase 3 docs-root packet than the returned same-lane reminder family, so it should not be treated as already aligned until it explicitly carries the validator-support, err_ptr/xarray, xarray_slot, and shared catalog companion surfaces without widening into broader replay claims.
- `zigux/tests/README.md` now also keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned tests-root evidence beside the starter, helper, policy, and layout-replay packet.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface, and its current Phase 3 inventory now aligns with the directly readable shared ABI manifest companion at `zigux/tests/fixtures/phase3_abi_manifest.json`.

## Sampled Missing Wider Packet Members

- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Current Gap

The earlier shared-reminder drift is currently closed across the shared tests-root and scripts-root summaries, but the docs-root Phase 3 reminder still reads narrower than the returned current-tree packet.

Current `master` keeps the packet-local export/UAPI survey note and validator directly readable through `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py`, and both `zigux/tests/README.md` and `scripts/zigux/README.md` now record those same packet-local surfaces as current shared reminder evidence. Current `master` also directly serves the dedicated header-family survey follow-through through `Documentation/zigux/phase3-abi-header-family-survey.md` and `scripts/zigux/validate-phase3-abi-header-family-survey.py`, it directly serves the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py` together with the manifest-backed ABI inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, and it directly serves `Documentation/zigux/phase3-linux-zigux-header-governance.md` as the bounded Linux-header ownership note for `include/linux/zigux.h`, so those returned survey, validator, catalog, manifest, and governance surfaces no longer belong in the already-closed shared-reminder bucket.

The next same-lane follow-through is now docs-root-only: `Documentation/zigux/README.md` still does not make `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `scripts/zigux/validate-phase3-validator-support-surface.py`, or the returned xarray-slot packet explicit, even though the current validator-support note, tests-root reminder, scripts-root reminder, and shared ABI packet all already treat those surfaces as returned bounded evidence.

Any later same-lane follow-through should stay bounded to that one docs-root refresh first, and only return to a broader shared-summary reread if current-tree changes reopen another Phase 3 reminder packet after that.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, policy, notifier-binding, kernel-export-shim, packet-local export/UAPI survey note and validator, dedicated header-family survey follow-through, separately readable shared validator entrypoint, shared ABI catalog helper, manifest-backed ABI inventory, focused export/UAPI layout replay, low-level-wrapper reminder surfaces, and returned linux-header governance note; records the shared tests-root and scripts-root summaries as aligned while leaving the docs-root reminder explicitly narrower; samples the still-missing paired next-step note; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that any broader Phase 3 header-family follow-through beyond the dedicated survey, linux-header governance follow-through, or wider shared replay routes have returned beyond the bounded packet-local survey, manifest, catalog, governance, and replay surfaces already enumerated above.
