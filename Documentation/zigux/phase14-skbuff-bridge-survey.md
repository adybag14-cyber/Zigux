# Phase 14 Skbuff Bridge Survey

This document records the bounded Phase 14 survey lane around `net/core/skbuff.c`.

## Status

- `PHASE14_LANE_KEY=P14-L12`
- `PHASE14_STATUS=active`
- `PHASE14_SLICE=skbuff-direct-xmit-identity-drop`
- `PHASE14_SURVEYED_COMMIT=02264a3240cd30ce45c9a932047a0204b7ab5029`
- survey provenance captured against verified `master` head `02264a3240cd30ce45c9a932047a0204b7ab5029`
- scope: the landed `net/core/skbuff_bridge.zig` boundary map plus its expanded lifetime audit outline, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
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
- the bridge now records the partial-seg metadata and tail-owner follow-up around `SKB_GSO_PARTIAL`, `SKB_GSO_DODGY`, `SKB_GSO_CB(iter)->data_offset`, the last-segment `gso_size` or `gso_segs` clamp, and the `sock_wfree` tail transfer so the lane names where GSO metadata and sock-owned backpressure state move while still keeping live packet shaping in C.
- the bridge now records the checksum-to-data-offset crossover inside `skb_segment()`, keeping `SKB_GSO_CB(nskb)->csum`, `SKB_GSO_CB(nskb)->csum_start`, `SKB_GSO_CB(iter)->data_offset`, and `remcsum_offload` visible in one review-only checkpoint so the lane names the remaining checksum metadata coupling while still keeping live packet shaping in C.
- the bridge now records the exported tail-publication contract around `segs->prev`, the last-segment `gso_size` or `gso_segs` clamp, `tail->next`, and the nearby `validate_xmit_skb_list()` handoff so the lane names where segmented output becomes a published list without weakening the stay-in-C posture.
- the bridge now records the `validate_xmit_skb_list()` consumer-side reset around `next = skb->next`, `skb_mark_not_on_list()`, `skb->prev = skb`, and `tail = skb->prev` so the lane names how single-skb and segmented outputs converge on one tail contract without weakening the stay-in-C posture.
- the bridge now records the smaller `validate_xmit_skb_list()` republish handoff around `head = skb`, `tail->next = skb`, and `validate_xmit_skb()` drop pruning so the lane records how validated outputs are stitched back into one list before any wrapper claim approaches live packet lifetime behavior.
- the packet now records a dedicated stay-in-C governance note for the direct `__dev_direct_xmit()` identity-drop checkpoint, keeping `skb = validate_xmit_skb_list(...)`, `skb != orig_skb`, and the drop path explicitly observational-only while qdisc publication, queue ownership, and skb lifetime ownership remain in C.
- the bridge now records the narrower `__dev_direct_xmit()` identity-drop follow-up around `skb = validate_xmit_skb_list(...)`, `skb != orig_skb`, and the drop path, and that checkpoint stays strictly observational: it does not move qdisc publication, queue ownership, or skb lifetime ownership out of the existing C implementation.

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
- landed `phase14-skbuff-segmentation-tail-owner-followup`
- landed `phase14-skbuff-segmentation-csum-data-offset-followup`
- landed `phase14-skbuff-segs-prev-tail-publication-followup`
- landed `phase14-skbuff-validate-xmit-list-reset-followup`
- landed `phase14-skbuff-validate-xmit-republish-followup`
- landed `phase14-skbuff-direct-xmit-governance-note`
- landed `phase14-skbuff-direct-xmit-identity-drop-followup`
- blocked `phase14-skbuff-live-ownership-blocker`

