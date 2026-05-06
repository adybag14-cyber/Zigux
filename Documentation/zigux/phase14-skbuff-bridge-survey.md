# Phase 14 Skbuff Bridge Survey

This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SURVEYED_COMMIT=f05e02445443e7743c3675a6f8ca4f70f6e736fb`
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_SLICE=skbuff-boundary-map-tail-publication-followup`
- scope: the landed `net/core/skbuff_bridge.zig` boundary map plus its expanded lifetime audit outline and concurrency-sensitive checkpoint catalog, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
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

The highest-value honest step in this lane is therefore to add a boundary map that names the allocation, clone, mutation, checksum, segmentation, refcount, and teardown seams while explicitly keeping the refcounted lifetime and concurrency core in C.

## Survey findings

- `net/core/skbuff.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `include/linux/skbuff.h` makes the coupling visible: `struct skb_shared_info`, the split `dataref`, header-clone rules, `destructor_arg`, checksum metadata, and GSO fields show exactly why this lane needs explicit stay-in-C decisions before implementation claims.
- `net/core/datagram.c` is a useful nearby consumer because it still relies on the shipped skbuff lifetime model rather than any alternate wrapper surface.
- the new `net/core/skbuff_bridge.zig` starter stays intentionally narrow around boundary recording for allocation entrypoints, clone and copy seams, headroom mutation, checksum or segmentation surfaces, shared-info refcount ownership, and destructor or free-path ownership.
- the bridge now carries an explicit review-only concurrency-sensitive checkpoint catalog around the partial-tail-owner, checksum-to-data-offset, and exported tail-publication checkpoints inside `skb_segment()`, so the packet satisfies the roadmap's concurrency-audit requirement without claiming live ownership of skbuff lifetime, qdisc publication, or checksum state.
- the bridge now keeps checksum-complete state around `__skb_checksum_complete()` and `skb_checksum_complete_unset()` separate from the segmentation study, which keeps the ownership boundary around `skb->csum`, `skb->ip_summed`, `skb->csum_valid`, and `skb->csum_complete_sw` explicit without claiming live checksum-state control.
- the bridge now records the orphan-frag and zerocopy handoff inside `skb_segment()`, keeping `skb_orphan_frags()`, `skb_zerocopy_clone()`, `SKBFL_SHARED_FRAG`, and the carried fragment state visible while still keeping live payload ownership in C.
- the bridge now records the checksum-metadata handoff inside `skb_segment()`, keeping `CHECKSUM_NONE`, `skb_checksum()`, `SKB_GSO_CB(nskb)->csum`, and `SKB_GSO_CB(nskb)->csum_start` visible while still keeping live checksum and GSO ownership in C.
- the bridge now records the partial-seg metadata and tail-owner follow-up around `SKB_GSO_PARTIAL`, `SKB_GSO_DODGY`, `SKB_GSO_CB(iter)->data_offset`, the last-segment `gso_size` or `gso_segs` clamp, and the `sock_wfree` tail transfer so the lane names where GSO metadata and sock-owned backpressure state move while still keeping live packet shaping in C.
- the bridge now records the checksum-to-data-offset crossover inside `skb_segment()`, keeping `SKB_GSO_CB(nskb)->csum`, `SKB_GSO_CB(nskb)->csum_start`, `SKB_GSO_CB(iter)->data_offset`, and `remcsum_offload` visible in one review-only checkpoint so the lane names the remaining checksum metadata coupling while still keeping live packet shaping in C.
- the bridge now records the exported tail-list publication contract inside `skb_segment()`, keeping `segs->prev`, `tail->next`, the last-segment `gso_size` or `gso_segs` clamp, and the nearby `validate_xmit_skb_list()` consumer contract visible in one review-only checkpoint so the lane names the qdisc-facing handoff while still keeping live packet shaping in C.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-skbuff-boundary-map-starter`
- landed `phase14-skbuff-test-gate`
- landed `phase14-skbuff-slice-note`
- landed `phase14-skbuff-survey-note`
- landed `phase14-skbuff-concurrency-audit-outline`
- landed `phase14-skbuff-checksum-state-audit`
- landed `phase14-skbuff-segmentation-followup`
- landed `phase14-skbuff-segmentation-tail-owner-followup`
- landed `phase14-skbuff-segmentation-csum-data-offset-followup`
- landed `phase14-skbuff-segs-prev-tail-publication-followup`
- blocked `phase14-skbuff-live-ownership-blocker`

This keeps the lane explicit without overstating progress: Zigux now has a real Phase 14 skbuff boundary map, a lifetime-audit foothold, an explicit concurrency-sensitive checkpoint catalog for the qdisc-facing tail-publication boundary, an explicit checksum-state audit, the orphan-frag and zerocopy handoff study, the checksum-metadata handoff study, the partial-seg tail-owner follow-up, the checksum-to-data-offset crossover audit, and the exported tail-publication audit, but it still does not claim live refcount transitions, destructor ordering, checksum ownership, qdisc-facing publication ownership, segmentation behavior, or a direct `net/core/skbuff.c` rewrite.

## Freeze-in-C guardrails

- named owner: `Core-Adjacent Pod`
- status bucket: `freeze_in_c`
- validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all` plus `make -C zigux phase14`
- rollback owner: `Repo Tooling Pod`
- rollback threshold: keep this packet in `freeze_in_c` posture and return it to blocked skbuff-packet maintenance if the validation gate, rollback owner, blocked live-ownership gap, or explicit stay-in-C wording around qdisc-facing publication stops being visible in the same survey packet.
- required evidence:
  - explicit stay-in-C wording for `segs->prev`, `tail->next`, and `validate_xmit_skb_list()`
  - the blocked `phase14-skbuff-live-ownership-blocker` kept visible beside the no-smaller-follow-up posture
  - explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, and destructor coordination remain in C
- automatic return-to-blocked triggers:
  - any edit that drops the named validation gate or rollback owner
  - missing freeze-in-C or stay-in-C wording for the exported tail-publication checkpoint
  - any manifest refresh that changes the blocked live-ownership gap without refreshing this survey note
  - any edit that weakens the explicit no-smaller-follow-up stance and silently implies a fresh skbuff wrapper step

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

Keep the Phase 14 skbuff lane parked unless the packet drifts or stronger stay-in-C evidence changes the freeze posture. After the exported-tail checkpoint, no smaller review-only skbuff follow-up remains before the live ownership blocker.
