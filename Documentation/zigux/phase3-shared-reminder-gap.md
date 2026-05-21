# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the shared tests-root export/UAPI layout route, and the direct C smoke proof; the docs-root and tests-root Phase 3 summaries now reflect those returns, while the scripts-root summary stays aligned on the adjacent inventory and shared export/UAPI layout surfaces without widening into broader replay claims`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, Documentation/zigux/phase3-kernel-export-shim-governance.md, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, zigux/tests/phase3_export_uapi_layout_build.zig, zigux/tests/build.zig, and scripts/zigux/check-phase3-export-uapi-c-header-smoke.py; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py; it also confirms the focused xarray-slot slice through Documentation/zigux/phase3-xarray-slot-slice.md, zigux/helpers/xarray_slot_view.zig, zigux/tests/phase3_xarray_slot_starter_packet.zig, zigux/tests/phase3_xarray_slot_starter_packet_build.zig, zigux/tests/phase3_xarray_slot_dump.zig, zigux/tests/phase3_xarray_slot_dump_build.zig, zigux/tests/fixtures/phase3_xarray_slot/expected.json, scripts/zigux/check-phase3-xarray-slot-starter-packet.py, and scripts/zigux/check-phase3-xarray-slot.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; it also confirms the bounded low-level-wrapper packet through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; current master also directly serves the packet-local export/UAPI survey note through Documentation/zigux/phase3-export-uapi-boundary-survey.md together with the packet-local validator scripts/zigux/validate-phase3-export-uapi-survey.py, the shared tests-root route zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig, the focused layout replay pair zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig, and the direct C smoke route python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py; current master also directly serves the dedicated header-family survey follow-through through Documentation/zigux/phase3-abi-header-family-survey.md together with scripts/zigux/validate-phase3-abi-header-family-survey.py, and the focused abi.h next-step follow-through through Documentation/zigux/phase3-abi-h-boundary-next-step.md; current master also directly serves the shared ABI catalog helper through scripts/zigux/phase3_catalog.py together with the manifest-backed ABI inventory through zigux/tests/fixtures/phase3_abi_manifest.json; current master also directly serves Documentation/zigux/phase3-linux-zigux-header-governance.md as the bounded Linux-header ownership note for include/linux/zigux.h; Documentation/zigux/README.md and zigux/tests/README.md now keep the validator-support, helper-local, xarray-slot, header-family, abi.h next-step, catalog, shared export/UAPI layout, direct C smoke, and layout-replay reminder family explicit with the same bounded posture, while scripts/zigux/README.md keeps the aligned validator-support, helper-local, xarray-slot, header-family, abi.h next-step, catalog, and shared export/UAPI layout surfaces explicit without yet restating the direct C smoke pair`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep this note parked unless a fresh current-master reread shows the scripts-root direct-C-smoke follow-through has landed or another one-file reminder drift opens; the earlier docs-root refresh is closed and the remaining same-family follow-through stays scripts-root-local`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
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
- `zigux/helpers/xarray_slot_view.zig`
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
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `scripts/zigux/check-phase3-xarray-slot.py`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `zigux/tests/build.zig`
- `zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_export_uapi_c_header_smoke.c`
- `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` now keeps the kernel-facing export shim packet explicit without implying the broader export/UAPI survey stack has returned.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with the bounded current-tree-backed starter, helper, xarray-slot, policy, notifier-binding, separately readable shared validator entrypoint, shared ABI catalog helper, manifest-backed ABI inventory, returned linux-header governance note, returned header-family survey follow-through, shared tests-root export/UAPI layout route, direct C smoke route, and focused layout-replay packet.
- `Documentation/zigux/phase3-abi-header-family-survey.md` together with `scripts/zigux/validate-phase3-abi-header-family-survey.py` now stays explicit as returned same-family follow-through rather than as a sampled missing wider member.
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md` now also stays explicit as returned focused abi.h follow-through beside the dedicated header-family survey instead of being left in missing-route wording.
- `Documentation/zigux/README.md` now stays aligned with the same bounded Phase 3 reminder family already carried by the validator-support note, the shared reminder gap note, the tests-root reminder, and the scripts-root reminder; it should not be treated as a narrower holdout unless a fresh reread finds new same-lane drift.
- `zigux/tests/README.md` now also keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, the shared tests-root export/UAPI layout route, the direct C smoke route, and the returned `xarray_slot` packet explicit as returned tests-root evidence beside the starter, helper, policy, and layout-replay packet.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface, and its current Phase 3 inventory now aligns with the directly readable shared ABI manifest companion at `zigux/tests/fixtures/phase3_abi_manifest.json` plus the shared export/UAPI layout surfaces; the returned direct C smoke proof stays tracked here as adjacent same-family evidence rather than as scripts-root inventory wording.

## Sampled Missing Wider Packet Members

- No additional wider same-lane packet member needs to be called out here while the current docs-root, tests-root, and scripts-root summaries stay aligned with the returned header-family and abi.h follow-through.

## Current Gap

The earlier shared-reminder drift is now closed across the docs-root and tests-root summaries, while `scripts/zigux/README.md` keeps the narrower remaining inventory-local follow-through for the returned direct C smoke pair.

Current `master` keeps the packet-local export/UAPI survey note and validator directly readable through `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now all record those same packet-local surfaces as current shared reminder evidence. Current `master` also directly serves the shared tests-root export/UAPI layout route through `zigux/tests/build.zig` plus `zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`, and it directly serves the direct C smoke proof through `zigux/tests/phase3_export_uapi_c_header_smoke.c` plus `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`, so those two returned proof surfaces no longer belong in a reminder-gap bucket. Current `master` also directly serves the focused `xarray_slot` packet through `Documentation/zigux/phase3-xarray-slot-slice.md`, `zigux/helpers/xarray_slot_view.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_dump.zig`, `zigux/tests/phase3_xarray_slot_dump_build.zig`, `zigux/tests/fixtures/phase3_xarray_slot/expected.json`, `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`, and `scripts/zigux/check-phase3-xarray-slot.py`, and the docs-root, tests-root, and scripts-root reminder family now all keep that bounded helper-local packet explicit instead of leaving it parked only inside validator-support wording. Current `master` also directly serves the dedicated header-family survey follow-through through `Documentation/zigux/phase3-abi-header-family-survey.md` and `scripts/zigux/validate-phase3-abi-header-family-survey.py`, it directly serves the focused abi.h next-step follow-through through `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, it directly serves the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py` together with the manifest-backed ABI inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, and it directly serves `Documentation/zigux/phase3-linux-zigux-header-governance.md` as the bounded Linux-header ownership note for `include/linux/zigux.h`, so those returned survey, next-step, validator, catalog, manifest, governance, shared-route, and C-smoke surfaces no longer belong in the already-closed shared-reminder bucket.

