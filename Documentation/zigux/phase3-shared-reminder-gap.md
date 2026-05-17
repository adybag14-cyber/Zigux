# Phase 3 Shared Reminder Gap

This note keeps the remaining shared Phase 3 reminder drift explicit after the current branch narrowed to smaller directly readable surfaces.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current branch now carries a bounded dev_t starter packet plus three focused helper-local slices, and the remaining broader reminder drift is concentrated in the shared docs-root, tests-root, and checklist summaries`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct branch readback now confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper slices through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig; Documentation/zigux/phase3-bitmap-cpumask-slice.md, include/zigux/bitmap_cpumask.h, zigux/uapi/bitmap_cpumask.zig, zigux/bindings/bitmap_cpumask.zig, zigux/helpers/bitmap_view.zig, zigux/helpers/cpumask_view.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet.zig, and zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig; and Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, and zigux/tests/phase3_policy_starter_packet_build.zig`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow the Phase 3 sections in Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md so they all match the same bounded four-slice posture before any new broader validator or export-boundary work`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/bitmap_cpumask.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/bindings/abi.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`

## Remaining Broad Reminder Surfaces

- `Documentation/zigux/README.md` still presents a narrower two-slice Phase 3 summary and still samples broader packet members without naming the bitmap/cpumask and policy slices now carried on this branch.
- `zigux/tests/README.md` still presents the older two-slice Phase 3 tests-root reminder packet and still frames the docs-root summary as the only remaining follow-up even though the tests-root wording now lags too.
- `Documentation/zigux/review-checklist.md` still carries the older two-slice shared Phase 3 checklist clause and does not yet name the bitmap/cpumask and policy slices that this branch now exposes.
- issue `#325` remains the operational tracker until those shared summary surfaces are narrowed to the same current branch packet.

## Sampled Missing Wider Packet Members

- `zigux/bindings/notifier_abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`

## Current Gap

The current branch already did the right thing by adding the bitmap/cpumask slice note, keeping the dedicated validator-support note current, and preserving the bounded starter-plus-helper posture in the dedicated slice files. The remaining drift is now concentrated in the shared docs-root, tests-root, and checklist summaries, which still talk as if the current branch stops at the older two-slice packet or otherwise leave the newer helper-local slices implicit.

That means the next truthful step is not to reopen the older dump-style bitmap/cpumask replay packet or to widen into broader ABI substrate work. The next truthful step is to narrow those shared reminder surfaces so reviewers see the starter packet, the focused helper-local `err_ptr` / `xarray`, bitmap/cpumask, and policy slices, plus the sampled broader gaps, exactly as they exist on this branch.

## Scope

This note is limited to the remaining shared reminder drift after the current starter packet and three helper-local slices landed on the branch. It records the directly readable current packet, names the remaining shared summary surfaces, samples the wider packet members that remain absent, and keeps the next repair step explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.