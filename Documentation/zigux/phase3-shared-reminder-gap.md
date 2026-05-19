# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the shared ABI catalog helper plus manifest-backed inventory companion, and the shared docs-root plus tests-root Phase 3 summaries now all reflect that return while scripts-root inventory work stays separate`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, Documentation/zigux/phase3-kernel-export-shim-governance.md, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; it also confirms the bounded low-level-wrapper packet through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; current master also directly serves the packet-local export/UAPI survey note through Documentation/zigux/phase3-export-uapi-boundary-survey.md together with the packet-local validator scripts/zigux/validate-phase3-export-uapi-survey.py and the focused layout replay pair zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig; current master also directly serves the shared ABI catalog helper through scripts/zigux/phase3_catalog.py together with the manifest-backed ABI inventory through zigux/tests/fixtures/phase3_abi_manifest.json; current master also directly serves Documentation/zigux/phase3-linux-zigux-header-governance.md as the bounded Linux-header ownership note for include/linux/zigux.h; Documentation/zigux/README.md now keeps Documentation/zigux/phase3-export-uapi-boundary-survey.md and scripts/zigux/validate-phase3-export-uapi-survey.py explicit as returned shared reminder evidence, zigux/tests/README.md now also keeps those same packet-local surfaces explicit beside the returned starter, helper, policy, and layout-replay packet, and scripts/zigux/README.md remains a separate scripts-root reminder surface that now aligns with the directly readable shared ABI manifest inventory companion at zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep any future same-lane follow-through scoped to a fresh shared-summary reread only if current master changes reopen Phase 3 reminder drift`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
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
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` now keeps the kernel-facing export shim packet explicit without implying the broader export/UAPI survey stack has returned.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with the bounded current-tree-backed starter, helper, policy, notifier-binding, separately readable shared validator entrypoint, shared ABI catalog helper, manifest-backed ABI inventory, returned linux-header governance note, and focused layout-replay packet.
- `Documentation/zigux/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned shared reminder evidence instead of framing them as repo-reality gaps.
- `zigux/tests/README.md` now also keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned tests-root evidence beside the starter, helper, policy, and layout-replay packet.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface, and its current Phase 3 inventory now aligns with the directly readable shared ABI manifest companion at `zigux/tests/fixtures/phase3_abi_manifest.json`.

## Sampled Missing Wider Packet Members

- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Current Gap

The earlier shared-reminder drift is currently closed across the shared docs-root and tests-root summaries.

Current `master` keeps the packet-local export/UAPI survey note and validator directly readable through `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py`, and both `Documentation/zigux/README.md` and `zigux/tests/README.md` now record those same packet-local surfaces as current shared reminder evidence. Current `master` also directly serves the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py` together with the manifest-backed ABI inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, and it directly serves `Documentation/zigux/phase3-linux-zigux-header-governance.md` as the bounded Linux-header ownership note for `include/linux/zigux.h`, so those three surfaces no longer belong in this reminder note's missing-file sample set.

No remaining same-lane scripts-root manifest-path drift is visible after rereading the current Phase 3 reminder packet: `scripts/zigux/README.md` already names the directly readable `zigux/tests/fixtures/phase3_abi_manifest.json` inventory companion rather than the older missing `zigux/tests/phase3_abi_manifest.json` path.

Any later same-lane follow-through should stay bounded to a fresh shared-summary reread only if current-tree changes reopen the reminder packet.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, policy, notifier-binding, kernel-export-shim, packet-local export/UAPI survey note and validator, separately readable shared validator entrypoint, shared ABI catalog helper, manifest-backed ABI inventory, focused export/UAPI layout replay, low-level-wrapper reminder surfaces, and returned linux-header governance note; records the shared docs-root, tests-root, and scripts-root summaries as aligned; samples the wider header-family survey follow-through that still remains absent; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that the broader Phase 3 linux-header governance follow-through, header-family survey packet, or wider shared replay routes have returned beyond the bounded packet-local survey, manifest, catalog, governance, and replay surfaces already enumerated above.