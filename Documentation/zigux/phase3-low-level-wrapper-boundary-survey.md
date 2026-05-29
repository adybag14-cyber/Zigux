# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the bounded Phase 3 low-level wrapper packet on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder plus directly readable interop-policy raw-pointer bridge entrypoints, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one shared tests-root reminder, one workflow-backed replay route, and two returned shared Makefile replay gates`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/README.md, zigux/tests/build.zig, zigux/Makefile, and .github/workflows/zigux-bootstrap.yml; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the landed range-bounded MMIO typed accessors, the directly coupled unsafe-policy companion, the shared narrow-unsafe interop-policy bridge entrypoints, the dedicated build companion, the shared tests-root reminder, the workflow-backed low-level-wrapper replay route, the direct zig build phase3-low-level-wrappers replay route, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gates while the adjacent catalog-selftest guard stays outside this wrapper packet`

## Current Directly Readable Low-Level Wrapper Evidence

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`
- `zigux/Makefile`
- `make -C zigux phase3-low-level-wrappers`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `make -C zigux phase3-low-level-wrappers-test`

## Adjacent Directly Readable Phase 3 Support

- `scripts/zigux/check-phase3-catalog-selftest.py`
- `scripts/zigux/check-phase3-selftest-surface.py`
- `scripts/zigux/generate-phase3-check-wrappers.py`
- `scripts/zigux/check-phase3-wrapper-templates.py`

Current `master` also keeps `scripts/zigux/check-phase3-selftest-surface.py` directly readable as the shared Phase 3 selftest-surface guard for the returned validator-support, shared-tests-route, export/UAPI, catalog, and low-level-wrapper reminder packet. That newer shared guard should stay framed here as adjacent cross-packet support rather than as extra low-level-wrapper-local proof.

Current `master` also keeps `scripts/zigux/generate-phase3-check-wrappers.py` together with `scripts/zigux/check-phase3-wrapper-templates.py` directly readable as the adjacent stale-wrapper cleanup pair for historical shared-runner wrapper retirement, and that churn-control support should stay framed here as adjacent cross-packet evidence rather than as extra low-level-wrapper-local proof.

## Current Gap

The live Phase 3 tree now carries the roadmap-approved atomic and barrier wrapper leafs plus a broad MMIO helper packet, and current `master` also keeps the range-bounded MMIO typed accessors `constPointerAt()`, `pointerAt()`, `readAt()`, `writeAt()`, `exchangeAt()`, and `writeMaskedAt()` directly readable in `zigux/helpers/mmio.zig`. Against the roadmap's approved atomic, barrier, and MMIO wrapper requirement, that means the bounded low-level-wrapper packet no longer has the earlier helper-body MMIO gap around `MmioRange` follow-through.

Current `master` also keeps `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, `rangeInteropPolicyByte()`, and the width-specific `read8InteropPolicyBytes()`/`write8InteropPolicyBytes()`/`read8InteropPolicyByte()`/`write8InteropPolicyByte()`/`read16InteropPolicyBytes()`/`write16InteropPolicyBytes()`/`read16InteropPolicyByte()`/`write16InteropPolicyByte()`/`read32InteropPolicyBytes()`/`write32InteropPolicyBytes()`/`read32InteropPolicyByte()`/`write32InteropPolicyByte()`/`read64InteropPolicyBytes()`/`write64InteropPolicyBytes()`/`read64InteropPolicyByte()`/`write64InteropPolicyByte()` entrypoints directly readable in `zigux/helpers/mmio.zig`, so the bounded low-level-wrapper survey should treat those MMIO range and width-specific wrappers as landed helper-local evidence rather than collapsing MMIO coverage to the generic typed accessors alone.

The honest same-lane next step is therefore not new wrapper-body expansion. It is truthfulness maintenance: keep the survey note, the dedicated survey validator, the focused replay shard, the dedicated shared build companion, the returned Makefile replay gates, and the workflow-backed replay route aligned with those landed range-bounded MMIO accessors so future lane-local drift does not reintroduce a fake gap into the wrapper packet.

That live barrier helper surface, dedicated survey validator, and focused replay now line up on current `master`: `zigux/helpers/barrier.zig` keeps the generic order-checked `fence()` dispatch, `fenceOrderAllowed()`, `validateFenceOrder()`, `FenceError`, and the seq_cst `storeLoad()` alias explicit beside `fullFence()`, the dedicated survey validator exact-requires `storeLoad()` beside the existing barrier aliases, and the focused replay now routes one seq_cst masked MMIO handoff through `storeLoad()` beside the retained `fullFence()` proof. No additional helper-body follow-through is warranted here unless one of those already-landed barrier aliases drops out of the bounded low-level wrapper packet again.

Current `master` also keeps the post-atomic barrier alias `afterAtomic()` directly readable in `zigux/helpers/barrier.zig`, with its helper-local `phase3 barrier wrappers keep post-atomic full barriers explicit` proof covering an atomic RMW followed by the full-barrier handoff. Treat that as landed barrier-wrapper evidence beside `storeLoad()` and `fullFence()`, not as a reason to reopen broader low-level wrapper implementation.

Those roadmap-approved wrapper leafs now sit beside one directly readable unsafe-policy companion through `zigux/helpers/unsafe_policy.zig`, the shared narrow-unsafe decoder through `zigux/unsafe/narrow.zig`, the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, and one focused low-level-wrapper replay shard through `zigux/tests/phase3_low_level_wrappers.zig`.

