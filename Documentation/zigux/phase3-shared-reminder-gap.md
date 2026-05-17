# Phase 3 Shared Reminder Gap

This note records the remaining shared Phase 3 reminder drift on the active Lane 30 branch and keeps the bounded four-slice packet explicit for the next same-lane follow-up.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=the remaining shared Phase 3 reminder drift is the four-slice truthfulness pass across Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct branch readback confirms the bounded dev_t starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper-local err_ptr/xarray slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, plus the helper-local xarray-slot packet through Documentation/zigux/phase3-xarray-slot-slice.md, zigux/helpers/xarray_slot_view.zig, zigux/tests/phase3_xarray_slot_starter_packet.zig, zigux/tests/phase3_xarray_slot_dump.zig, and zigux/tests/fixtures/phase3_xarray_slot_manifest.json, plus the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, and zigux/tests/phase3_policy_starter_packet_manifest.json; the three shared reminder surfaces still lag that four-slice packet on this branch`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md so they describe the same four-slice packet and keep wider Phase 3 routes parked as repo-reality gaps`
- `PHASE3_SHARED_REMINDER_GAP_CHECKER=python3 scripts/zigux/check-phase3-shared-reminder-gap.py --self-test now fail-closes on this tracker note, Documentation/zigux/phase3-validator-support-surface.md, and scripts/zigux/check-phase3-xarray-slot-starter-packet.py agreeing on the same three remaining shared reminder surfaces`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-xarray-slot-slice.md`
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
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/phase3_xarray_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`

## Shared Reminder Surfaces

- `Documentation/zigux/README.md` still needs the same four-slice narrowing pass.
- `zigux/tests/README.md` still needs the same four-slice narrowing pass.
- `Documentation/zigux/review-checklist.md` still needs the same four-slice narrowing pass.
- `scripts/zigux/check-phase3-shared-reminder-gap.py` now guards the shared reminder inventory so future same-lane passes keep this tracker note, `Documentation/zigux/phase3-validator-support-surface.md`, and `scripts/zigux/check-phase3-xarray-slot-starter-packet.py` aligned around the same three remaining shared reminder surfaces.
- Keep that pending cleanup anchored to `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and `Documentation/zigux/phase3-validator-support-surface.md` rather than reopening older saved Phase 3 publication packets.

## Sampled Missing Wider Packet Members

- `zigux/kernel/export_shim.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/helpers/ida_bitmap_view.zig`

## Current Gap

The active shared reminder drift is no longer the older two-slice gap. The current branch already carries the bounded dev_t starter packet, the focused helper-local err_ptr/xarray interop slice, the helper-local xarray-slot parity packet, and the focused policy slice. The remaining same-lane work is to update the docs-root, tests-root, and review-checklist summaries so they stop treating the xarray-slot and policy slices as broader missing routes while still leaving wider Phase 3 ABI, export/UAPI, low-level-wrapper, catalog, IDR, and IDA routes explicitly parked.

## Scope

This note is limited to the remaining shared Phase 3 reminder drift on the active Lane 30 branch. It records the directly readable four-slice packet, names the three shared reminder surfaces that still need the narrowing pass, adds a fail-closed checker for that remaining shared reminder inventory, and keeps the next truthful same-lane step explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, catalog, IDR, or IDA packet has landed on current `master`.