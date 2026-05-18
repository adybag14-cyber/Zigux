# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 shared-reminder status on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master keeps the docs-root and tests-root Phase 3 summaries aligned with the landed notifier binding companion, bounded kernel-export-shim note, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the shared ABI packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/kernel/export_shim.zig, Documentation/zigux/phase3-kernel-export-shim-governance.md, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_dev_t_starter_packet_manifest.json, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig; it also confirms the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, and scripts/zigux/check-phase3-errptr-xarray-starter-packet.py, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; it also confirms the bounded low-level-wrapper packet through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; current master also directly serves scripts/zigux/validate-phase3.py as the separately readable shared validator entrypoint; repeated authenticated reads still return missing for Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, scripts/zigux/validate-phase3-export-uapi-survey.py, and zigux/tests/fixtures/phase3_abi_manifest.json; Documentation/zigux/README.md and zigux/tests/README.md now both keep scripts/zigux/validate-phase3.py explicit as a directly readable shared validator entrypoint instead of listing it inside the broader repo-reality-gap bucket`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=leave future same-lane follow-through parked unless a fresh reread shows a different bounded Phase 3 reminder surface changed again`

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
- `scripts/zigux/validate-phase3.py`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-kernel-export-shim-governance.md` now keeps the kernel-facing export shim packet explicit without implying the broader export/UAPI survey stack has returned.
- `Documentation/zigux/phase3-validator-support-surface.md` stays aligned with the bounded current-tree-backed starter, helper, policy, notifier-binding, separately readable shared validator entrypoint, and focused layout-replay packet.
- `Documentation/zigux/README.md` is now aligned with the bounded current packet: it keeps `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, and the low-level-wrapper helper-and-build surfaces explicit while still framing `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` as repo-reality gaps.
- `zigux/tests/README.md` is now aligned on the returned notifier-binding, kernel-export-shim, focused export/UAPI layout replay, low-level-wrapper reminder packet, and separately readable shared validator entrypoint instead of keeping `scripts/zigux/validate-phase3.py` inside the broader repo-reality-gap list.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and already frames `scripts/zigux/validate-phase3.py` as the separately readable shared validator entrypoint rather than a repo-reality gap.

## Sampled Missing Wider Packet Members

- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Current Gap

The earlier shared-reminder drift is now closed on both the shared docs-root and tests-root summaries.

Current `master` now keeps `Documentation/zigux/README.md` aligned with the returned notifier binding companion, the bounded kernel-export-shim governance note, the focused export/UAPI layout replay pair, the low-level-wrapper reminder packet, and the separately readable shared validator entrypoint. `zigux/tests/README.md` now does the same and keeps `scripts/zigux/validate-phase3.py` explicit as the separately readable shared validator entrypoint instead of leaving it inside the broader missing survey and catalog list.

Future same-lane follow-through should stay parked unless a fresh reread exposes a different one-file reminder drift.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, policy, notifier-binding, kernel-export-shim, separately readable shared validator entrypoint, focused export/UAPI layout replay, and low-level-wrapper reminder surfaces; records the shared docs-root and tests-root summaries as aligned; samples wider packet members that remain absent; and preserves the non-overlapping rule that any future scripts-root inventory follow-through stays separate. It does not claim that the broader Phase 3 export/UAPI survey, shared validator packet beyond the single entrypoint, catalog, IDR, or IDA packet has returned beyond the bounded low-level-wrapper reminder packet already enumerated above.