# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the bounded Phase 3 low-level wrapper packet on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the dedicated build companion, the direct zig build phase3-low-level-wrappers-test replay route, and the shared tests-root reminder while the adjacent catalog-selftest guard stays outside this wrapper packet`

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
- `zigux/Makefile`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `make -C zigux phase3-low-level-wrappers-test`

## Adjacent Directly Readable Phase 3 Support

- `scripts/zigux/check-phase3-catalog-selftest.py`

## Current Gap

The live Phase 3 tree is no longer missing the dedicated build companion for the current low-level wrapper packet. It already exposes one directly readable low-level helper shard through `zigux/helpers/atomic.zig`, one barrier helper companion through `zigux/helpers/barrier.zig`, one MMIO helper companion through `zigux/helpers/mmio.zig`, one directly readable unsafe-policy companion through `zigux/helpers/unsafe_policy.zig`, the shared narrow-unsafe decoder through `zigux/unsafe/narrow.zig`, the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, and one focused low-level-wrapper replay shard through `zigux/tests/phase3_low_level_wrappers.zig`.

It also now exposes one dedicated shared build companion through `zigux/tests/phase3_low_level_wrappers_build.zig`, which keeps the focused replay shard runnable through `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` without widening the low-level wrapper packet into a broader Phase 3 completion claim. The shared tests-root reminder in `zigux/tests/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig` explicit beside the starter, helper, policy, and layout-replay packet, so the low-level-wrapper survey no longer treats shared tests-root coverage as a separate missing follow-through. Current `master` also keeps `zigux/Makefile` and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay command and the returned shared Makefile replay gate without widening into broader Phase 3 completion claims. That directly coupled build companion and the live `zigux/helpers/mmio.zig` helper both depend on `zigux/helpers/unsafe_policy.zig`, so the packet reminder needs to keep that helper-local unsafe-policy surface explicit instead of undercounting it as if the MMIO wrapper stood alone.

Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one returned shared Makefile replay gate, and one direct replay command are directly readable, while the separately readable Phase 3 catalog-selftest guard stays adjacent cross-packet support rather than extra low-level-wrapper proof.

Current `master` now separately exposes the adjacent shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py`, the export/UAPI boundary survey note through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, the packet-local export/UAPI survey validator through `scripts/zigux/validate-phase3-export-uapi-survey.py`, the focused export/UAPI layout replay through `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig`, and the adjacent catalog-selftest guard through `scripts/zigux/check-phase3-catalog-selftest.py`, and those separate surfaces should stay framed as cross-packet support rather than as landed same-lane proof.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the directly readable atomic helper shard, the barrier helper companion, the MMIO helper companion, the directly coupled unsafe-policy companion, the shared narrow-unsafe decoder, the dedicated survey validator, the focused replay shard, the dedicated shared build companion, the returned shared Makefile replay gate, the shared tests-root reminder, and the direct replay command; records the separately readable adjacent catalog-selftest guard as cross-packet support; and keeps the next bounded implementation step explicit. It does not fold the separately readable shared validator, shared ABI checker, shared ABI catalog helper, export/UAPI layout packet, or adjacent catalog-selftest guard into low-level-wrapper completion.
