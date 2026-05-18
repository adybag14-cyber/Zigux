# Phase 3 Shared Reminder Gap

This note records the current bounded Phase 3 reminder drift on live `master` and the active Lane 27 bitmap/cpumask branch.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit in the dedicated Phase 3 notes, the docs root, and the tests root, but one shared reminder surface still lags: Documentation/zigux/review-checklist.md continues to describe Documentation/zigux/README.md as the remaining surface that needs the same three-slice narrowing pass even though the docs-root and tests-root summary repair is already closed`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, and zigux/tests/phase3_dev_t_starter_packet.zig, the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py; Documentation/zigux/README.md and zigux/tests/README.md already reflect that bounded three-slice posture, while Documentation/zigux/review-checklist.md still carries the older docs-root-lag wording`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep the next live-master follow-through bounded to one review-checklist wording refresh so the checklist matches the already-live docs-root and tests-root three-slice packet; keep any separate scripts-root inventory truthfulness work isolated from this shared reminder gap`
- `PHASE3_SHARED_REMINDER_BRANCH_OVERLAY=the active Lane 27 branch adds one focused bitmap/cpumask interop slice with starter-packet and fixture-backed parity coverage, so the branch-local shared reminder packet is now four slices rather than the three-slice packet shipped on live master`
- `PHASE3_SHARED_REMINDER_BRANCH_NEXT_STEP=keep the branch-local follow-through bounded to the remaining four-slice wording refresh in Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md instead of widening into broader validator, export/UAPI, low-level-wrapper, or scripts-root inventory claims`

## Directly Readable Current Packet On Live `master`

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

## Branch-Local Lane 27 Overlay

The active Lane 27 branch layers one additional helper-local interop slice on top of that live-master packet:

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `include/zigux/bitmap_cpumask.h`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`

## Shared Reminder Surfaces

### Live `master`

- `Documentation/zigux/phase3-validator-support-surface.md` reflects the bounded three-slice posture on current `master`.
- `Documentation/zigux/README.md` now also reflects that bounded three-slice posture and should stay aligned with the dedicated notes.
- `zigux/tests/README.md` carries the bounded three-slice Phase 3 summary and should stay aligned with the dedicated notes.
- `Documentation/zigux/review-checklist.md` is the remaining shared reminder surface that still needs the same three-slice wording refresh.
- `scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this shared-gap note.

### Active Lane 27 Branch

- `Documentation/zigux/phase3-validator-support-surface.md` already records the branch-local four-slice posture and the exact remaining reminder drift.
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md` keeps the helper-local bitmap/cpumask overlay bounded and names the same three remaining branch-local reminder surfaces.
- `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still need the same four-slice wording refresh before the branch can claim a fully aligned shared reminder packet.
- `scripts/zigux/README.md` should remain a separate scripts-root follow-up even after those three branch-local reminder surfaces are refreshed.

## Sampled Missing Wider Packet Members

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/tests/phase3_low_level_wrappers.zig`

## Current Gap

On live `master`, the earlier docs-root and tests-root reminder drift around the starter packet, the `err_ptr` / `xarray` helper slice, and the later landed policy slice is now closed. What remains there is a narrower checklist-only follow-through. `Documentation/zigux/review-checklist.md` still describes `Documentation/zigux/README.md` as the remaining lagging surface even though the docs root and tests root already carry the bounded three-slice posture.

On the active Lane 27 branch, the packet has moved one step further. The bitmap/cpumask starter-plus-dump overlay is already present, but the shared reminder wording has not caught up yet. Future Phase 3 work in this exact lane should therefore keep the next follow-through bounded to `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` so those three surfaces describe the branch-local four-slice packet truthfully before any broader summary cleanup is attempted.

## Scope

This note is limited to the current shared-summary status for the bounded Phase 3 packet. It records the directly readable starter, helper, and policy slices on live `master`; records the branch-local bitmap/cpumask overlay carried by the active Lane 27 branch; keeps the live-master checklist-only wording drift explicit; keeps the branch-local four-slice wording drift explicit; samples wider packet members that remain absent; and preserves the non-overlapping next steps for any future follow-up. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
