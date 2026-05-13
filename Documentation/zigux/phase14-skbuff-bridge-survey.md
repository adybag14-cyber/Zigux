# Phase 14 Skbuff Bridge Survey

This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status

- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- explicit stay-in-C wording for `segs->prev`, `tail->next`, and `validate_xmit_skb_list()`
- explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, and destructor coordination remain in C

## Boundary Reading

The current anchor packet is review-only. It keeps the boundary-map helper in `net/core/skbuff_bridge.zig`, the focused survey gate in `zigux/tests/phase14_skbuff_bridge.zig`, and the manifest in `zigux/tests/phase14_skbuff_bridge_manifest.json` aligned with the shared Phase 14 smoke packet.

The skbuff lane stays parked at the live ownership blocker because shared-info refcounts, destructor teardown, checksum state, segmentation metadata, and exported tail publication still belong to the C implementation.

After the roadmap-alignment helper and the exported-tail checkpoint, no smaller review-only skbuff follow-up remains before the live ownership blocker.
