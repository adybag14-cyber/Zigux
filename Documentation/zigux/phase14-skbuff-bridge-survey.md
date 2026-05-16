# Phase 14 Skbuff Bridge Survey
This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`
- current `master` no longer exposes the earlier `P14-L11` skbuff anchor packet files `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, or `net/core/skbuff_bridge.zig`
- the previous `full_bundle_only` compile path from commits `a953f7dfe776dce0c693c8c15633684ed5243af8` and `9cf18b7e5859e0639347c620a7b9dc2005a3dee6` is archival only and must not be treated as live compile evidence on current `master`
- explicit stay-in-C ownership for queue publication, skb lifetime, checksum state, destructor coordination, and the final sock-owned tail transfer remains the Phase 14 boundary even while the anchor packet is absent

## Boundary Reading
Against the Phase 14 roadmap, `net/core/skbuff.c` still belongs in a bounded review-first, stay-in-C posture rather than a live parity claim.
The current repo state no longer ships the earlier skbuff bridge helper or its focused survey gate, so this note is now a truthfulness marker rather than a live companion to a shipped anchor packet.
That means the meaningful current statement is narrower than the previous review-only helper summary: there is no live Zigux skbuff bridge packet on current `master`, and there is therefore no honest skbuff-local compile route to claim today.
The Phase 14 boundary itself has not changed. Queue-facing tail publication, queue ownership, shared-info refcount ownership, checksum state, destructor and frag-list teardown, segmentation metadata, the final sock-owned tail transfer, and the consumer-side list reset inside `validate_xmit_skb_list()` still belong to the C implementation.

## Compile Evidence
- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`
- current `master` no longer exposes `zigux/tests/phase14_build.zig`
- current `master` no longer exposes `net/core/skbuff_bridge.zig`
- because those packet files are absent, there is no live `phase14-skbuff-bridge-tests` or `full_bundle_only` replay route to validate on current `master`
- any future compile claim for this lane must first restore a bounded skbuff anchor packet and only then reintroduce compile-route wording

## Gates
1. treat this note as a truthfulness gate only
   - it must not claim a live skbuff helper, focused survey gate, or shared build route while those files remain absent on current `master`
2. restore a bounded anchor packet before restoring compile claims
   - only after a shipped skbuff helper plus focused survey gate exists again should this lane claim live compile evidence

## Next bounded step
Leave this lane parked unless a future current-`master` change restores a bounded skbuff anchor packet or reintroduces stale compile-route wording. If it reopens, first reread this note and confirm whether `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, and `net/core/skbuff_bridge.zig` all exist again before claiming any compile evidence.
