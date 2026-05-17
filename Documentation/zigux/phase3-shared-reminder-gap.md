# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 reminder drift on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit in the dedicated Phase 3 notes and the docs-root summary, but the shared tests-root and review-checklist summaries still lag that three-slice posture`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow zigux/tests/README.md and Documentation/zigux/review-checklist.md so they both describe the bounded three-slice Phase 3 posture and stop parking the policy slice as a broader missing route`

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
- `zigux/bindings/abi.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-validator-support-surface.md` already reflects the bounded three-slice posture on current `master`.
- `Documentation/zigux/README.md` now reflects the bounded three-slice posture on current `master` and no longer parks `include/zigux/abi.h` or `zigux/bindings/abi.zig` as broader missing routes.
- `zigux/tests/README.md` still carries the older narrower Phase 3 summary and still treats the policy slice anchors as broader repo-reality gaps.
- `Documentation/zigux/review-checklist.md` still tells reviewers to treat `Documentation/zigux/README.md` and `zigux/tests/README.md` as the remaining broader shared reminder surfaces and still anchors the Phase 3 shared question to only the starter packet plus `err_ptr` / `xarray`.

## Sampled Missing Wider Packet Members

- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Current Gap

The earlier docs-root and tests-root reminder drift around the starter packet and the `err_ptr` / `xarray` slice was reduced again once the docs-root summary was brought up to the current three-slice posture, but the shared tests-root and review-checklist summaries still describe only two of the landed slices and still park the policy slice anchors as if they were absent.

That means the next truthful step is an even smaller reminder-surface cleanup pass, not a new helper or validator packet. Future Phase 3 work should first bring those two remaining shared summaries up to the current three-slice posture, then only reopen broader reminder work again if additional validator or export-boundary routes land on `master`.

## Scope

This note is limited to the remaining shared-summary drift for the bounded Phase 3 packet. It records the directly readable starter, helper, and policy slices, notes that the docs-root summary is now aligned, names the shared summaries that still lag that state, samples wider packet members that remain absent, and keeps the next truthful cleanup step explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
