# Phase 3 Shared Reminder Gap

This note keeps the remaining shared Phase 3 reminder drift explicit after current `master` narrowed to smaller directly readable surfaces.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now carries a bounded dev_t starter packet with paired dev_t and version bindings, two focused helper-local interop slices, and one focused helper-local policy slice, and the remaining broad reminder drift is now concentrated in the shared summary surfaces that have not yet named the full four-slice packet`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback now confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, and zigux/tests/phase3_dev_t_starter_packet_manifest.json; the focused helper-local interop slices through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json, Documentation/zigux/phase3-list-hlist-slice.md, include/zigux/list_hlist.h, zigux/uapi/list_hlist.zig, zigux/bindings/list_hlist.zig, zigux/helpers/list_view.zig, zigux/helpers/hlist_view.zig, zigux/tests/phase3_list_hlist_starter_packet.zig, zigux/tests/phase3_list_hlist_starter_packet_build.zig, zigux/tests/phase3_list_hlist_starter_packet_manifest.json, zigux/tests/phase3_list_hlist_dump.zig, and scripts/zigux/check-phase3-list-hlist.py; and the focused policy slice through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet_manifest.json, and scripts/zigux/check-phase3-policy-starter-packet.py, while Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md still describe narrower or older shared Phase 3 packets`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow only the Phase 3 sections in Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md so they explicitly name the current four-slice packet before any new shared validator or wider ABI reminder work`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-list-hlist-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/list_hlist.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/list_hlist.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/bindings/list_hlist.zig`
- `zigux/bindings/abi.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `zigux/tests/phase3_list_hlist_starter_packet.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_manifest.json`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `scripts/zigux/check-phase3-list-hlist.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`

## Remaining Broad Reminder Surfaces

- `Documentation/zigux/README.md` still presents a narrower Phase 3 summary than the directly readable four-slice packet now on current `master`.
- `Documentation/zigux/review-checklist.md` still names the older bounded reminder packet and has not yet been widened to include the list/hlist slice or the focused policy slice.
- `zigux/tests/README.md` still describes the pre-Lane-28 shared tests-root packet instead of the current four-slice review surface.

## Sampled Missing Wider Packet Members

- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/kernel/export_shim.zig`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Current Gap

The repository already did the right thing by landing the list/hlist starter packet as a current-master-safe helper-local slice beside the existing `dev_t`, `err_ptr` / `xarray`, and policy packets. The dedicated validator-support note can now describe that four-slice posture directly, but the broader shared summary surfaces still lag behind it.

That means the next truthful step is not to reopen the older snapshot-only ABI scaffold or to widen into the absent shared validator family. The next truthful step is to narrow the shared Phase 3 sections in the docs root, checklist, and tests root so reviewers see the starter packet, the two helper-local interop slices, the focused policy slice, and the sampled broader gaps exactly as they exist on the live tree.

## Scope

This note is limited to the remaining shared reminder drift after the current four-slice Phase 3 packet landed. It records the directly readable current packet, names the three shared summary surfaces that still lag behind it, samples the wider packet members that remain absent, and keeps the next repair step explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
