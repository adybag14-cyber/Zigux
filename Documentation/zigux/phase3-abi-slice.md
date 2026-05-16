# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=the broader shared Phase 3 ABI packet is not yet materially present on current master, so this note must stay a repo-reality reminder rather than a shipped-manifest claim`
- `PHASE3_CURRENT_INTEROP_GAP=current master still lacks the starter exported-header, binding, UAPI, focused replay, and validator packet that earlier versions of this note described as already shipped`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-16 reached this note and zigux/tests/README.md, but representative Phase 3 starter paths currently return 404 on master, including include/linux/zigux.h, include/zigux/abi.h, include/zigux/dev_t.h, zigux/bindings/dev_t.zig, zigux/uapi/version.zig, zigux/tests/phase3_export_uapi_layout.zig, and scripts/zigux/validate-phase3-export-uapi-survey.py, so this lane must treat the starter ABI and runtime shim packet as backlog instead of live evidence`
- `PHASE3_NEXT_SAFE_STEP=land one bounded starter ABI packet on master and refresh this note in the same change, for example one Linux-facing header pair plus one directly readable replay or validator surface that proves the new packet actually exists`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `zigux/tests/README.md` currently still carries a broader Phase 3 packet summary and should be narrowed in a follow-on same-lane truthfulness repair
- the roadmap and ledger still place Phase 3 in the ABI substrate and export-boundary family, so the next real progress step remains a small landed header, binding, or validation slice instead of more reminder-only prose

## Sampled Missing Starter Packet Paths

- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`

## Current Gap

The Phase 3 roadmap still calls for a narrow exported header and starter UAPI boundary, but current `master` does not yet provide that packet as directly readable product evidence. The immediate requirement in this lane is honesty about what has actually landed: the shared ABI slice note exists, but the representative starter header, binding, replay, and validator paths sampled above are still absent on current `master`. That means this note should stop telling reviewers that the packet already ships and instead point them toward the next bounded implementation step that would make those claims true.

Broader ABI/runtime progress should therefore stay attached to one real landed slice at a time. Do not treat this reminder-surface repair as Phase 3 completion, and do not widen it into a larger UAPI family, policy helper packet, or runtime shim claim until the corresponding files are directly readable on `master`.

## Scope

This note is now limited to repo-reality reporting for the shared Phase 3 ABI lane. It records which surfaces were directly readable during this run, names a sampled set of missing starter ABI/runtime paths, and preserves a narrow next-step recommendation. It does not claim that the starter header family, bindings, UAPI companions, focused replay files, or validator routes already ship on current `master`.