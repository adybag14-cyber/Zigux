# Phase 14 Skbuff Bridge Survey
This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`
- `PHASE14_POSTURE=boundary_map_only`
- current `master` no longer exposes the earlier `P14-L11` skbuff anchor packet files `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, `net/core/skbuff_bridge.zig`, or `zigux/tests/phase14_skbuff_bridge_manifest.json`
- `phase14-skbuff-anchor-packet-missing` is the current repo-readback gap, not a roadmap status change; the retained Phase 14 blocker is still the live ownership and packet-lifetime seam recorded here as a stay-in-C boundary
- the previous `full_bundle_only` compile path from commits `a953f7dfe776dce0c693c8c15633684ed5243af8` and `9cf18b7e5859e0639347c620a7b9dc2005a3dee6` is archival only and must not be treated as live compile evidence on current `master`
- explicit stay-in-C ownership for queue publication, skb lifetime, checksum state, destructor coordination, segmentation metadata, and the final sock-owned tail transfer remains the Phase 14 boundary even while the anchor packet is absent

## Boundary Reading
Against the Phase 14 roadmap, `net/core/skbuff.c` still belongs in a bounded `boundary_map_only`, review-first, freeze-in-C posture rather than a live parity claim.
The current repo state no longer ships the earlier skbuff bridge helper, focused survey gate, or manifest packet, so this note is now a truthfulness marker rather than a live companion to a shipped anchor packet.
That missing packet is a repo-readback gap layered on top of the roadmap posture, not a reason to pretend the underlying blocker changed.
The deeper blocker is still the live ownership seam: queue-facing tail publication, queue ownership, shared-info refcount and header-write ownership, checksum state, destructor and frag-list teardown, segmentation metadata, the final sock-owned tail transfer, and the consumer-side list reset inside `validate_xmit_skb_list()` remain in C.
That means the meaningful current statement is narrower than the previous review-only helper summary: there is no live Zigux skbuff bridge packet on current `master`, and there is therefore no honest skbuff-local compile route to claim today.
The Phase 14 boundary itself has not changed.

## Compile Evidence
- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`
- current `master` no longer exposes `zigux/tests/phase14_build.zig`
- current `master` no longer exposes `net/core/skbuff_bridge.zig`
- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`
- because those packet files are absent, there is no live `phase14-skbuff-bridge-tests`, `phase14-smoke`, or `full_bundle_only` replay route to validate in this lane today
- any future compile claim for this lane must first restore a bounded skbuff anchor packet and only then reintroduce compile-route wording

## Gates
1. treat this note as a truthfulness gate only
   - it must keep the repo-readback gap explicit without turning the missing packet into a fake ownership-status change
2. keep the roadmap-facing `boundary_map_only` posture explicit
   - the survey must continue to name the retained live-ownership seam and stay-in-C decision even while the helper, manifest, and focused gate remain absent
3. restore a bounded anchor packet before restoring compile claims
   - only after a shipped skbuff helper plus focused survey gate exists again should this lane claim live compile evidence
4. keep the blocked consumer-tail contract explicit even while the packet is absent
   - `validate_xmit_skb_list()`, qdisc-facing publication, checksum ownership, segmentation metadata, destructor ordering, and the final sock-owned tail transfer must remain named as C-owned review points while the lane stays freeze-in-C

## Next bounded step
Leave this lane parked unless a future current-`master` change restores a bounded skbuff anchor packet or reintroduces stale compile-route wording.
If it reopens, first reread this note and confirm whether `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, `net/core/skbuff_bridge.zig`, and `zigux/tests/phase14_skbuff_bridge_manifest.json` all exist again before claiming any compile evidence, and keep the roadmap-facing `boundary_map_only` posture explicit if the packet is still absent.