This keeps the lane explicit without overstating progress: Zigux now has a real Phase 14 skbuff boundary map, a lifetime-audit foothold, an explicit checksum-state audit, the first segmentation-handoff study, the partial-seg tail-owner follow-up, the checksum-to-data-offset crossover audit, the exported tail-publication checkpoint, the consumer-side `validate_xmit_skb_list()` reset checkpoint, the republish handoff that stitches validated outputs back into one list, and the direct `__dev_direct_xmit()` identity-drop checkpoint itself, but it still does not claim live refcount transitions, destructor ordering, checksum ownership, segmentation behavior, qdisc publication ownership, or a direct `net/core/skbuff.c` rewrite.

## Freeze-in-C guardrails

- named owner: `Core-Adjacent Pod`
- status bucket: `freeze_in_c`
- validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all` plus `make -C zigux phase14`
- rollback owner: `Repo Tooling Pod`
- rollback threshold: keep this packet in `freeze_in_c` posture and return it to blocked skbuff-packet maintenance if the validation gate, rollback owner, no-ready-next posture, or the stay-in-C wording around the republish and direct-xmit checkpoints stops being explicit.
- fallback path: Keep `net/core/skbuff.c` as the source of truth, keep `net/core/skbuff_bridge.zig` boundary-map-only, and fall back to blocked skbuff-packet maintenance if the stay-in-C or rollback contract stops being explicit.
- required evidence:
  - named owner, validation gate, and rollback owner recorded together in this survey note
  - explicit stay-in-C wording for `head = skb`, `tail->next = skb`, `validate_xmit_skb()`, `skb = validate_xmit_skb_list(...)`, `skb != orig_skb`, and the `__dev_direct_xmit()` identity-drop checkpoint
  - the landed direct-xmit identity-drop checkpoint and the blocked live-ownership gap kept explicit beside the same freeze-in-C posture
  - explicit wording that the identity-drop checkpoint is observational only and does not transfer qdisc publication, queue ownership, or skb lifetime ownership out of C
  - the same no-ready-next posture for the republish and direct-xmit checkpoints kept explicit across this survey note and `Documentation/zigux/phase14-skbuff-bridge-slice.md`
- automatic return-to-blocked triggers:
  - any edit that drops the named validation gate or rollback owner
  - missing freeze-in-C or stay-in-C wording for the republish or direct-xmit handoff in this survey packet
  - any manifest refresh that changes the landed direct-xmit checkpoint or blocked gap without refreshing this survey note
  - any edit that stops distinguishing the observational `__dev_direct_xmit()` identity-drop checkpoint from the still-blocked qdisc publication, queue ownership, or skb lifetime ownership
  - any change that silently restores a ready-next claim or narrows the packet past observational-only wording without refreshing the bridge, manifest, and note set together

## Rollback threshold for observational checkpoints

This run tightens one narrower guardrail without reopening the bridge.

- current packet posture for both the `validate_xmit_skb_list()` republish checkpoint and the `__dev_direct_xmit()` identity-drop checkpoint remains `freeze_in_c` even though the survey lane stays active for reviewability maintenance.
- the smallest evidence packet that keeps those checkpoints honest is still the existing bridge, manifest-backed survey, slice note, and this survey note, all agreeing that `head = skb`, `tail->next = skb`, `validate_xmit_skb()`, `skb = validate_xmit_skb_list(...)`, `skb != orig_skb`, qdisc publication, queue ownership, and skb lifetime ownership stay explicitly in C.
- if a future run wants to reopen a narrower follow-up, it must refresh that whole packet together. A note-only change that weakens the observational-only wording or silently reintroduces a new ready-next claim is not an acceptable bridge step.
- if any of those cues drift, the lane should fall straight back to blocked skbuff-packet maintenance instead of claiming forward motion on transmit-list ownership.

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

Keep this lane parked unless the skbuff survey packet drifts again or another narrower same-family audit becomes explicit without weakening the stay-in-C posture. The landed `__dev_direct_xmit()` identity-drop checkpoint stays observational only, qdisc publication, queue ownership, and skb lifetime ownership remain explicitly in C, and any future packet repair that loses the shared no-ready-next posture should be treated as rollback-to-maintenance work rather than as a new bridge opening.
