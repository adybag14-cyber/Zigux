# Phase 3 Shared Reminder Gap

This note keeps the remaining shared Phase 3 reminder drift explicit after the current `master` starter packet narrowed to a smaller directly readable surface.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now carries a bounded starter header-family plus dev_t packet, but the shared tests-root and checklist reminder surfaces still overclaim a broader ABI, export/UAPI, and validator packet as if it already ships`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback now confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, while broader reminder surfaces still describe absent wider packet members and replay routes`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=narrow the Phase 3 section in zigux/tests/README.md and the shared Phase 3 checklist prompt in Documentation/zigux/review-checklist.md so they match the current starter packet and sampled gap posture before any new slug-sanity or wider ABI reminder work`

## Directly Readable Starter Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`

## Remaining Broad Reminder Surfaces

- `zigux/tests/README.md` still presents the broader ABI, export/UAPI, low-level-wrapper, and validator packet as if those reminder members and replay routes are all shipped current-`master` evidence.
- `Documentation/zigux/review-checklist.md` still asks reviewers to keep `Documentation/zigux/phase3-abi-header-family-survey.md` and `Documentation/zigux/phase3-abi-h-boundary-next-step.md` aligned even though the current starter packet is now centered in `Documentation/zigux/phase3-abi-slice.md` and `Documentation/zigux/phase3-validator-support-surface.md`.
- issue `#325` remains the operational tracker for this broader reminder drift while the shared surfaces are narrowed one bounded slice at a time.

## Sampled Missing Wider Packet Members

- `include/zigux/abi.h`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Current Gap

The repository has already done the right thing once by narrowing the dedicated Phase 3 validator-support note and its checker to the directly readable starter packet on current `master`. The remaining drift is now concentrated in the broader shared reminder surfaces that still talk as if the wider ABI substrate, export/UAPI replay, and validator family are all present.

That means the next truthful step is not to replay an old slug-sanity packet or re-expand the Phase 3 story. The next truthful step is to narrow the shared tests-root and checklist reminders so reviewers see the starter packet and the remaining sampled gaps exactly as they exist on the live tree.

## Scope

This note is limited to the remaining shared reminder drift after the starter packet landed. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned. It records the current directly readable starter packet, names the two shared reminder surfaces that still overclaim, samples the wider packet members that remain absent, and keeps the next repair step explicit.