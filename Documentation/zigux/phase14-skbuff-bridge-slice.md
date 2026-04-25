# Phase 14 Skbuff Bridge Slice

This bounded Phase 14 slice starts `net/core/skbuff_bridge.zig` as a pure boundary map anchored to `net/core/skbuff.c`.

The current bridge stays intentionally narrow:

- records the main allocation entrypoints around `__alloc_skb()`, `napi_alloc_skb()`, and `build_skb()` without claiming allocator ownership
- records clone and private-copy seams around `skb_clone()`, `skb_copy()`, and `__pskb_copy_fclone()` as future wrapper candidates only
- records headroom growth and in-header carve paths around `pskb_expand_head()`, `skb_copy_expand()`, and `pskb_carve_inside_header()` without claiming live mutation ownership
- records checksum and segmentation surfaces around `__skb_checksum_complete()` and `skb_segment()` as metadata-heavy boundaries only
- marks `skb_shared_info.dataref`, `skb_header_cloned()`, and the shared header-write rules as explicit stay-in-C decisions
- marks `skb_release_head_state()`, `skb_release_data()`, and `consume_skb()` as explicit stay-in-C decisions tied to destructor callbacks and frag-list teardown
- adds a five-checkpoint lifetime audit outline that names dataref splits, clone-before-expand mutation, destructor ordering, checksum-complete state caching, and segmentation frag or checksum handoff while keeping all live ownership in C

This slice still does not claim live allocation, refcount transitions, header-write eligibility, destructor callbacks, frag-list teardown, checksum completion, segmentation behavior, or a direct `net/core/skbuff.c` rewrite.

The next honest bounded step in this same lane is to tighten the segmentation handoff study around `skb_segment()`, `skb_orphan_frags()`, and `skb_zerocopy_clone()` so the bridge records how frag ownership and checksum metadata move without weakening the current boundary-map-only posture.
