# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 reminder drift on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit in the dedicated Phase 3 notes, the docs root, the tests root, and the shared checklist bullet, but one checklist-only wording drift still remains: Documentation/zigux/review-checklist.md now describes itself as a shared reminder surface that still needs a future three-slice wording refresh instead of stating the already-live bounded three-slice posture directly`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, and zigux/tests/phase3_dev_t_starter_packet.zig, the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; Documentation/zigux/README.md and zigux/tests/README.md already reflect that bounded three-slice posture, and Documentation/zigux/review-checklist.md now points at itself rather than the docs root, but the checklist bullet still frames that same bounded posture as a future refresh instead of a current shared reminder`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep the next follow-through bounded to one review-checklist sentence cleanup so the Phase 3 checklist bullet states the already-live bounded three-slice packet directly; keep any separate scripts-root inventory truthfulness work isolated from this shared reminder gap`

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
- `Documentation/zigux/README.md` now also reflects that bounded three-slice posture and should stay aligned with the dedicated notes.
- `zigux/tests/README.md` carries the bounded three-slice Phase 3 summary and should stay aligned with the dedicated notes.
- `Documentation/zigux/review-checklist.md` now carries the same bounded three-slice packet, but one self-referential checklist sentence still needs a final wording cleanup.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this shared-gap note.

## Sampled Missing Wider Packet Members

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_low_level_wrappers.zig`

## Current Gap

The earlier docs-root and tests-root reminder drift around the starter packet, the `err_ptr` / `xarray` helper slice, and the later landed policy slice is now closed on current `master`.

What remains is a narrower checklist-only wording cleanup. `Documentation/zigux/review-checklist.md` now points at itself rather than at `Documentation/zigux/README.md`, but the Phase 3 checklist bullet still talks as though that bounded three-slice posture belongs to a future refresh instead of presenting it directly as the current shared reminder packet. Future Phase 3 work in this shared reminder lane should therefore finish that one checklist sentence cleanup before reopening broader summary cleanup.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, and policy slices; marks the docs-root and tests-root summary repair as closed; keeps the narrower checklist-only wording cleanup explicit; samples wider packet members that remain absent; and preserves the non-overlapping next step for any future follow-up. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
