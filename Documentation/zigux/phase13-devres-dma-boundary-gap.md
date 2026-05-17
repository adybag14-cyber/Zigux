# Phase 13 devres DMA Boundary Gap

## Status
- `PHASE13_DEVRES_DMA_BOUNDARY_GAP_STATUS=active`
- lane: `P13-L11`
- scope: checker-local truthfulness for the existing Phase 13 devres DMA/scatterlist boundary packet

## Current gap
Current `master` keeps the helper-first DMA/scatterlist boundary explicit in the live packet:
- `zigux/tests/phase13_devres_manifest.json` now records `lane_key: P13-L01`
- the same manifest uses `surveyed_commit: master-readback-2026-05-14`
- the manifest keeps `phase13-devres-live-dma-backed-helpers` and `phase13-devres-live-scatterlist-ownership` blocked with the newer `blocked_on_live_*` status wording
- `Documentation/zigux/phase13-devres-survey.md` explicitly says older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift

The checker-local drift is that `scripts/zigux/check-phase13-devres-packet.py` still hard-codes the older `P13-L05` lane key, the older surveyed commit hash, and the earlier `blocked_on_dma_state` / `blocked_on_scatterlist_state` manifest status names.

## Why this note exists
This note keeps the mismatch reviewable without widening into helper behavior, DMA-backed parity, scatterlist lifecycle ownership, or broader Phase 13 route edits. The paired checker proves the gap is still real on current `master` and gives a bounded handoff point for the future lane that realigns the older packet checker.

## Boundaries
- no change to `lib/devres.zig`
- no change to `zigux/tests/phase13_devres_manifest.json`
- no change to `Documentation/zigux/phase13-devres-survey.md`
- no change to `scripts/zigux/validate-phase13-release.py`
