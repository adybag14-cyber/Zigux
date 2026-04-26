const std = @import("std");

pub const Ownership = enum {
    boundary_map_only,
    stay_in_c,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    posture: []const u8,
    provides_boundary_map: bool,
    provides_lifetime_audit_outline: bool,
    provides_stay_in_c_decisions: bool,
    touches_live_allocators: bool,
    touches_live_refcounts: bool,
    touches_live_destructors: bool,
};

pub const BoundaryArea = struct {
    id: []const u8,
    summary: []const u8,
    ownership: Ownership,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

pub const BoundaryMap = struct {
    anchor: []const u8,
    posture: []const u8,
    areas: []const BoundaryArea,
};

pub const AuditGuard = enum {
    header_write_requires_private_data,
    clone_or_reallocate_before_mutation,
    destructor_before_frag_release,
    checksum_complete_state_cache,
    segmentation_orphan_and_zerocopy_handoff,
    segmentation_checksum_metadata_handoff,
    segmentation_partial_tail_owner_transfer,
    segmentation_checksum_data_offset_crossover,
};

pub const AuditCheckpoint = struct {
    id: []const u8,
    anchor_symbol: []const u8,
    summary: []const u8,
    guard: AuditGuard,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
    ownership: Ownership,
};

pub const LifetimeAudit = struct {
    anchor: []const u8,
    posture: []const u8,
    checkpoints: []const AuditCheckpoint,
    blocked_live_behaviors: []const []const u8,
    next_step: []const u8,
};

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "allocation-entrypoints",
        .summary = "Record the main skb allocation entrypoints without claiming allocator or cache ownership.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_skb", "napi_alloc_skb", "build_skb" },
        .rationale = "The first honest skbuff foothold is to name where callers enter the allocation surface, while leaving the slab, page-frag, NAPI, and truesize accounting machinery in C.",
    },
    .{
        .id = "clone-and-private-copy",
        .summary = "Map clone and private-copy helpers as reviewable wrapper candidates only.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "skb_clone", "skb_copy", "__pskb_copy_fclone" },
        .rationale = "Clone and copy entrypoints are visible seams for future wrapper discussion, but the real behavior still depends on skb_shared_info.dataref, headerless skb rules, and frag ownership that should remain in C.",
    },
    .{
        .id = "headroom-and-linearization-mutation",
        .summary = "Capture headroom growth and in-header carve paths as mutation seams, not live rewrite candidates.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "pskb_expand_head", "skb_copy_expand", "pskb_carve_inside_header" },
        .rationale = "These helpers mutate skb geometry and copy state across shared heads, so Phase 14 should record their boundary without pretending Zig now owns the mutation path.",
    },
    .{
        .id = "checksum-and-segmentation-surface",
        .summary = "Document checksum completion and segmentation as metadata-heavy boundaries before any wrapper claim touches them.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__skb_checksum_complete", "skb_segment" },
        .rationale = "Checksum and segmentation are caller-visible surfaces, but they are tightly coupled to csum metadata, frag layout, and GSO bookkeeping that should stay in the existing C implementation for now.",
    },
    .{
        .id = "shared-info-refcount-ownership",
        .summary = "Keep skb_shared_info refcount splits and header-write eligibility explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "struct skb_shared_info", "dataref", "skb_header_cloned" },
        .rationale = "The split dataref model and header-clone rules decide whether headers may be mutated at all, so they are core ownership logic rather than a safe Phase 14 wrapper target.",
    },
    .{
        .id = "destructor-and-free-path",
        .summary = "Keep destructor callbacks and final release ordering explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "skb_release_head_state", "skb_release_data", "consume_skb" },
        .rationale = "Teardown crosses destructor callbacks, destructor_arg payloads, frag lists, and final consume or free paths, which is exactly the kind of lifetime ownership Phase 14 should record and leave in C.",
    },
};