The next same-lane follow-through is no longer the docs-root refresh: `Documentation/zigux/README.md` now explicitly carries the validator-support, `err_ptr` / `xarray`, `xarray_slot`, shared catalog companion, and bounded export/UAPI plus header-family reminder surfaces alongside the starter, policy, low-level-wrapper, shared tests-root layout, and direct C smoke packet. Any later same-lane follow-through should now stay parked until a fresh reread of the shared reminder family finds a smaller one-file truthfulness drift on current `master`.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, xarray-slot, policy, notifier-binding, kernel-export-shim, packet-local export/UAPI survey note and validator, the shared tests-root export/UAPI layout route, the direct C smoke route, the dedicated header-family survey follow-through, focused abi.h next-step follow-through, separately readable shared validator entrypoint, shared ABI catalog helper, manifest-backed ABI inventory, focused export/UAPI layout replay, low-level-wrapper reminder surfaces, and returned linux-header governance note; records the shared docs-root and tests-root summaries as aligned while keeping the scripts-root direct-C-smoke follow-through separate; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that any broader Phase 3 header-family follow-through beyond the dedicated survey, focused abi.h next-step note, linux-header governance follow-through, or wider shared replay routes have returned beyond the bounded packet-local survey, manifest, catalog, governance, shared-route, C-smoke, and replay surfaces already enumerated above.