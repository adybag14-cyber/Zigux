# Phase 13 Devres DMA Boundary Gap

## Scope

This note records one bounded `P13-L11` drift inside the current Phase 13 devres packet.

The live manifest and survey already keep the helper-only DMA/scatterlist boundary explicit, including the blocked `phase13-devres-live-dma-mappings` and `phase13-devres-live-scatterlist-ownership` states.

## Current Drift

Two older validation surfaces still lag that live packet:

- `scripts/zigux/check-phase13-devres-packet-alignment.py` still expects `17` manifest gaps and `6` blocked states, and it does not yet model `phase13-devres-live-dma-mappings` or `blocked_on_live_dma_state`.
- `zigux/tests/phase13_devres_reviewability.zig` still expects the same `17`-gap and `6`-blocked shape and likewise omits the live DMA-mappings block.

## Why This Matters

Without a dedicated guard, the current repo can keep shipping a truthful manifest and survey while the older checker-local validation packet silently lags the live DMA/scatterlist boundary.

That is reviewability drift, not helper progress.

## Next Bounded Step

Refresh the checker-local validation surfaces so they model the same blocked live-DMA and live-scatterlist packet already carried by:

- `zigux/tests/phase13_devres_manifest.json`
- `Documentation/zigux/phase13-devres-survey.md`
- `zigux/tests/phase13_devres_dma_coherent.zig`

Do not widen this into helper behavior, shared release-note wording, or coherent-DMA replay ownership.
