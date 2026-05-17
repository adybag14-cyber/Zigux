# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet plus one directly readable dev_t binding, one machine-readable starter manifest, and one starter replay route rather than the broader shared Phase 3 ABI packet, so this note stays a repo-reality report instead of a completion claim`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair, two starter UAPI companion files, one starter binding, one starter manifest, and one focused starter replay route, but it still lacks the broader export-shim, validator, and wider bindings packet that earlier versions of the shared Phase 3 reminders described`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-17 now reaches the starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, and zigux/tests/phase3_dev_t_starter_packet_manifest.json, while representative broader Phase 3 paths still remain absent, including include/zigux/abi.h, zigux/tests/phase3_export_uapi_layout.zig, scripts/zigux/validate-phase3-export-uapi-survey.py, and zigux/kernel/export_shim.zig`
- `PHASE3_NEXT_SAFE_STEP=keep Phase 3 narrowed to the next smallest current-master validator or export-boundary proof that builds on this starter packet without widening into broader bindings, wrapper, or runtime-shim claims`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `zigux/tests/README.md` is still the next shared reminder surface to narrow so it matches this note and `Documentation/zigux/phase3-validator-support-surface.md` without implying the broader Phase 3 packet has already returned
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Bounded Starter Packet Present On Master

- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`

## Remaining Sampled Gaps

- `include/zigux/abi.h`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Current Gap

The Phase 3 roadmap still calls for a narrow exported header and starter UAPI boundary. Current `master` now provides a broader directly readable slice of that plan through one Linux-facing header pair, two small UAPI companions, one starter `dev_t` binding, one starter manifest, and one focused starter replay route, but it still does not provide the wider export-boundary validator packet or the broader ABI substrate.

That means the immediate requirement in this lane has shifted again from proving total absence to keeping the newly landed starter packet honest and reviewable. Reviewers can now inspect a real starter packet, a machine-readable manifest, and a focused replay route on `master`, but the lane still must not imply that the wider Phase 3 binding family, export/UAPI layout packet, export shims, or validator routes already ship.

Broader ABI and runtime progress should therefore keep landing one real current-master slice at a time. Do not treat this starter header-family packet, starter manifest, and `dev_t` replay route as Phase 3 completion, and do not widen it into a larger UAPI family, policy helper packet, low-level-wrapper claim, or runtime shim claim until the corresponding files are directly readable on `master`.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records the directly readable starter header-family packet, the newly landed `dev_t` binding, the machine-readable starter manifest, and the starter replay route, names a sampled set of broader Phase 3 gaps that remain absent on current `master`, and preserves a narrow next-step recommendation. It does not claim that the broader Phase 3 export/UAPI replay files, validator routes, or low-level-wrapper surfaces already ship on current `master`.