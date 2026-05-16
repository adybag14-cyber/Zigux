# Phase 14 Skbuff Bridge Survey
This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- explicit boundary-map wording for the seven review-only areas currently surfaced by `SkbuffBridgeLab.boundaryMap()`: allocation entrypoints, clone or private-copy handling, head expansion and carve, queue-facing tail publication, shared-info refcount ownership, destructor and frag-list teardown, and checksum-complete state cache
- explicit audit wording that the bridge stays `boundary_map_only` while still exposing both `SkbuffBridgeLab.lifetimeAudit()` and `SkbuffBridgeLab.segmentationAudit()` as review-only checkpoint packets
- explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, and the final sock-owned tail transfer remain in C
- compile evidence remains `full_bundle_only` through `phase14-skbuff-bridge-tests`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14-test`

## Boundary Reading
The current anchor packet is review-only.
It keeps the boundary-map helper in `net/core/skbuff_bridge.zig`, the focused survey gate in `zigux/tests/phase14_skbuff_bridge.zig`, and the manifest in `zigux/tests/phase14_skbuff_bridge_manifest.json` aligned with the shared Phase 14 smoke packet.
Against the Phase 14 roadmap, the live skbuff bridge now does the bounded work this note needs to describe: it provides a boundary map, a lifetime-audit outline, and explicit stay-in-C decisions without claiming a live port.
The boundary-map side stays at seven areas. Four areas remain `boundary_map_only`: allocation entrypoints, clone or private-copy handling, head expansion and carve, and checksum-complete state cache invalidation. Three areas stay `stay_in_c`: queue-facing tail publication, shared-info refcount ownership, and destructor plus frag-list teardown.
The audit side also stays review-only. `SkbuffBridgeLab.lifetimeAudit()` keeps the live ownership blocker explicit, and `SkbuffBridgeLab.segmentationAudit()` keeps the orphan-frag, checksum metadata, partial-tail-owner transfer, checksum-to-data-offset crossover, and exported tail-publication checkpoints reviewable as one grouped stay-in-C packet.
The skbuff lane stays parked at the live ownership blocker because shared-info refcounts, destructor teardown, checksum state, segmentation metadata, the final sock-owned tail transfer, exported tail publication, and the consumer-side list reset inside `validate_xmit_skb_list()` still belong to the C implementation. The queue-facing tail-publication packet remains bounded to `segs->prev`, `tail->next`, `skb_mark_not_on_list()`, and `tail = skb->prev` while leaving live queue ownership in C. After the roadmap-alignment helper and the exported-tail checkpoint, no smaller review-only skbuff follow-up remains before the live ownership blocker.

## Compile Evidence
- `zigux/tests/phase14_skbuff_bridge.zig` remains the anchor-local survey gate for lane `P14-L11`.
- `zigux/tests/phase14_build.zig` still wires `phase14-skbuff-bridge-tests` to `phase14_skbuff_bridge.zig` and imports `../../net/core/skbuff_bridge.zig`, so the full-bundle replay still compiles the shipped boundary-map helper instead of only note text.
- this anchor stays `full_bundle_only`; the focused `phase14-smoke` shard is reserved for `phase14-end-to-end-smoke-tests` and does not claim a dedicated skbuff replay route.

## Gates
1. run the dedicated Phase 14 build
   - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
   - `make -C zigux phase14-test`
2. run the convenience target
   - `make -C zigux phase14`

## Next bounded step
Leave this lane parked unless `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `net/core/skbuff_bridge.zig`, or this note drift again on the roadmap-backed boundary-map wording, the full-bundle-only compile evidence, or the blocked stay-in-C ownership wording.
