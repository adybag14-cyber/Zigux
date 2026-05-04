# Phase 14 Skbuff Bridge Slice

This bounded Phase 14 slice keeps `net/core/skbuff_bridge.zig` as a pure boundary map anchored to `net/core/skbuff.c`.

The current bridge stays intentionally narrow:

- records the main allocation entrypoints around `__alloc_skb()`, `napi_alloc_skb()`, and `build_skb()` without claiming allocator ownership
- records clone and private-copy seams around `skb_clone()`, `skb_copy()`, and `__pskb_copy_fclone()` as future wrapper candidates only
- records headroom growth and in-header carve paths around `pskb_expand_head()`, `skb_copy_expand()`, and `pskb_carve_inside_header()` without claiming live mutation ownership
- records checksum and segmentation surfaces around `__skb_checksum_complete()` and `skb_segment()` as metadata-heavy boundaries only
- marks `skb_shared_info.dataref`, `skb_header_cloned()`, and the shared header-write rules as explicit stay-in-C decisions
- marks `skb_release_head_state()`, `skb_release_data()`, and `consume_skb()` as explicit stay-in-C decisions tied to destructor callbacks and frag-list teardown
- adds a twelve-checkpoint lifetime audit outline that names dataref splits, clone-before-expand mutation, destructor ordering, checksum-complete state caching, segmentation orphan-frag or zerocopy handoff, segmentation checksum-metadata handoff, the partial-GSO tail-owner transfer, the checksum-to-data-offset crossover, the exported tail-publication contract, the `validate_xmit_skb_list()` consumer-side list reset, the `head = skb` or `tail->next = skb` republish stitchback after `validate_xmit_skb()` drop pruning, and the observational `__dev_direct_xmit()` identity-drop checkpoint while keeping all live ownership in C
- adds a four-checkpoint concurrency audit outline that names the BH-local NAPI page-frag allocator lock, the per-CPU skb head-cache refill, the drop-reason RCU publication path, and the remote-CPU defer-free handoff while keeping allocator concurrency, RCU publication ordering, and deferred-free execution in C

This slice still does not claim live allocation, refcount transitions, header-write eligibility, destructor callbacks, frag-list teardown, checksum completion, segmentation behavior, qdisc publication ownership, queue ownership, skb lifetime ownership, or a direct `net/core/skbuff.c` rewrite.

The bridge packet also now records both the dedicated direct-xmit governance note and the landed `__dev_direct_xmit()` identity-drop checkpoint: `skb = validate_xmit_skb_list(...)`, `skb != orig_skb`, and the drop path stay observational only while qdisc publication, queue ownership, and skb lifetime ownership remain explicitly in C.

This slice is now parked at the direct-xmit identity-drop boundary. The landed checkpoint remains observational only, qdisc publication, queue ownership, and skb lifetime ownership stay explicitly in C unless a future narrower audit justifies another review-local same-family step. The skbuff-local concurrency checkpoints remain review-only too: the NAPI BH-local allocator lock, drop-reason RCU publication, and remote defer-free handoff are evidence surfaces, not bridge ownership claims.
