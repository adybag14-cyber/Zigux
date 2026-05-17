# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 reminder drift on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit in the dedicated Phase 3 notes, but the shared docs-root and review-checklist summaries still lag that three-slice posture and still need a non-overlapping cleanup order`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py, while zigux/tests/README.md already reflects that bounded three-slice posture`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow Documentation/zigux/README.md first so it matches the bounded three-slice Phase 3 posture already reflected in the dedicated notes and zigux/tests/README.md, then refresh Documentation/zigux/review-checklist.md as the follow-through shared reminder surface instead of treating both summaries as one simultaneous cleanup step`

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
- `Documentation/zigux/README.md` is the first remaining shared reminder surface to refresh: it still describes the Phase 3 summary as the starter packet plus the `err_ptr` / `xarray` helper slice and still frames `include/zigux/abi.h` and `zigux/bindings/abi.zig` as broader parked routes.
- `zigux/tests/README.md` already carries the bounded three-slice Phase 3 summary and should stay aligned with the dedicated notes while the remaining shared reminder surfaces catch up.
- `Documentation/zigux/review-checklist.md` is the follow-through shared reminder surface after the docs-root pass: it still tells reviewers to treat `Documentation/zigux/README.md` and `zigux/tests/README.md` as the remaining broader shared reminder surfaces and still anchors the Phase 3 shared question to only the starter packet plus `err_ptr` / `xarray`.

## Sampled Missing Wider Packet Members

- `zigux/bindings/notifier_abi.zig`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_low_level_wrappers.zig`

## Current Gap

The earlier docs-root and tests-root reminder drift around the starter packet and the `err_ptr` / `xarray` slice was reduced, and the later landed policy slice is now already reflected in `zigux/tests/README.md`. The remaining truthful-summary gap is narrower: the docs root and review checklist still describe only two bounded current-tree-backed slices and still park the policy slice anchors as if they were absent.

That means the next truthful step is one narrow sequencing correction for the remaining shared summaries, not a new helper or validator packet. Refresh `Documentation/zigux/README.md` first so the docs root stops competing with the already-aligned tests root, then follow with `Documentation/zigux/review-checklist.md` once the docs-root wording is current. Future Phase 3 work should only reopen broader reminder cleanup again if additional validator or export-boundary routes land on `master`.

## Scope

This note is limited to the current shared-summary drift for the bounded Phase 3 packet. It records the directly readable starter, helper, and policy slices, names the shared summaries that still lag that state, records the non-overlapping cleanup order for those remaining reminder surfaces, samples wider packet members that remain absent, and keeps the next truthful cleanup step explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.