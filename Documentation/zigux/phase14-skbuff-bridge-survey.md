# Phase 14 Skbuff Bridge Survey

This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status

- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- explicit stay-in-C wording for `sock_wfree`, `tail->destructor`, `tail->sk`, `segs->prev`, `tail->next`, `validate_xmit_skb_list()`, `skb_mark_not_on_list()`, and `tail = skb->prev`
- explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, and the final sock-owned tail transfer remain in C
- compile evidence remains `full_bundle_only` through `phase14-skbuff-bridge-tests`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14-test`

## Boundary Reading

The current anchor packet is review-only. It keeps the boundary-map helper in `net/core/skbuff_bridge.zig`, the focused survey gate in `zigux/tests/phase14_skbuff_bridge.zig`, and the manifest in `zigux/tests/phase14_skbuff_bridge_manifest.json` aligned with the shared Phase 14 smoke packet.

The skbuff lane stays parked at the live ownership blocker because shared-info refcounts, destructor teardown, checksum state, segmentation metadata, the final sock-owned tail transfer, exported tail publication, and the consumer-side list reset inside `validate_xmit_skb_list()` still belong to the C implementation.

After the roadmap-alignment helper and the exported-tail checkpoint, no smaller review-only skbuff follow-up remains before the live ownership blocker.

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

Leave this lane parked unless `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `net/core/skbuff_bridge.zig`, or this note drift again on the full-bundle-only compile evidence or the blocked stay-in-C ownership wording.
