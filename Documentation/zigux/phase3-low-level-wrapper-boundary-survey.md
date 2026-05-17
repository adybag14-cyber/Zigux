# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the Phase 3 low-level wrapper family on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one shared narrow-unsafe decoder, this dedicated survey note, a dedicated survey validator, and one focused low-level-wrapper replay shard, while the shared build companion remains absent`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback on 2026-05-17 reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, and zigux/tests/phase3_low_level_wrappers.zig, while repeated authenticated contents reads still return missing for zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through in survey-and-gap-accounting mode with the dedicated survey validator keeping the current helper-and-replay packet fail-closed until current master materializes the shared build companion beside zigux/tests/phase3_low_level_wrappers.zig, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, and zigux/unsafe/narrow.zig`

## Roadmap And Ledger Anchors

- The Phase 3 roadmap still names `approved atomic, barrier, and MMIO wrappers` as required Zigux features inside the ABI and interop substrate.
- Bootstrap ledger step `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, still lists `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3.py`, and `Documentation/zigux/phase3-abi-slice.md` as part of that original bounded Phase 3 substrate packet.

## Current Directly Readable Low-Level Wrapper Evidence

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/phase3_low_level_wrappers.zig`

## Missing Low-Level Wrapper Companions On Current `master`

- `zigux/tests/phase3_low_level_wrappers_build.zig`

## Current Gap

The live Phase 3 tree is not empty. It already exposes one directly readable low-level helper shard through `zigux/helpers/atomic.zig`, and that shard keeps compare-exchange ordering rules reviewable on current `master`. It also exposes one directly readable barrier helper companion through `zigux/helpers/barrier.zig`, which keeps compiler, acquire, release, full, and acquire-release barrier wrappers reviewable before the wider wrapper family lands. It now also exposes one directly readable MMIO helper companion through `zigux/helpers/mmio.zig`, which keeps volatile register reads, writes, exchange-style updates, and masked register writes reviewable before the shared build companion lands. It also exposes the shared narrow-unsafe decoder through `zigux/unsafe/narrow.zig`, which keeps the approved unsafe-scope split reviewable even before the broader replay route lands. It also now exposes the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, which keeps the current helper-and-replay reminder surface fail-closed even while the shared build companion stays partial. It also now exposes one focused low-level-wrapper replay shard through `zigux/tests/phase3_low_level_wrappers.zig`, which keeps the atomic, barrier, and MMIO handoff packet reviewable even though the shared build companion has not returned yet.

That keeps the honest same-lane outcome on wrapper-backed implementation plus truthfulness repair, not on speculative helper expansion. Reviewers should treat the low-level wrapper family as materially but not fully materialized on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, the shared narrow-unsafe decoder, the dedicated survey validator, and one focused low-level-wrapper replay shard are directly readable, while the shared build companion remains a current repo-reality gap.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the directly readable atomic helper shard, the barrier helper companion, the MMIO helper companion, the shared narrow-unsafe decoder, the dedicated survey validator, and the focused replay shard; names the missing shared build companion; and keeps the next bounded implementation step explicit. It does not claim that the broader low-level wrapper packet, shared ABI replay, or validator stack already ships on current `master`.