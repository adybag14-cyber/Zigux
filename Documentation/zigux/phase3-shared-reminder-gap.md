# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 reminder drift on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit in the dedicated Phase 3 notes, the docs root, and the shared checklist bullet, so the remaining shared-reminder drift is now down to one tests-root sentence: zigux/tests/README.md still says the docs root plus checklist both need the same narrowing pass even though the docs root and checklist are already aligned`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, and zigux/tests/phase3_dev_t_starter_packet.zig, the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; Documentation/zigux/README.md and Documentation/zigux/review-checklist.md now both state the bounded three-slice posture directly, while zigux/tests/README.md still groups the docs root with that now-closed shared-reminder cleanup instead of limiting the remaining follow-through to the tests-root sentence plus any separate scripts-root inventory truthfulness work`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep the next follow-through bounded to one tests-root sentence cleanup in zigux/tests/README.md so the Phase 3 tests packet stops treating Documentation/zigux/README.md and Documentation/zigux/review-checklist.md as still pending; keep any separate scripts-root inventory truthfulness work isolated from that tests-root repair`

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

- `Documentation/zigux/phase3-validator-support-surface.md` reflects the bounded three-slice posture on current `master`.
- `Documentation/zigux/README.md` reflects that bounded three-slice posture and should stay aligned with the dedicated notes.
- `Documentation/zigux/review-checklist.md` now also states that same bounded three-slice packet directly.
- `zigux/tests/README.md` carries the bounded three-slice Phase 3 summary overall, but one follow-through sentence still over-groups the docs root and checklist with work that is already closed.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this shared-gap note.

## Sampled Missing Wider Packet Members

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_low_level_wrappers.zig`

## Current Gap

The earlier docs-root and checklist reminder drift around the starter packet, the `err_ptr` / `xarray` helper slice, and the later landed policy slice is now closed on current `master`.

What remains is one narrower tests-root sentence cleanup. `zigux/tests/README.md` now carries the bounded Phase 3 packet overall, but one follow-through sentence still says both the docs root and the review checklist need the same narrowing pass even though those two shared reminder surfaces are already aligned. Future Phase 3 work in this shared reminder lane should therefore finish that one tests-root sentence before reopening any larger Phase 3 summary cleanup.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, and policy slices; marks the docs-root and checklist reminder repairs as closed; keeps the narrower tests-root wording cleanup explicit; samples wider packet members that remain absent; and preserves the non-overlapping next step for any future follow-up. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
