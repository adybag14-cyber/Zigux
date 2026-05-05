# Phase 3 Low-Level Wrapper Survey

This compatibility note preserves the older low-level wrapper survey markers for the bounded Phase 3 ABI substrate.

The active current-head packet for this lane now lives in `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`.
Treat that boundary survey as the authoritative live wrapper inventory.
Treat the marker block in this note as legacy gate compatibility evidence until the dedicated validator lane retires or rewires it.

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

This compatibility note does not reopen a larger runtime concurrency or driver wrapper family on its own.
It only keeps the older dedicated survey gate understandable while the newer boundary survey carries the live packet details.

## Compatibility Role

This file is no longer the best place to infer current blob IDs or wrapper breadth.
Its job is narrower:

- preserve the legacy marker set still audited by `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- point reviewers at `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` for the current packet-local helper inventory
- keep the older gate readable until the dedicated validator lane decides whether to retire or rewire it

## Live Repo Reality

The current tree still carries a real low-level wrapper packet, but the freshest wrapper evidence now lives in the boundary-survey note rather than here.
This older survey remains useful only as compatibility context for the dedicated survey gate:

- `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, and `zigux/helpers/mmio.zig` remain part of the bounded Phase 3 ABI packet
- `zigux/tests/phase3_abi.zig` still imports the corresponding helper modules through the shared ABI replay surface
- `zigux/tests/fixtures/phase3_abi_manifest.json` still keeps those helper files inside the shared `abi` slice
- the dedicated validator still reads this note's legacy marker block, so removing or silently repurposing it would create avoidable review noise before the validator lane is ready

For the current live wrapper surface, blob markers, and narrower boundary wording, use `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` first.

## Ledger Alignment

This compatibility survey still belongs to the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That keeps this lane inside stale-survey cleanup rather than helper expansion or a new validation family.

## Current Boundary Gap

No new helper-local bug is being claimed here.

The remaining gap in this note is purely compatibility hygiene:

- the active packet has moved to the boundary-survey note
- this older note still exists because a dedicated validator gate reads its markers
- reviewers should not mistake that retained marker block for the freshest source of truth

## Next Bounded Step

- leave this compatibility note parked unless the dedicated validator still needs another small clarity pass or the retained markers stop matching its expected contract
- if the validator lane later rewires to the boundary-survey note, retire this file instead of widening its scope again
- keep any follow-up inside the same survey-compatibility packet unless a separate lane explicitly reopens wrapper implementation or validation-gate work
