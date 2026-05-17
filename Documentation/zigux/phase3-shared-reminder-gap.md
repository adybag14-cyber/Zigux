# Phase 3 Shared Reminder Gap

This note keeps the remaining shared Phase 3 reminder drift explicit after current `master` narrowed to smaller directly readable surfaces.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now carries a bounded dev_t starter packet plus one focused helper-local err_ptr/xarray slice, and the remaining broad reminder drift is now concentrated in the docs-root Phase 3 summary`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback now confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig; zigux/tests/README.md now matches that bounded posture, while Documentation/zigux/README.md still describes absent wider packet members and replay routes as if they already ship`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow only the Phase 3 section in Documentation/zigux/README.md so it matches the current starter packet plus helper-slice posture before any new slug-sanity or wider ABI reminder work`

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

- `Documentation/zigux/README.md` still presents the broader ABI, export/UAPI, low-level-wrapper, catalog, and shared replay packet as if those wider reminder members already ship on current `master`.
- `zigux/tests/README.md` now matches the bounded starter packet plus helper-local slice posture and no longer needs the broader shared-packet narrowing that earlier runs were tracking here.
- issue `#325` remains the operational tracker until the docs-root Phase 3 summary is narrowed to the same current-tree-backed packet.

## Sampled Missing Wider Packet Members

- `include/zigux/abi.h`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Current Gap

The repository already did the right thing by narrowing the dedicated Phase 3 validator-support note, aligning the checklist clause, and narrowing the tests-root summary to the current starter packet plus helper slice. The remaining drift is now concentrated in the docs-root Phase 3 summary, which still talks as if the wider ABI substrate, export/UAPI replay, and validator family are all present.

That means the next truthful step is not to replay an old slug-sanity packet or to reopen the tests-root packet. The next truthful step is to narrow the docs-root Phase 3 summary so reviewers see the starter packet, the focused helper slice, and the sampled broader gaps exactly as they exist on the live tree.

## Scope

This note is limited to the remaining shared reminder drift after the current starter packet and helper slice landed. It records the directly readable current packet, names the remaining docs-root Phase 3 summary as the last broad shared reminder surface, samples the wider packet members that remain absent, and keeps the next repair step explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.