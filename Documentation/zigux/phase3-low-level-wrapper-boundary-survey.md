# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the bounded Phase 3 low-level wrapper packet on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, and export/UAPI survey-validator surfaces now read separately on current master, while the separate catalog-selftest guard remains an adjacent broader gap`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the dedicated build companion, the direct zig build phase3-low-level-wrappers-test replay route, and the shared tests-root reminder while the separate catalog-selftest guard stays outside this wrapper packet`

## Current Directly Readable Low-Level Wrapper Evidence

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

## Remaining Adjacent Phase 3 Gaps

- `scripts/zigux/check-phase3-catalog-selftest.py`

## Current Gap

The live Phase 3 tree is no longer missing the dedicated build companion for the current low-level wrapper packet. It already exposes one directly readable low-level helper shard through `zigux/helpers/atomic.zig`, one barrier helper companion through `zigux/helpers/barrier.zig`, one MMIO helper companion through `zigux/helpers/mmio.zig`, one directly readable unsafe-policy companion through `zigux/helpers/unsafe_policy.zig`, the shared narrow-unsafe decoder through `zigux/unsafe/narrow.zig`, the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, and one focused low-level-wrapper replay shard through `zigux/tests/phase3_low_level_wrappers.zig`.

It also now exposes one dedicated shared build companion through `zigux/tests/phase3_low_level_wrappers_build.zig`, which keeps the focused replay shard runnable through `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` without widening the low-level wrapper packet into a broader Phase 3 completion claim. The shared tests-root reminder in `zigux/tests/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig` explicit beside the starter, helper, policy, and layout-replay packet, so the low-level-wrapper survey no longer treats shared tests-root coverage as a separate missing follow-through. That directly coupled build companion and the live `zigux/helpers/mmio.zig` helper both depend on `zigux/helpers/unsafe_policy.zig`, so the packet reminder needs to keep that helper-local unsafe-policy surface explicit instead of undercounting it as if the MMIO wrapper stood alone.

Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, and one direct replay command are directly readable, while the broader shared Phase 3 catalog-selftest guard remains a separate gap.

Current `master` now separately exposes the adjacent shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py`, the export/UAPI boundary survey note through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, the packet-local export/UAPI survey validator through `scripts/zigux/validate-phase3-export-uapi-survey.py`, and the focused export/UAPI layout replay through `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig`, while the separate catalog-selftest guard `scripts/zigux/check-phase3-catalog-selftest.py` is still not directly readable here and should stay framed as an adjacent gap rather than as landed same-lane proof.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the directly readable atomic helper shard, the barrier helper companion, the MMIO helper companion, the directly coupled unsafe-policy companion, the shared narrow-unsafe decoder, the dedicated survey validator, the focused replay shard, the dedicated shared build companion, the shared tests-root reminder, and the direct replay command; names the remaining broader shared Phase 3 catalog-selftest guard; and keeps the next bounded implementation step explicit. It does not claim that the remaining shared Phase 3 catalog-selftest guard already ships, and it does not fold the separately readable shared validator, shared ABI checker, shared ABI catalog helper, or export/UAPI layout packet into low-level-wrapper completion.
