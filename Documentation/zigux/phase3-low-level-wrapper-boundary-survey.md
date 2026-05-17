# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the Phase 3 low-level wrapper family on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, but current master now directly exposes only one atomic helper shard plus this dedicated survey note rather than the full helper trio and focused replay packet that earlier continuity notes described`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback on 2026-05-17 reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md and zigux/helpers/atomic.zig, while repeated authenticated contents reads still return missing for zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, and zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through in survey-and-gap-accounting mode until current master materializes one more bounded companion beside zigux/helpers/atomic.zig, with the next honest implementation step being either one directly readable barrier-or-mmio helper shard or one equally bounded focused replay companion`

## Roadmap And Ledger Anchors

- The Phase 3 roadmap still names `approved atomic, barrier, and MMIO wrappers` as required Zigux features inside the ABI and interop substrate.
- Bootstrap ledger step `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, still lists `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3.py`, and `Documentation/zigux/phase3-abi-slice.md` as part of that original bounded Phase 3 substrate packet.

## Current Directly Readable Low-Level Wrapper Evidence

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`

## Missing Low-Level Wrapper Companions On Current `master`

- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

## Current Gap

The live Phase 3 tree is not empty. It already exposes one directly readable low-level helper shard through `zigux/helpers/atomic.zig`, and that shard keeps compare-exchange ordering rules reviewable on current `master`. What it does not currently expose is the rest of the approved low-level wrapper family: the barrier and MMIO helper companions, the explicit narrow-unsafe bridge companion, the focused replay route, and the dedicated survey validator packet that earlier continuity notes described.

That makes the real same-lane outcome a survey-first truthfulness repair, not another speculative helper claim. Reviewers should treat the low-level wrapper family as partially materialized on current `master`: one atomic helper shard is directly readable, while the broader barrier, MMIO, narrow-unsafe, replay, and validator companions remain current repo-reality gaps.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the one directly readable atomic helper shard, names the missing barrier, MMIO, narrow-unsafe, replay, validator, and manifest companions, and keeps the next bounded implementation step explicit. It does not claim that the broader low-level wrapper packet, shared ABI replay, or validator stack already ships on current `master`.