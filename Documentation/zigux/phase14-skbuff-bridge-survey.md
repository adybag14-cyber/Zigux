# Phase 14 Skbuff Bridge Survey
This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_PREVIOUS_PACKET_LANE=P14-Y03`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- `PHASE14_POSTURE=boundary_map_only`
- current `master` ships the bounded skbuff anchor packet again through `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, and `zigux/tests/phase14_build.zig`
- `phase14-skbuff-live-ownership-blocker` is the live Phase 14 blocker: the review-only packet exists, but it still records explicit stay-in-C ownership rather than a parity or runtime-ownership transfer
- the previous absent-anchor wording is no longer truthful on current `master` and must not be used as a substitute for reading the returned bridge-local packet
- explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, segmentation metadata, and the final sock-owned tail transfer remains the Phase 14 boundary

## Boundary Reading
Against the Phase 14 roadmap, `net/core/skbuff.c` still belongs in a bounded `boundary_map_only`, review-first, freeze-in-C posture rather than a live parity claim.
Current `master` now ships a review-only skbuff bridge packet again, so this note should describe that live packet honestly instead of pretending the helper, manifest, focused gate, or Phase 14 build shard are absent.
The meaningful current statement is that the packet is present but still blocked on live ownership and packet-lifetime behavior that stays in C.
That deeper blocker remains the same Phase 14 seam: qdisc-facing publication, queue ownership, shared-info refcount and header-write ownership, checksum state, destructor and frag-list teardown, segmentation metadata, the final sock-owned tail transfer, `sock_wfree`, `tail->destructor`, `tail->sk`, tail->next splicing, and the consumer-side `tail = skb->prev` reset inside `validate_xmit_skb_list()` remain in C.
The live bridge packet therefore remains review-only boundary evidence, not a delivery, parity, or ownership-transfer claim.

## Compile Evidence
- current `master` exposes `zigux/tests/phase14_skbuff_bridge.zig`
- current `master` exposes `zigux/tests/phase14_build.zig`
- current `master` exposes `net/core/skbuff_bridge.zig`
- current `master` exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`
- `zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`
- that route is still evidence for a bounded boundary packet only; it must not be restated as a parity claim while `phase14-skbuff-live-ownership-blocker` stays open

## Gates
1. treat this note as a review-only boundary marker
   - it must keep the live packet presence explicit without overstating the packet as a status change, parity claim, or ownership transfer
2. keep the roadmap-facing `boundary_map_only` posture explicit
   - the survey must continue to name the retained live-ownership seam and stay-in-C decision while the bridge, manifest, focused gate, and build shard remain review-only evidence
3. keep the blocked consumer-tail contract explicit
   - `validate_xmit_skb_list()`, qdisc-facing publication, checksum ownership, segmentation metadata, destructor ordering, `sock_wfree`, `tail->destructor`, `tail->sk`, `tail->next`, `segs->prev`, `skb_mark_not_on_list()`, `tail = skb->prev`, and the final sock-owned tail transfer must remain named as C-owned review points
4. keep the live bridge-local packet aligned with the manifest and focused gate
   - if the bridge, dedicated test, manifest, or Phase 14 build shard drifts again, fix the directly coupled packet before widening into shared Phase 14 reminder surfaces

## Stay-In-C Guardrail
- manifest-backed guardrail: `phase14-skbuff-stay-in-c-guardrail` keeps this review-only packet fail-closed until the same packet carries explicit reopen evidence instead of lighter bridge-presence wording
- machine-check surface: `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` keeps the dedicated note fail-closed on its lane key, blocked gap, review-only posture, live-packet wording, and required stay-in-C evidence
- rollback owner: `Repo Tooling Pod`
- required evidence before any status review:
  - `Architecture Council` reopen record linked from the active skbuff packet
  - parity scorecard evidence and benchmark notes attached to the same skbuff packet
  - validation replay command and evidence archive path recorded beside the latest blocker disposition
- automatic return-to-blocked triggers:
  - any `net/core/skbuff_bridge.zig` claim or status review that drops `phase14-skbuff-live-ownership-blocker`
  - missing qdisc-facing publication, checksum ownership, segmentation metadata, destructor ordering, or final sock-owned tail transfer wording in the active skbuff packet
  - any bridge-presence wording that upgrades the packet into parity, runtime ownership, or a freeze-map status change without the required reopen evidence

## Next bounded step
Leave this lane parked unless a future current-`master` reread finds another survey-only drift against the live skbuff bridge packet or the Phase 14 roadmap.
If it reopens, first compare this note with `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, and `zigux/tests/phase14_build.zig`, then keep the repair inside this survey note only unless those directly coupled surfaces prove the wording stale again.
If the packet ever moves toward status review, update this note and `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` together before any broader shared Phase 14 reminder surface repeats the claim.