const audit_checkpoints = [_]AuditCheckpoint{
    .{
        .id = "dataref-header-write-split",
        .anchor_symbol = "skb_cloned/skb_header_cloned",
        .summary = "Record that header writes are blocked until shared-data ownership collapses to a private head.",
        .guard = .header_write_requires_private_data,
        .observed_fields = &[_][]const u8{ "skb->cloned", "skb_shinfo(skb)->dataref", "skb->hdr_len" },
        .blocked_by = "The split dataref model and headerless skb rules decide whether the header may be written at all, so Zigux should audit that ownership boundary rather than claim a live clone or mutate wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "clone-before-expand-mutation",
        .anchor_symbol = "pskb_expand_head",
        .summary = "Track the clone-or-reallocate handoff before headroom mutation touches shared data.",
        .guard = .clone_or_reallocate_before_mutation,
        .observed_fields = &[_][]const u8{ "skb->cloned", "skb_shinfo(skb)->dataref", "skb_shinfo(skb)->frag_list" },
        .blocked_by = "pskb_expand_head() conditionally clones frag lists, releases old shared data, and rewrites skb geometry, so Phase 14 should keep the mutation handoff in C while only naming the checkpoint.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "destructor-before-data-release",
        .anchor_symbol = "skb_release_head_state/skb_release_data",
        .summary = "Capture destructor callbacks and frag-list release ordering before final consume or free paths run.",
        .guard = .destructor_before_frag_release,
        .observed_fields = &[_][]const u8{ "skb->destructor", "skb_shinfo(skb)->destructor_arg", "skb_shinfo(skb)->frag_list" },
        .blocked_by = "The release path can run destructor callbacks, detach socket state, and then free frags or frag lists, so Zigux should keep that teardown ordering in C rather than pretend it already owns skb lifetime.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "checksum-complete-state-cache",
        .anchor_symbol = "__skb_checksum_complete/skb_checksum_complete_unset",
        .summary = "Keep checksum-complete caching and invalidation tied to skb-owned state fields.",
        .guard = .checksum_complete_state_cache,
        .observed_fields = &[_][]const u8{ "skb->csum", "skb->ip_summed", "skb->csum_valid", "skb->csum_complete_sw" },
        .blocked_by = "__skb_checksum_complete() stores checksum state back into the skb when it is not shared, and skb_checksum_complete_unset() invalidates that cache after packet mutation, so Zigux should record the ownership boundary without claiming live checksum-state control.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-orphan-and-zerocopy-handoff",
        .anchor_symbol = "skb_segment/skb_orphan_frags/skb_zerocopy_clone",
        .summary = "Track the orphan-frag gate and zerocopy carryover before segmented outputs reuse page-backed payload state.",
        .guard = .segmentation_orphan_and_zerocopy_handoff,
        .observed_fields = &[_][]const u8{ "skb_shinfo(head_skb)->frag_list", "skb_shinfo(head_skb)->flags", "skb_shinfo(nskb)->flags", "skb_shinfo(nskb)->nr_frags" },
        .blocked_by = "skb_segment() first forces skb_orphan_frags(head_skb, GFP_ATOMIC) for zerocopy-backed input, then propagates SKBFL_SHARED_FRAG state and calls skb_zerocopy_clone() across frag_skb and frag_list members, so Zigux should keep that frag-ownership transfer in C while only naming the boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-checksum-metadata-handoff",
        .anchor_symbol = "skb_segment/SKB_GSO_CB",
        .summary = "Record where segmented outputs reset or recompute checksum metadata as GSO state moves onto each new skb.",
        .guard = .segmentation_checksum_metadata_handoff,
        .observed_fields = &[_][]const u8{ "nskb->remcsum_offload", "nskb->ip_summed", "SKB_GSO_CB(nskb)->csum", "SKB_GSO_CB(nskb)->csum_start", "skb_shinfo(head_skb)->gso_size" },
        .blocked_by = "skb_segment() can clear ip_summed to CHECKSUM_NONE, copy checksum bytes through skb_copy_and_csum_bits(), or recompute checksum state through skb_checksum() before it seeds SKB_GSO_CB(nskb), so Zigux should keep checksum and GSO metadata ownership in C while only recording the handoff.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-partial-tail-owner-transfer",
        .anchor_symbol = "skb_segment/SKB_GSO_PARTIAL/sock_wfree",
        .summary = "Track partial-GSO metadata rewrites and the final sock-owned tail transfer before segmented output ownership leaves the bridge study boundary.",
        .guard = .segmentation_partial_tail_owner_transfer,
        .observed_fields = &[_][]const u8{
            "skb_shinfo(iter)->gso_size",
            "skb_shinfo(iter)->gso_segs",
            "skb_shinfo(iter)->gso_type",
            "SKB_GSO_CB(iter)->data_offset",
            "tail->truesize",
            "tail->destructor",
            "tail->sk",
        },
        .blocked_by = "skb_segment() promotes NETIF_F_GSO_PARTIAL into SKB_GSO_PARTIAL, clears SKB_GSO_DODGY, rewrites each segment's gso_size, gso_segs, gso_type, and SKB_GSO_CB(iter)->data_offset, then transfers sock-owned backpressure state by swapping the tail skb truesize, destructor, and sk with head_skb when head_skb->destructor == sock_wfree, so Zigux should keep both the partial-seg metadata path and the tail-owner transfer in C while only naming the handoff.",
        .ownership = .stay_in_c,
    },
    {