Current `master` also keeps `zigux/helpers/layout_assert.zig` directly readable, and the focused replay plus the dedicated shared build companion now keep `layout_assert.assertMmioRangeLayout()` explicit as helper-local MMIO layout evidence instead of leaving that shape check implicit behind the shared ABI packet.

Current `master` also keeps the shared narrow-unsafe decoder's direct interop-policy and byte-entry raw-pointer bridge helpers explicit through `pointerAtInteropPolicyBytes()`, `pointerAtInteropPolicy()`, `constPointerAtInteropPolicyBytes()`, `constPointerAtInteropPolicy()`, `sliceAtInteropPolicyBytes()`, `sliceAtInteropPolicy()`, `constSliceAtInteropPolicyBytes()`, `constSliceAtInteropPolicy()`, `writeValueAtInteropPolicyBytes()`, and `writeValueAtInteropPolicy()` in `zigux/unsafe/narrow.zig`, so the low-level-wrapper reminder should treat those access-boundary entry points as current helper-local evidence rather than as missing follow-through.

Current `master` also keeps the shared narrow-unsafe decoder's raw-pointer bridge exchange relays explicit through `exchangeValueAtInteropPolicyBytes()`, `exchangeValueAtInteropPolicy()`, and `exchangeValueAtByte()` in `zigux/unsafe/narrow.zig`, and the focused replay now keeps those exchange handoffs reviewable beside the existing pointer, slice, and direct value relays rather than leaving the narrower mutation path implicit.

It also now exposes one dedicated shared build companion through `zigux/tests/phase3_low_level_wrappers_build.zig`, which keeps the focused replay shard runnable through `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` without widening the low-level wrapper packet into a broader Phase 3 completion claim. The shared tests-root reminder in `zigux/tests/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig` explicit beside the starter, helper, policy, and layout-replay packet, so the low-level-wrapper survey no longer treats shared tests-root coverage as a separate missing follow-through. Current `master` also keeps `zigux/Makefile`, `make -C zigux phase3-low-level-wrappers`, and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay commands and the returned shared Makefile replay gates without widening into broader Phase 3 completion claims. That directly coupled build companion and the live `zigux/helpers/mmio.zig` helper both depend on `zigux/helpers/unsafe_policy.zig`, so the packet reminder needs to keep that helper-local unsafe-policy surface explicit instead of undercounting it as if the MMIO wrapper stood alone.

Current `master` also keeps `.github/workflows/zigux-bootstrap.yml` explicit with the shipped low-level-wrapper self-test, survey check, focused replay, and shared tests-root replay steps, so the bounded reminder packet should treat that bootstrap workflow route as current support evidence rather than leaving the workflow-backed wrapper gate implicit behind the dedicated validator and Makefile route.

That workflow-backed replay step now belongs to the same bounded reminder packet as the dedicated survey validator and the returned Makefile replay gates, so later lane-local cleanup should reread those four support surfaces together instead of treating the workflow route as optional background context.

Current `master` also keeps the whole-record MMIO interop-policy predicates plus `readInteropPolicy()`, `writeInteropPolicy()`, `exchangeInteropPolicy()`, and `writeMaskedInteropPolicy()` directly readable in `zigux/helpers/mmio.zig`, so the low-level-wrapper survey and validator need to exact-require that same helper-local policy surface instead of only the byte-policy shorthand. The focused replay in `zigux/tests/phase3_low_level_wrappers.zig` now keeps the direct typed-scope `readScoped()`/`writeScoped()`/`exchangeScoped()`/`writeMaskedScoped()` MMIO proof beside both the byte-policy shorthand checks and one dedicated whole-record `InteropPolicy` replay, plus the existing atomic, barrier, and raw-pointer bridge coverage, so the scope-gated and whole-record MMIO accessors should now be treated as landed replay evidence on current `master`.

Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`, with no remaining helper-local gap inside the atomic, barrier, and MMIO leaf wrappers themselves: the packet now covers one atomic helper shard, one barrier helper companion, one MMIO helper companion, the landed range-bounded MMIO typed accessors, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder plus interop-policy raw-pointer bridge entrypoints, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, two returned shared Makefile replay gates, and two direct replay commands, while the separately readable Phase 3 catalog-selftest guard stays adjacent cross-packet support rather than extra low-level-wrapper proof.

Current `master` now separately exposes the adjacent shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py`, the export/UAPI boundary survey note through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, the packet-local export/UAPI survey validator through `scripts/zigux/validate-phase3-export-uapi-survey.py`, the focused export/UAPI layout replay through `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig`, and the adjacent catalog-selftest guard through `scripts/zigux/check-phase3-catalog-selftest.py`, and those separate surfaces should stay framed as cross-packet support rather than as landed same-lane proof.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the directly readable atomic helper shard, the barrier helper companion, the MMIO helper companion, the directly readable layout-assert helper companion, the directly coupled unsafe-policy companion, the shared narrow-unsafe decoder plus interop-policy raw-pointer bridge entry points, the dedicated survey validator, the focused replay shard, the dedicated shared build companion, the returned shared Makefile replay gates, the shared tests-root reminder, the workflow-backed low-level-wrapper replay route, the whole-record MMIO interop-policy predicates and helper entry points, the landed range-bounded MMIO typed accessors, and the direct replay commands; records the separately readable adjacent catalog-selftest guard as cross-packet support; and keeps the next bounded implementation step explicit. It does not fold the separately readable shared validator, shared ABI checker, shared ABI catalog helper, or export/UAPI layout packet into low-level-wrapper completion.