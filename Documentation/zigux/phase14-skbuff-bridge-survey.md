# Phase 14 Skbuff Bridge Survey

This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=skbuff-boundary-map-starter`
- scope: the landed `net/core/skbuff_bridge.zig` boundary map plus its initial lifetime audit outline, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
- product boundary:
  - `net/core/skbuff_bridge.zig`
  - `zigux/tests/phase14_skbuff_bridge.zig`
  - `zigux/tests/phase14_skbuff_bridge_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-skbuff-bridge-slice.md`
  - `Documentation/zigux/phase14-skbuff-bridge-survey.md`

## Why this slice exists

The Phase 14 roadmap explicitly names `net/core/skbuff.c` as a boundary-study target and the freeze map also lists it as a current stay-in-C anchor. That means the right first move is not a pretend port. It is a reviewable bridge that makes the ownership boundaries visible.

That matters because the live `net/core/skbuff.c` anchor is already 7,476 lines, `include/linux/skbuff.h` adds another 5,467 lines of shared metadata and inline rules, and even a nearby `net/core/datagram.c` user still depends on the existing skb lifetime model. The file mixes allocation, clone or copy helpers, headroom mutation, copy and checksum helpers, checksum completion, GSO segmentation, destructor callbacks, frag ownership, and final consume or free paths.

The highest-value honest step in this lane is therefore to add a boundary map that names the allocation, clone, mutation, checksum, segmentation, refcount, and teardown seams while explicitly keeping the refcounted lifetime core in C.

## Survey findings

- `net/core/skbuff.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `include/linux/skbuff.h` makes the coupling visible: `struct skb_shared_info`, the split `dataref`, header-clone rules, `destructor_arg`, checksum metadata, and GSO fields show exactly why this lane needs explicit stay-in-C decisions before implementation claims.
- `net/core/datagram.c` is a useful nearby consumer because it still relies on the shipped skbuff lifetime model rather than any alternate wrapper surface.
- the new `net/core/skbuff_bridge.zig` starter stays intentionally narrow around boundary recording for allocation entrypoints, clone and copy seams, headroom mutation, checksum or segmentation surfaces, shared-info refcount ownership, and destructor or free-path ownership.
- the bridge now keeps checksum-complete state around `__skb_checksum_complete()` and `skb_checksum_complete_unset()` separate from the segmentation study, which keeps the ownership boundary around `skb->csum`, `skb->ip_summed`, `skb->csum_valid`, and `skb->csum_complete_sw` explicit without claiming live checksum-state control.
- the bridge now makes the first segmentation-handoff study explicit around `skb_segment()`, `skb_orphan_frags()`, `skb_zerocopy_clone()`, `SKBFL_SHARED_FRAG`, `nskb->ip_summed`, and `SKB_GSO_CB(nskb)` so the lane names where frag ownership and checksum metadata move while still keeping live packet shaping in C.
- the next honest skbuff-facing step is the smaller `skb_segment()` tail-owner follow-up around `SKB_GSO_PARTIAL`, `SKB_GSO_DODGY`, `SKB_GSO_CB(iter)->data_offset`, and the `sock_wfree` tail transfer so the lane records the remaining partial-seg metadata path before any wrapper claim approaches live packet lifetime behavior.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-skbuff-boundary-map-starter`
- landed `phase14-skbuff-test-gate`
- landed `phase14-skbuff-slice-note`
- landed `phase14-skbuff-survey-note`
- landed `phase14-skbuff-lifetime-audit-outline`
- landed `phase14-skbuff-checksum-state-audit`
- landed `phase14-skbuff-segmentation-followup`
- ready-next `phase14-skbuff-segmentation-tail-owner-followup`
- blocked `phase14-skbuff-live-ownership-blocker`

This keeps the lane explicit without overstating progress: Zigux now has a real Phase 14 skbuff boundary map, a lifetime-audit foothold, an explicit checksum-state audit, and the first segmentation-handoff study, but it still does not claim live refcount transitions, destructor ordering, checksum ownership, segmentation behavior, or a direct `net/core/skbuff.c` rewrite.

## Non-goals

This survey slice does not claim:

- allocator implementation or cache ownership
- live `dataref` transitions
- header-write eligibility logic
- destructor callbacks or frag teardown
- checksum completion ownership
- GSO segmentation behavior
- a direct `net/core/skbuff.c` port

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Stay in the Phase 14 skbuff lane and add one tiny `skb_segment()` tail-owner follow-up next, limited to `SKB_GSO_PARTIAL`, `SKB_GSO_DODGY`, `SKB_GSO_CB(iter)->data_offset`, and the `sock_wfree` transfer so the bridge records the remaining partial-seg metadata path before any wrapper leaves the current boundary-map-only posture.
