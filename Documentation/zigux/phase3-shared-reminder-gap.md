# Phase 3 Shared Reminder Gap

This note records the current shared Phase 3 reminder drift on `master` after the dedicated ABI, helper-local, and policy slice notes were refreshed.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus one focused helper-local err_ptr/xarray slice plus one focused policy slice explicit in the dedicated Phase 3 notes, while the docs root, tests root, and review checklist still lag that three-slice posture`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig; the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig; and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py, while Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md still describe only the older two-slice shared packet`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=apply one narrow truthfulness pass to Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md so those shared reminders point at the same three-slice packet before any wider Phase 3 substrate work reopens`

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
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`

## Shared Reminder Surfaces Still To Refresh

- `Documentation/zigux/README.md` still describes only the bounded starter packet plus the helper-local `err_ptr` / `xarray` slice and still parks `include/zigux/abi.h` plus `zigux/bindings/abi.zig` as broader Phase 3 gaps instead of current policy-slice evidence.
- `zigux/tests/README.md` still describes the same older two-slice packet and still treats the policy-backed ABI binding surface as broader missing work rather than current reviewable evidence.
- `Documentation/zigux/review-checklist.md` still asks reviewers to confirm only the starter packet plus the helper-local `err_ptr` / `xarray` slice and still frames the docs root plus tests root as the remaining broader shared reminder surfaces.

## Sampled Missing Wider Packet Members

- `zigux/helpers/mmio.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/atomic.zig`
- `zigux/kernel/export_shim.zig`
- `scripts/zigux/validate-phase3.py`

## Current Gap

The remaining shared Phase 3 reminder drift is no longer about whether the focused policy slice exists. It does. The current gap is that the docs root, tests root, and review checklist still stop at the older two-slice summary and still present the shared ABI binding pair as broader missing work instead of as bounded policy-slice evidence already present on `master`.

That means the next truthful step is one narrow reminder-surface cleanup pass in those three shared files. Future Phase 3 work should not reopen broader low-level-wrapper, runtime-shim, export-boundary, or shared-validator claims until fresh current-tree proof lands.

## Scope

This note is limited to the bounded current Phase 3 shared reminder drift. It records the directly readable starter packet, helper-local slice, and focused policy slice, names the three shared reminder surfaces that still lag behind that current packet, samples wider packet members that remain absent, and keeps the next bounded follow-up explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
