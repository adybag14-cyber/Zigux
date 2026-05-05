# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current atomic, barrier, and MMIO boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak`
- `PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed`
- `PHASE3_ATOMIC_BLOB_SHA=9e02a5504a426f154d750463a5ed2e8023ec5250`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=acquire-release-full`
- `PHASE3_BARRIER_STATUS=module-global-fence-word-still-present`
- `PHASE3_BARRIER_BLOB_SHA=409abd11b3df741121f39f758359ca298c5e1c45`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=range-read32-write32`
- `PHASE3_MMIO_STATUS=direct-32-bit-mmio-only`
- `PHASE3_MMIO_BLOB_SHA=218e68eb18f91b6df31e686fb7f121234d49fb24`
- `PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_BUILD_BLOB_SHA=5ff32e1306830195e248c26b2125cb6f9b2418c9`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_TEST_BLOB_SHA=ff067964d3be09c39c7fb052f56021db2d04d709`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=c8cc38bf91ee6e5e01808d47a141c75e1df46586`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=ce862469be6fbef9bc7833ff31d98937dcbcc753`
- `PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=helper-surface-and-focused-proof-packet-no-longer-match`
- `PHASE3_NEXT_BOUNDED_STEP=realign-the-focused-low-level-test-and-validator-packet-with-live-helper-reality-before-expanding-barrier-or-mmio-scope`

## Roadmap Contract

Phase 3 is where Zigux starts defining the permanent C and Zigux boundary instead of only helper scaffolding.

For this lane, the roadmap requirements are:

- approved atomic, barrier, and MMIO wrappers
- explicit narrow-unsafe review instead of hidden raw-pointer expansion

That does not require a broad kernel-style low-level helper family yet. It does require the live repo to say clearly which low-level wrappers are already part of the permanent boundary and when the helper sources, focused proofs, and survey notes have drifted apart.

## Live Repo Reality

This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for the directly coupled helper packet.

The current tree carries a real but narrower low-level wrapper packet than the surrounding survey-and-proof surfaces claim:

- `zigux/helpers/atomic.zig` exposes `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`, all parameterized by Zig atomic order instead of a broader kernel-style helper family.
- `zigux/helpers/barrier.zig` currently exposes only `acquire`, `release`, and `full`, and it still does so through a module-global `fence_word` rather than a throwaway local probe.
- `zigux/helpers/mmio.zig` currently exposes only `range`, `read32`, and `write32`, all routed through the narrow volatile pointer path in `zigux/unsafe/narrow.zig`.
- The dedicated low-level survey, ABI slice note, and focused proof packet currently overstate that live helper surface by describing combined acquire-release barriers plus scoped, policy-aware, and multi-width MMIO helpers that are not present in the inspected helper files.

That means the real reviewability gap in this lane is no longer helper absence. It is evidence drift between the helper sources and the focused docs-and-test packet that is supposed to describe them.

## Ledger Alignment

This low-level wrapper packet still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means the current atomic, barrier, and MMIO helpers should stay reviewable as one small substrate packet, and the next honest move is to bring the focused proof surfaces back into line with the inspected helper files before claiming more wrapper breadth.

## Current Boundary Gap

The current gap is review-surface drift, not total absence of low-level wrappers:

- the helper files already provide a bounded atomic surface, a minimal barrier surface, and a direct 32-bit MMIO surface
- the focused notes and proof packet still describe a wider barrier and MMIO family than the inspected helpers actually expose
- the barrier helper still keeps hidden shared state through `fence_word`, so even the smaller live barrier surface is not yet as explicit as the surrounding survey note previously claimed

That repo reality still fits the roadmap's wrapper-first posture, but it does not justify claiming scoped or policy-aware MMIO helpers, combined acquire-release barriers, or a broader proof packet until those surfaces really exist.

## Next Bounded Step

The next honest follow-on inside this family is still narrow:

- realign `zigux/tests/phase3_low_level_wrappers.zig`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, and the paired ABI note with the inspected helper surface
- keep the packet on the current atomic helper set plus direct 32-bit MMIO and the existing three barrier entry points unless a roadmap-backed boundary slice needs more
- if the barrier helper is revisited after that, prefer removing the hidden module-global state before adding broader barrier variants
- refresh the packet-local `*_BLOB_SHA` markers whenever the directly coupled low-level packet is deliberately resurveyed after helper-local changes
