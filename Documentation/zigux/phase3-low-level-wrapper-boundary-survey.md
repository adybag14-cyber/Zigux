# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current atomic, barrier, and MMIO boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak`
- `PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed`
- `PHASE3_ATOMIC_BLOB_SHA=3d709c0f9c77ae2e6a8a6d4fe6951c6326e4d1de`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair`
- `PHASE3_BARRIER_STATUS=local-sentinel-probe-only`
- `PHASE3_BARRIER_BLOB_SHA=782616269d5003960cf3f6b7ef2a3ce502ddb3ed`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=range-read8-write8-read16-write16-read32-write32-read64-write64`
- `PHASE3_MMIO_STATUS=byte-16-bit-32-bit-and-64-bit-mmio-through-narrow-pointer-bridge`
- `PHASE3_MMIO_BLOB_SHA=3e53168ff806ef94e691667f84ec871cfa6d4288`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_TEST_SCOPE=focused-atomic-barrier-mmio-replay-plus-signed-atomic-edges-acq-rel-strong-compare-exchange-mismatch-barrier-locality-non-seq-cst-ordering-and-byte-16-bit-32-bit-and-64-bit-mmio-range-replay`
- `PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface`
- `PHASE3_LOW_LEVEL_TEST_BLOB_SHA=6e34681a33cba837600cac89fc225d54520ffd6c`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b`
- `PHASE3_ABI_EXPECTED_BLOB_SHA=891be039615b878e10fda94788bc896ef12aac7b`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=4cdf556d8b2cf2182bf7dbc625e7e062d9d367c2`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=06546498c75e7efc7e60f110162a1c96f32a41e3`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_BOUNDARY_SCOPE=focused-low-level-replay-plus-shared-abi-compile-layout-dump-packet`
- `PHASE3_BOUNDARY_GAP=focused-low-level-replay-now-covers-signed-fetch-and-min-max-edges-plus-monotonic-and-acq-rel-strong-compare-exchange-mismatch-byte-16-bit-32-bit-and-64-bit-mmio-range-and-barrier-locality-while-shared-abi-packet-still-carries-the-broader-compile-layout-and-dump-proof`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-the-focused-replay-and-the-shared-abi-packet-aligned-when-helper-surface-moves`

## Roadmap Contract

Phase 3 is where Zigux starts defining the permanent C and Zigux boundary instead of only helper scaffolding.

For this lane, the roadmap requirements are still narrow:

- approved atomic, barrier, and MMIO wrappers
- explicit narrow-unsafe review instead of hidden raw-pointer expansion
- compile, layout, dump, and focused replay evidence that tells reviewers exactly how much of the low-level wrapper family is actually proven on current `master`

That still does not require a broad kernel-style low-level helper family. It does require the repo to say clearly which low-level wrappers are already shipped, which focused replay is real, and which broader proof still comes from the shared ABI packet.

## Live Repo Reality

This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for this directly coupled low-level wrapper packet.

The current tree carries a real low-level wrapper packet:

- `zigux/helpers/atomic.zig` exposes `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`, with helper-local tests still carrying a few atomic edge cases beyond the focused replay.
- `zigux/helpers/barrier.zig` exposes `acquire`, `release`, `full`, and `acquireRelease()` through local compiler-barrier wrappers, with direct locality proof now also present in the focused replay.
- `zigux/helpers/mmio.zig` exposes `range`, `read8`, `write8`, `read16`, `write16`, `read32`, `write32`, `read64`, and `write64`, all routed through the narrow pointer bridge in `zigux/unsafe/narrow.zig`, which now keeps the MMIO pointer handoff at `align(1)` so byte-addressed 16-bit, 32-bit, and 64-bit accesses do not silently assume stronger alignment than the helper packet proves.
- `zigux/tests/phase3_low_level_wrappers.zig` now directly proves the shipped helper surface, including fetch, signed atomic arithmetic and min/max edges, monotonic strong `compareExchange()`, `acq_rel` strong `compareExchange()` mismatch handling, weak compare-exchange coverage, explicit barrier-locality replay, non-`seq_cst` ordering, plus byte-addressed 16-bit, 32-bit, and 64-bit MMIO range descriptors and odd-offset MMIO behavior.
- The shared compile, layout, and dump proof for this packet still lives in `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/expected.json`, and `zigux/tests/fixtures/phase3_abi_manifest.json`.

## Ledger Alignment

This low-level wrapper packet still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That keeps this lane inside shared-packet survey and validator maintenance rather than a new helper tranche.

## Current Boundary Gap

The live gap is no longer helper absence and it is no longer the absence of a dedicated replay.

The current reviewability gap is narrower:

- the helper files already ship the bounded atomic, barrier, and MMIO surface listed above
- the repo now has a dedicated focused replay for that starter packet in `zigux/tests/phase3_low_level_wrappers.zig`
- the focused replay now covers signed `fetchAdd` and `fetchSub`, signed `fetchMin` and `fetchMax`, monotonic strong `compareExchange()`, `acq_rel` strong `compareExchange()` mismatch handling, byte/16-bit/32-bit/64-bit MMIO range descriptors, non-`seq_cst` atomic orderings, direct barrier-locality proof, and the byte-addressed alignment handoff for odd-offset 16-bit, 32-bit, and 64-bit MMIO
- the shared ABI packet remains the broader compile, layout, and dump proof surface for this family

That repo reality still fits the roadmap's wrapper-first posture, but it means this survey should describe the widened focused replay honestly without pretending it replaces the shared ABI packet.

## Next Bounded Step

- leave this lane parked unless one of the directly coupled helper files, the focused replay, or the shared ABI proof files moves again
- if the helper surface grows, refresh both this survey and the dedicated replay before claiming broader closure
- keep any follow-up inside the same replay-or-validator packet unless a separate lane explicitly opens low-level wrapper implementation work
