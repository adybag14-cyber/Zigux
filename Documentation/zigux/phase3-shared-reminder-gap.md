# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 reminder drift on `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit in the dedicated Phase 3 notes, the docs root, and the shared checklist bullet, but two shared-reminder wording drifts still remain: Documentation/zigux/review-checklist.md still describes that same bounded three-slice posture as a future refresh, and zigux/tests/README.md still says the docs root plus checklist both need the same narrowing pass even though the docs root is already aligned`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, and zigux/tests/phase3_dev_t_starter_packet.zig, the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; Documentation/zigux/README.md already reflects that bounded three-slice posture, but Documentation/zigux/review-checklist.md still frames it as a future refresh and zigux/tests/README.md still groups the docs root with that pending checklist follow-through instead of limiting the remaining shared-reminder drift to the review checklist plus separate scripts-root inventory truthfulness`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep the next follow-through bounded to one shared-reminder sentence cleanup, starting with zigux/tests/README.md so the tests-root Phase 3 packet stops treating Documentation/zigux/README.md as still pending; keep any later review-checklist or scripts-root inventory truthfulness work isolated from that tests-root repair`

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
- `zigux/tests/README.md` carries the bounded three-slice Phase 3 summary overall, but one follow-through sentence still over-groups the docs root with the pending checklist cleanup.
- `Documentation/zigux/review-checklist.md` still carries the same bounded three-slice packet, but it still frames that posture as a future refresh instead of the current shared reminder packet.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this shared-gap note.

## Sampled Missing Wider Packet Members

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_low_level_wrappers.zig`

## Current Gap

The earlier docs-root reminder drift around the starter packet, the `err_ptr` / `xarray` helper slice, and the later landed policy slice is closed on current `master`.

What remains is now a narrower shared-reminder wording cleanup split across two broader reminder surfaces. `Documentation/zigux/review-checklist.md` still talks as though that bounded three-slice posture belongs to a future refresh instead of presenting it directly as the current shared reminder packet. `zigux/tests/README.md` now carries the bounded Phase 3 packet overall, but one follow-through sentence still says both the docs root and the review checklist need the same narrowing pass even though the docs root is already aligned. Future Phase 3 work in this shared reminder lane should therefore finish those broader reminder sentences one at a time, starting with the tests-root sentence, before reopening any larger Phase 3 summary cleanup.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, and policy slices; marks the docs-root reminder repair as closed; keeps the narrower tests-root plus checklist wording cleanup explicit; samples wider packet members that remain absent; and preserves the non-overlapping next step for any future follow-up. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
