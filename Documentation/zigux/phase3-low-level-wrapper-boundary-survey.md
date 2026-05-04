# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current atomic, barrier, and MMIO boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max`
- `PHASE3_ATOMIC_STATUS=bounded-helper-surface-and-mismatch-replay-landed`
- `PHASE3_ATOMIC_BLOB_SHA=30a95ede47e7a1223b0b5a5314c1960b1d102008`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full`
- `PHASE3_BARRIER_STATUS=throwaway-probe-barriers-landed`
- `PHASE3_BARRIER_BLOB_SHA=409abd11b3df741121f39f758359ca298c5e1c45`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64-plus-policy-read8-write8-read16-write16-read32-write32-read64-write64-and-generic-policy-bridges`
- `PHASE3_MMIO_STATUS=scoped-width-specific-mmio-and-policy-bridge-landed`
- `PHASE3_MMIO_BLOB_SHA=ff5a7457511619bb9f23792cde74a53b29377823`
- `PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_BUILD_BLOB_SHA=5ff32e1306830195e248c26b2125cb6f9b2418c9`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_TEST_BLOB_SHA=2fef30ca53d96481e8477a5ed7b0716ce0dc98ea`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=230bd0dcb1662291d19983d2b434bfc0feda2cef`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=c339c6d6791ffd3646f6cba96b686de963995f7f`
- `PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-relaxed-order-barrier-variants-or-broader-kernel-style-atomic-family-is-shipped-yet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-the-low-level-wrapper-packet-narrow-until-one-roadmap-backed-boundary-slice-needs-another-explicit-atomic-or-mmio-helper`

## Roadmap Contract

Phase 3 is where Zigux starts defining the permanent C and Zigux boundary instead of only helper scaffolding.

For this lane, the roadmap requirements are:

- approved atomic, barrier, and MMIO wrappers
- approved atomic wrappers
- approved barrier wrappers
- approved MMIO wrappers
- explicit narrow-unsafe review instead of hidden raw-pointer expansion

That does not require a broad kernel-style low-level helper family yet.
It does require the live repo to say clearly which low-level wrappers are already part of the permanent boundary and which wider helper families are still intentionally deferred.

## Live Repo Reality

This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for the directly coupled low-level packet.

The current tree already carries a real bounded low-level wrapper packet:

- `zigux/helpers/atomic.zig` currently limits the approved helper surface to `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`, all parameterized by Zig atomic order rather than widening into a broader kernel-style helper family. The current focused replay now also keeps acquire-only, release-only, `acq_rel`, and monotonic ordering combinations explicit, so reviewers do not have to infer non-`seq_cst` support from helper signatures alone.
- `zigux/helpers/barrier.zig` currently limits the approved barrier surface to `acquire`, `release`, `acquireRelease`, and `full`, each expressed through a throwaway ordered atomic probe so the helper does not keep hidden shared state.
- `zigux/helpers/mmio.zig` currently limits the approved MMIO surface to `range`, `read8`, `read16`, `read32`, `read64`, `write8`, `write16`, `write32`, and `write64`, plus the scoped `read8`, `write8`, `read16`, `write16`, `read32`, `write32`, `read64`, and `write64` entry points, the width-specific `read8Policy`, `write8Policy`, `read16Policy`, `write16Policy`, `read32Policy`, `write32Policy`, `read64Policy`, and `write64Policy` entry points, and the generic `readScopedWithPolicy` plus `writeScopedWithPolicy` bridges that keep decoded-policy MMIO access routed back through the declared narrow unsafe layer.
- `zigux/tests/phase3_low_level_wrappers_build.zig` and `zigux/tests/phase3_low_level_wrappers.zig` keep the atomic, barrier, direct-plus-scoped MMIO, width-specific policy-aware MMIO, and generic decoded-policy MMIO bridge packet reviewable on one focused compile-and-test path, and the focused build now also wires the current `interop_policy` dependency that `zigux/helpers/mmio.zig` imports.
- `zigux/tests/phase3_policy_unsafe.zig` and `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py` keep the broader whole-record interop-policy decode and second-boundary-helper MMIO story reviewable beside that focused low-level gate, so the decoded-policy MMIO surface stays explicit across both focused packets without widening the low-level wrapper lane into the broader policy-and-unsafe packet.
- `zigux/tests/phase3_low_level_wrappers.zig` now keeps the strong and weak compare-exchange replay, `fetchMin()` and `fetchMax()` replay, the acquire-only, release-only, combined acquire-plus-release, and full barrier probes, denied-scope checks, width-specific direct, scoped, and policy-aware 8-bit, 16-bit, 32-bit, and 64-bit MMIO coverage, generic decoded-policy bridge coverage across the same widths, denied-scope policy failures, misalignment failures, overflow failures, and the shared `MmioRange` layout assertion reviewable without having to infer them from the broader `phase3_abi` bundle alone. The same focused replay now also keeps acquire-only, release-only, `acq_rel`, and monotonic atomic-ordering combinations explicit instead of leaving non-`seq_cst` support implicit in the helper signatures alone.

This is real roadmap-backed progress.
It is also still a deliberately narrow packet:

- no relaxed-order barrier variants are shipped in the current packet
- no broader kernel-style atomic helper family is shipped in the current packet
- no MMIO family wider than the direct, scoped, and decoded-policy 8-bit, 16-bit, 32-bit, and 64-bit accessors is shipped in the current packet

## Ledger Alignment

This low-level wrapper packet still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means the focused atomic, barrier, and MMIO replay should be read as tighter proof for the original ABI substrate packet rather than as a new standalone tranche.

- the original substrate ledger entry already named `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, and `zigux/helpers/mmio.zig` as part of the permanent Phase 3 boundary
- current `master` now keeps the direct, scoped, width-specific policy-aware, and generic decoded-policy packet reviewable through `zigux/tests/phase3_low_level_wrappers.zig`, while `zigux/tests/phase3_policy_unsafe.zig` still carries the broader whole-record policy decode and second-boundary-helper MMIO story
- this dedicated survey note exists to keep the currently approved wrapper set explicit so future Phase 3 work can prefer survey-and-validation honesty before widening the helper family

## Current Boundary Gap

The current gap is no longer the absence of atomic, barrier, or MMIO helpers.
Those helpers exist and are reviewable.

The remaining gap for this boundary packet is breadth, not presence:

- the current packet intentionally stops short of relaxed-order or broader Linux-style barrier helpers beyond the combined acquire-plus-release fence
- the current packet intentionally stops short of a broader kernel-style atomic helper family beyond the currently approved bounded surface
- the current packet intentionally stops short of wider MMIO families beyond the currently approved direct, scoped, and decoded-policy 8-bit, 16-bit, 32-bit, and 64-bit helpers

That repo reality matches the roadmap's wrapper-first posture.
It also means this lane should stay survey-and-validation heavy until one concrete roadmap-backed boundary slice needs one more explicit low-level helper.

## Next Bounded Step

The next honest follow-on inside this family is still narrow:

- keep the current atomic, barrier, and MMIO packet stable until one roadmap-backed boundary helper needs another explicit low-level wrapper
- keep broader kernel-style atomic or barrier families still deferred until that need is real and reviewable
- keep any MMIO expansion beyond the current direct, scoped, and decoded-policy 8-bit, 16-bit, 32-bit, and 64-bit helpers deferred until a boundary slice needs it
- refresh the packet-local `*_BLOB_SHA` markers whenever the directly coupled low-level packet paths are deliberately resurveyed after boundary-local changes

This lane does not justify broad atomic API growth, hidden shared-state barriers, or a wider MMIO family on its own.
