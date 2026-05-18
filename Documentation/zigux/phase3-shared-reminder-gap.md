# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the shared docs-root Phase 3 summary now reflects that return, and the remaining shared-reminder follow-through is the tests-root summary`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, Documentation/zigux/phase3-kernel-export-shim-governance.md, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; it also confirms the bounded low-level-wrapper packet through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; current master also directly serves the packet-local export/UAPI survey note through Documentation/zigux/phase3-export-uapi-boundary-survey.md together with the packet-local validator scripts/zigux/validate-phase3-export-uapi-survey.py and the focused layout replay pair zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig; repeated authenticated reads still return missing for Documentation/zigux/phase3-linux-zigux-header-governance.md, scripts/zigux/phase3_catalog.py, and zigux/tests/fixtures/phase3_abi_manifest.json; Documentation/zigux/README.md now keeps Documentation/zigux/phase3-export-uapi-boundary-survey.md and scripts/zigux/validate-phase3-export-uapi-survey.py explicit as returned shared reminder evidence, while zigux/tests/README.md still needs the first bounded Phase 3 tests-root reminder pass that makes those same packet-local surfaces explicit beside the returned starter, helper, policy, and layout-replay packet`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=refresh zigux/tests/README.md so the shared Phase 3 tests-root summary keeps the returned packet-local export/UAPI survey note and validator explicit while leaving the wider linux-header-governance, catalog, and manifest gaps parked`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
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

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` now keeps the kernel-facing export shim packet explicit without implying the broader export/UAPI survey stack has returned.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with the bounded current-tree-backed starter, helper, policy, notifier-binding, separately readable shared validator entrypoint, and focused layout-replay packet.
- `Documentation/zigux/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned packet-local shared reminder evidence instead of framing them as repo-reality gaps.
- `zigux/tests/README.md` currently still needs the first bounded Phase 3 shared-summary refresh: it does not yet keep `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py` explicit as returned tests-root evidence beside the starter, helper, policy, and layout-replay packet.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and already scopes its Phase 3 inventory to the live scripts-root packet instead of this shared docs-root and tests-root reminder drift.

## Sampled Missing Wider Packet Members

- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Current Gap

The earlier shared-reminder drift has narrowed again and is now limited to the tests-root summary.

Current `master` keeps the packet-local export/UAPI survey note and validator directly readable through `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `Documentation/zigux/README.md` now records those same packet-local surfaces as current shared reminder evidence. `zigux/tests/README.md` is the remaining shared reminder surface that still needs a bounded follow-through pass.

Future same-lane follow-through should stay bounded to `zigux/tests/README.md` and keep scripts-root inventory work separate.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, policy, notifier-binding, kernel-export-shim, packet-local export/UAPI survey note and validator, separately readable shared validator entrypoint, focused export/UAPI layout replay, and low-level-wrapper reminder surfaces; records the shared docs-root summary as aligned and the tests-root summary as still needing one bounded refresh; samples wider packet members that remain absent; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that the broader Phase 3 linux-header governance note, catalog wiring, manifest-backed ABI inventory, or shared replay packet has returned beyond the bounded packet-local survey and replay surfaces already enumerated above.