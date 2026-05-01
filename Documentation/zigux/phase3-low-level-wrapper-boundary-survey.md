# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current atomic, barrier, and MMIO boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor`
- `PHASE3_ATOMIC_STATUS=bounded-helper-surface-and-mismatch-replay-landed`
- `PHASE3_ATOMIC_BLOB_SHA=0b8982b9671cdbc968d5f121175a130cc21422d0`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=acquire-release-full`
- `PHASE3_BARRIER_STATUS=throwaway-probe-barriers-landed`
- `PHASE3_BARRIER_BLOB_SHA=309ba685e24c808488bea93131febe9aad615539`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64`
- `PHASE3_MMIO_STATUS=scoped-width-specific-mmio-and-64-bit-guard-coverage-landed`
- `PHASE3_MMIO_BLOB_SHA=f89427a1d2d9a3738575e70b4303a791cce8a3cd`
- `PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_BUILD_BLOB_SHA=26de15d04505e0d345e874c538044200507ab8c2`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_TEST_BLOB_SHA=1c7b1c9da723b6626366931fd995e90d471496c6`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=abddfc50e256426894fafc3752339bd1cea79a17`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=4053835af745f0841b13ebd8d7eb6a5af33003bc`
- `PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-relaxed-order-barrier-variants-or-broader-kernel-style-atomic-family-is-shipped-yet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-the-low-level-wrapper-packet-narrow-until-one-roadmap-backed-boundary-slice-needs-an-expanded-barrier-or-atomic-helper`

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

- `zigux/helpers/atomic.zig` currently limits the approved helper surface to `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `compareExchange`, and `compareExchangeWeak`, all parameterized by Zig atomic order rather than widening into a broader kernel-style helper family.
- `zigux/helpers/barrier.zig` currently limits the approved barrier surface to `acquire`, `release`, and `full`, each expressed through a throwaway ordered atomic probe so the helper does not keep hidden shared state.
- `zigux/helpers/mmio.zig` currently limits the approved MMIO surface to `range`, `read8`, `read16`, `read32`, `read64`, `write8`, `write16`, `write32`, and `write64`, plus the scoped `read8`, `write8`, `read16`, `write16`, `read32`, `write32`, `read64`, and `write64` entry points that keep volatile pointer formation routed back through the declared narrow unsafe layer.
- `zigux/tests/phase3_low_level_wrappers_build.zig` and `zigux/tests/phase3_low_level_wrappers.zig` keep that packet reviewable on one focused compile-and-test path.
- `zigux/tests/phase3_low_level_wrappers.zig` now keeps the strong and weak compare-exchange replay, barrier probe, denied-scope checks, width-specific direct and scoped 32-bit and 64-bit MMIO coverage, misalignment failures, overflow failures, and the shared `MmioRange` layout assertion reviewable without having to infer them from the broader `phase3_abi` bundle alone.

This is real roadmap-backed progress.
It is also still a deliberately narrow packet:

- no relaxed-order barrier variants are shipped in the current packet
- no broader kernel-style atomic helper family is shipped in the current packet
- no MMIO family wider than the direct and scoped 8-bit, 16-bit, 32-bit, and 64-bit accessors is shipped in the current packet

## Ledger Alignment

This low-level wrapper packet still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means the focused atomic, barrier, and MMIO replay should be read as tighter proof for the original ABI substrate packet rather than as a new standalone tranche.

- the original substrate ledger entry already named `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, and `zigux/helpers/mmio.zig` as part of the permanent Phase 3 boundary
- current `master` now also keeps that same packet reviewable through the focused `zigux/tests/phase3_low_level_wrappers.zig` replay path
- this dedicated survey note exists to keep the currently approved wrapper set explicit so future Phase 3 work can prefer survey-and-validation honesty before widening the helper family

## Current Boundary Gap

The current gap is no longer the absence of atomic, barrier, or MMIO helpers.
Those helpers exist and are reviewable.

The remaining gap for this boundary packet is breadth, not presence:

- the current packet intentionally stops short of relaxed-order or Linux-style expanded barrier helpers
- the current packet intentionally stops short of a broader kernel-style atomic helper family beyond the currently approved bounded surface
- the current packet intentionally stops short of wider MMIO families beyond the currently approved direct and scoped 8-bit, 16-bit, 32-bit, and 64-bit helpers

That repo reality matches the roadmap's wrapper-first posture.
It also means this lane should stay survey-and-validation heavy until one concrete roadmap-backed boundary slice needs one more explicit low-level helper.

## Next Bounded Step

The next honest follow-on inside this family is still narrow:

- keep the current atomic, barrier, and MMIO packet stable until one roadmap-backed boundary helper needs another explicit low-level wrapper
- keep broader kernel-style atomic or barrier families still deferred until that need is real and reviewable
- keep any MMIO expansion beyond the current direct and scoped 8-bit, 16-bit, 32-bit, and 64-bit helpers deferred until a boundary slice needs it
- refresh the packet-local `*_BLOB_SHA` markers whenever the directly coupled low-level packet paths are deliberately resurveyed after boundary-local changes

This lane does not justify broad atomic API growth, hidden shared-state barriers, or a wider MMIO family on its own.
