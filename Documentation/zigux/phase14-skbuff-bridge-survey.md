# Phase 14 Skbuff Bridge Survey
This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- current `master` still ships the bounded skbuff anchor packet files `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, and `net/core/skbuff_bridge.zig`
- the live packet remains review-first and `boundary_map_only`: `net/core/skbuff_bridge.zig` keeps seven boundary-map areas plus the review-only lifetime and segmentation checkpoints without claiming live skbuff ownership
- explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, and the final sock-owned tail transfer remains the Phase 14 boundary
- the helper, manifest, and dedicated gate keep the exported `segs->prev` publication, `tail->next` splicing, `validate_xmit_skb_list()` consumer path, `skb_mark_not_on_list()` single-skb reset, and `tail = skb->prev` cue explicit as blocked C-owned behavior

## Boundary Reading
Against the Phase 14 roadmap, `net/core/skbuff.c` still belongs in a bounded review-first, stay-in-C posture rather than a live parity claim.
The live Zigux packet is therefore a boundary-map helper plus focused survey gate, not a rewrite, ownership-transfer, or parity-ready implementation.
Queue-facing tail publication, queue ownership, shared-info refcount ownership, checksum state, destructor and frag-list teardown, segmentation metadata, the final sock-owned tail transfer through `SKB_GSO_PARTIAL` and `sock_wfree`, and the consumer-side list reset inside `validate_xmit_skb_list()` still belong to the C implementation.

## Compile Evidence
- current `master` exposes `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, and `net/core/skbuff_bridge.zig`
- `zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` into `phase14_skbuff_bridge.zig` and registers the bounded `phase14-skbuff-bridge-tests` route inside the shared Phase 14 bundle
- the skbuff anchor remains `full_bundle_only` through `phase14-skbuff-bridge-tests`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14-test`
- current `zigux/tests/phase14_build.zig` keeps the skbuff shard out of `phase14-smoke`, so there is still no focused-smoke compile claim for this anchor packet
- that route is honest compile and gate coverage for the bounded bridge packet only; it is not evidence that Zigux owns live queue publication, skb lifetime ownership, checksum ownership, destructor coordination, or the final sock-owned tail transfer
- any future widening beyond this bridge packet still needs new stay-in-C evidence first, not stale absence wording

## Gates
1. keep this note aligned with the live bridge packet
   - it must not claim the helper, dedicated gate, or shared Phase 14 build route is absent while those files remain on current `master`
2. keep the blocked tail-owner-transfer and consumer-tail contract explicit
   - `segs->prev`, `tail->next`, `validate_xmit_skb_list()`, `skb_mark_not_on_list()`, and `tail = skb->prev` must remain named as C-owned review points while the packet stays review-first

## Next bounded step
Leave this lane parked unless a fresh skbuff-bridge-local reread finds another same-packet blocker-summary, survey, or build-route drift.
If it reopens, reread this note against `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `zigux/tests/phase14_skbuff_bridge.zig`, and `zigux/tests/phase14_build.zig` before touching any shared Phase 14 surface.
