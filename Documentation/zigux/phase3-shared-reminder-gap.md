# Phase 3 Shared Reminder Gap

This note keeps the remaining shared Phase 3 reminder drift explicit after current `master` narrowed to smaller directly readable surfaces.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now carries a bounded dev_t starter packet plus one focused helper-local err_ptr/xarray slice, but the shared tests-root and docs-root reminder surfaces still overclaim a broader ABI, export/UAPI, and validator packet as if it already ships`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback now confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, while broader reminder surfaces still describe absent wider packet members and replay routes`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow the Phase 3 section in zigux/tests/README.md and the docs-root Phase 3 summary in Documentation/zigux/README.md so they match the current starter packet plus helper-slice posture before any new slug-sanity or wider ABI reminder work`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`

## Remaining Broad Reminder Surfaces

- `zigux/tests/README.md` still presents the broader ABI, export/UAPI, low-level-wrapper, and validator packet as if those reminder members and replay routes are all shipped current-`master` evidence.
- `Documentation/zigux/README.md` still presents the broader ABI, export/UAPI, low-level-wrapper, catalog, and shared replay packet as if those wider reminder members already ship on current `master`.
- issue `#325` remains the operational tracker for this broader reminder drift while the shared surfaces are narrowed one bounded slice at a time.

## Sampled Missing Wider Packet Members

- `include/zigux/abi.h`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Current Gap

The repository already did the right thing by narrowing the dedicated Phase 3 validator-support note, aligning the checklist clause, and keeping the current helper-local slice explicit beside the dev_t starter packet. The remaining drift is now concentrated in the two broader shared reminder surfaces that still talk as if the wider ABI substrate, export/UAPI replay, and validator family are all present.

That means the next truthful step is not to replay an old slug-sanity packet or to re-expand the Phase 3 story. The next truthful step is to narrow the shared tests-root and docs-root reminders so reviewers see the starter packet, the focused helper slice, and the sampled broader gaps exactly as they exist on the live tree.

## Scope

This note is limited to the remaining shared reminder drift after the current starter packet and helper slice landed. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned. It records the directly readable current packet, names the two shared reminder surfaces that still overclaim, samples the wider packet members that remain absent, and keeps the next repair step explicit.
