# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet rather than the broader shared Phase 3 ABI packet, so this note stays a repo-reality report instead of a completion claim`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair plus two starter UAPI companion files, but it still lacks the broader bindings, focused replay, and validator packet that earlier versions of the shared Phase 3 reminders described`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-16 now reaches the newly landed starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, and zigux/uapi/version.zig, while representative broader Phase 3 starter paths still remain absent, including include/zigux/abi.h, zigux/bindings/dev_t.zig, zigux/tests/phase3_export_uapi_layout.zig, and scripts/zigux/validate-phase3-export-uapi-survey.py`
- `PHASE3_NEXT_SAFE_STEP=keep Phase 3 narrowed to the next smallest current-master boundary proof by pairing this starter header-family packet with one directly readable focused replay or validator surface before widening into broader bindings, wrapper, or runtime-shim claims`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/tests/README.md` still carries a broader Phase 3 packet summary and should be narrowed in a follow-on same-lane truthfulness repair
- the roadmap and ledger still place Phase 3 in the ABI substrate and export-boundary family, so the next real progress step remains one small replay, validator, or binding slice instead of more reminder-only prose

## Bounded Starter Packet Present On Master

- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`

## Remaining Sampled Gaps

- `include/zigux/abi.h`
- `zigux/bindings/dev_t.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`

## Current Gap

The Phase 3 roadmap still calls for a narrow exported header and starter UAPI boundary. Current `master` now provides the first directly readable slice of that plan through one Linux-facing header pair and two small UAPI companions, but it still does not provide the broader bindings, focused replay, or validator packet that would make the whole ABI substrate materially present.

That means the immediate requirement in this lane has shifted from proving total absence to keeping the new bounded slice honest. Reviewers can now inspect a real starter packet on `master`, but the lane still must not imply that the wider Phase 3 binding family, layout replay surfaces, export shims, or validator routes already ship.

Broader ABI and runtime progress should therefore keep landing one real current-master slice at a time. Do not treat this starter header-family packet as Phase 3 completion, and do not widen it into a larger UAPI family, policy helper packet, low-level-wrapper claim, or runtime shim claim until the corresponding files are directly readable on `master`.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records the newly landed starter header-family packet, names a sampled set of broader Phase 3 gaps that remain absent on current `master`, and preserves a narrow next-step recommendation. It does not claim that the broader Phase 3 bindings, export/UAPI replay files, validator routes, or low-level-wrapper surfaces already ship on current `master`.
