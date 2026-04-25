# Phase 14 Skbuff Bridge Slice

This bounded Phase 14 slice starts `net/core/skbuff_bridge.zig` as a pure boundary map anchored to `net/core/skbuff.c`.

The current bridge stays intentionally narrow:

- records the main allocation entrypoints around `__alloc_skb()`, `napi_alloc_skb()`, and `build_skb()` without claiming allocator ownership
- records clone and private-copy seams around `skb_clone()`, `skb_copy()`, and `__pskb_copy_fclone()` as future wrapper candidates only
- records headroom growth and in-header carve paths around `pskb_expand_head()`, `skb_copy_expand()`, and `pskb_carve_inside_header()` without claiming live mutation ownership
- records checksum and segmentation surfaces around `__skb_checksum_complete()` and `skb_segment()` as metadata-heavy boundaries only
- marks `skb_shared_info.dataref`, `skb_header_cloned()`, and the shared header-write rules as explicit stay-in-C decisions
- marks `skb_release_head_state()`, `skb_release_data()`, and `consume_skb()` as explicit stay-in-C decisions tied to destructor callbacks and frag-list teardown
- adds a four-checkpoint lifetime audit outline that names dataref splits, clone-before-expand mutation, destructor ordering, and checksum or GSO metadata coupling while keeping all live ownership in C

This slice still does not claim live allocation, refcount transitions, header-write eligibility, destructor callbacks, frag-list teardown, checksum completion, segmentation behavior, or a direct `net/core/skbuff.c` rewrite.

The next honest bounded step in this same lane is to tighten the lifetime audit around `pskb_expand_head()`, `skb_release_head_state()` or `skb_release_data()`, and `skb_segment()` so the bridge records clone-or-reallocate handoff, destructor-ordered teardown, and checksum or frag metadata ownership without weakening the current boundary-map-only posture.
