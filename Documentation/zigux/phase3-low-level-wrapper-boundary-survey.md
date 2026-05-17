# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the Phase 3 low-level wrapper family on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, but current master now directly exposes one atomic helper shard, one shared narrow-unsafe decoder, this dedicated survey note, and a dedicated survey validator rather than the full helper trio and focused replay packet that earlier continuity notes described`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback on 2026-05-17 reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while repeated authenticated contents reads still return missing for zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through in survey-and-gap-accounting mode with the dedicated survey validator keeping the current atomic-plus-narrow reminder packet fail-closed until current master materializes one more bounded companion beside zigux/helpers/atomic.zig and zigux/unsafe/narrow.zig, with the next honest implementation step being either one directly readable barrier-or-mmio helper shard or one equally bounded focused replay companion`

## Roadmap And Ledger Anchors

- The Phase 3 roadmap still names `approved atomic, barrier, and MMIO wrappers` as required Zigux features inside the ABI and interop substrate.
- Bootstrap ledger step `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, still lists `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3.py`, and `Documentation/zigux/phase3-abi-slice.md` as part of that original bounded Phase 3 substrate packet.

## Current Directly Readable Low-Level Wrapper Evidence

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

## Missing Low-Level Wrapper Companions On Current `master`

- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`

## Current Gap

The live Phase 3 tree is not empty. It already exposes one directly readable low-level helper shard through `zigux/helpers/atomic.zig`, and that shard keeps compare-exchange ordering rules reviewable on current `master`. It also exposes the shared narrow-unsafe decoder through `zigux/unsafe/narrow.zig`, which keeps the approved unsafe-scope split reviewable even before the broader wrapper family lands. It also now exposes the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, which keeps the current atomic-plus-narrow reminder surface fail-closed even while the broader wrapper family stays absent. What it does not currently expose is the rest of the approved low-level wrapper family: the barrier and MMIO helper companions plus the focused replay route that earlier continuity notes described.

That keeps the honest same-lane outcome on validation and repo-reality accounting, not on speculative helper expansion. Reviewers should treat the low-level wrapper family as partially materialized on current `master`: one atomic helper shard, the shared narrow-unsafe decoder, and the dedicated survey validator are directly readable, while the broader barrier, MMIO, and replay companions remain current repo-reality gaps.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the directly readable atomic helper shard, the shared narrow-unsafe decoder, and the dedicated survey validator; names the missing barrier, MMIO, and replay companions; and keeps the next bounded implementation step explicit. It does not claim that the broader low-level wrapper packet, shared ABI replay, or validator stack already ships on current `master`.
