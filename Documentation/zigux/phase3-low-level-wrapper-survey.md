# Phase 3 Low-Level Wrapper Survey

This note records the current atomic, barrier, and MMIO wrapper packet for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_BLOB_SHA=647275db7988f5cb53506ad3bc689336e7d1be80`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_BLOB_SHA=d3f5db5ad00737c2d0a480cac775aeb26d5f9bd9`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=51cbee2b49cf551b051eb5427c4917b2fe74e6a9`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d`
- `PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=86ca818027f58c85c296cf39214bd1804ca55b4d`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=7b9e7f33bfb4024e0c7e761d64c4920dfb92dc83`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=atomic-barrier-mmio-shared-abi-packet`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=shared-dump-covers-mmio-range-while-atomic-and-barrier-remain-helper-local-only`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-note-and-its-focused-gate-aligned-until-a-real-shared-wrapper-replay-expansion-lands`

## Roadmap Contract

Phase 3 is the point where Zigux has to make the permanent C/Zig boundary reviewable.

For this low-level wrapper lane, the roadmap-backed contract is still narrow:

- approved atomic wrappers with explicit entry points
- approved barrier wrappers with explicit entry points
- approved MMIO wrappers that stay inside the narrow unsafe boundary
- shared ABI notes and gates that tell reviewers exactly how much of that wrapper family is currently proven

This lane does not justify a larger runtime concurrency or driver wrapper family on its own.

## Live Repo Reality

The current tree carries a real low-level wrapper packet, but it is smaller than a fuller wrapper-validation story:

- `zigux/helpers/atomic.zig` exports `load`, `store`, `exchange`, and `compareExchange`, and its helper-local test proves those wrappers behave predictably on a small in-memory value.
- `zigux/helpers/barrier.zig` exports `acquire`, `release`, and `full`, and its helper-local test proves the wrapper entry points compile and run together through the current sentinel-backed implementation.
- `zigux/helpers/mmio.zig` exports `range`, `read32`, and `write32`, keeps raw-pointer formation in `zigux/unsafe/narrow.zig`, and proves bounded register access through its helper-local test.
- `zigux/tests/phase3_abi.zig` imports `atomic_helpers`, `barrier_helpers`, and `mmio_helpers`, so the shared ABI replay still compiles against the same wrapper packet.
- `zigux/tests/fixtures/phase3_abi_manifest.json` already treats all three helper files as part of the shared `abi` slice.
- `zigux/tests/phase3_abi_dump.zig` and `zigux/tests/fixtures/phase3_abi/expected.json` expose shared dump evidence for `zigux_mmio_range` and the broader `zigux_interop_policy` contract, but they do not yet publish dedicated atomic or barrier dump markers.

That makes the current low-level wrapper packet real and reviewable, but still partial: MMIO has shared dump visibility, while atomic and barrier coverage still lives only in the helper-local tests plus the shared ABI import surface.

## Ledger Alignment

This low-level wrapper survey is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That keeps this lane inside shared-packet survey and gate maintenance rather than a new helper tranche.

## Current Boundary Gap

No new helper-local bug was proven in this run.

The live gap is review and validation visibility:

- the roadmap requires approved atomic, barrier, and MMIO wrappers
- the repo does ship those wrappers and includes them in the shared ABI manifest
- only MMIO is currently exposed on the shared dump path
- without a dedicated survey-and-gate surface for this lane, reviewers have to infer that partial state by reading several files instead of one bounded packet

## Next Bounded Step

- leave this lane parked unless `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/expected.json`, or `zigux/tests/fixtures/phase3_abi_manifest.json` moves again
- if a later change adds shared atomic or barrier dump evidence, resurvey this note against the exact live files before claiming broader wrapper closure
- keep any follow-up inside the same survey-or-validator packet unless a separate lane explicitly opens wrapper implementation work
