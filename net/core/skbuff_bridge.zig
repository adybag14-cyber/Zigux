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
    segmentation_tail_publication_contract,
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
    .{
        .id = "segmentation-checksum-data-offset-crossover",
        .anchor_symbol = "skb_segment/SKB_GSO_CB/remcsum_offload",
        .summary = "Track the checksum-to-data-offset crossover that seeds each output skb before later tail publication.",
        .guard = .segmentation_checksum_data_offset_crossover,
        .observed_fields = &[_][]const u8{
            "SKB_GSO_CB(nskb)->csum",
            "SKB_GSO_CB(nskb)->csum_start",
            "SKB_GSO_CB(iter)->data_offset",
            "remcsum_offload",
            "segs->prev",
        },
        .blocked_by = "skb_segment() carries checksum state forward by seeding SKB_GSO_CB(nskb)->csum and SKB_GSO_CB(nskb)->csum_start, rewrites SKB_GSO_CB(iter)->data_offset as the remaining bytes shrink, and only later publishes the tail chain through segs->prev with remcsum_offload in play, so Zigux should keep this checksum-to-publication crossover in C while only recording the boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "segmentation-tail-publication-contract",
        .anchor_symbol = "skb_segment/segs->prev/validate_xmit_skb_list",
        .summary = "Record the exported tail-pointer contract between skb_segment() and validate_xmit_skb_list() before any wrapper claims list ownership.",
        .guard = .segmentation_tail_publication_contract,
        .observed_fields = &[_][]const u8{
            "segs->prev",
            "tail->next",
            "skb_shinfo(tail)->gso_size",
            "skb_shinfo(tail)->gso_segs",
            "skb->prev",
            "skb->next",
        },
        .blocked_by = "skb_segment() publishes the last generated skb through segs->prev, clamps the last segment's gso_size or gso_segs after the partial-seg loop, and then validate_xmit_skb_list() consumes that contract by resetting skb->prev for unsegmented skbs, splicing tail->next, and trusting tail = skb->prev, so Zigux should keep this exported tail-publication path in C while only naming the contract.",
        .ownership = .stay_in_c,
    },
};

const blocked_live_behaviors = [_][]const u8{
    "live skbuff allocation and cache ownership",
    "shared-data refcount transitions",
    "destructor callback and frag-list teardown",
    "checksum-complete state transitions",
    "segmentation orphan-frag and zerocopy ownership handoff",
    "segmentation checksum metadata recompute and GSO handoff",
    "segmentation partial-seg metadata and tail-owner transfer",
    "segmentation checksum and data-offset crossover before tail publication",
    "segmentation exported tail-publication contract",
};

pub const SkbuffBridgeLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "skbuff_boundary_map_lab",
            .anchor = "net/core/skbuff.c",
            .posture = "boundary_map_only",
            .provides_boundary_map = true,
            .provides_lifetime_audit_outline = true,
            .provides_stay_in_c_decisions = true,
            .touches_live_allocators = false,
            .touches_live_refcounts = false,
            .touches_live_destructors = false,
        };
    }

    pub fn boundaryMap() BoundaryMap {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .areas = boundary_areas[0..],
        };
    }

    pub fn lifetimeAudit() LifetimeAudit {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .checkpoints = audit_checkpoints[0..],
            .blocked_live_behaviors = blocked_live_behaviors[0..],
            .next_step = nextAuditFocus(),
        };
    }

    pub fn stayInCDecisionCount() usize {
        var count: usize = 0;
        for (boundary_areas) |area| {
            if (area.ownership == .stay_in_c) {
                count += 1;
            }
        }
        return count;
    }

    pub fn auditCheckpointCount() usize {
        return audit_checkpoints.len;
    }

    pub fn nextAuditFocus() []const u8 {
        return "Audit the validate_xmit_skb_list() single-skb fallback around skb_mark_not_on_list(), skb->prev = skb, and tail = skb->prev so the bridge records the consumer-side list reset that still keeps exported tail publication in C.";
    }
};

test "skbuff bridge descriptor stays boundary-map only" {
    const descriptor = SkbuffBridgeLab.descriptor();

    try std.testing.expectEqualStrings("skbuff_boundary_map_lab", descriptor.name);
    try std.testing.expectEqualStrings("net/core/skbuff.c", descriptor.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", descriptor.posture);
    try std.testing.expect(descriptor.provides_boundary_map);
    try std.testing.expect(descriptor.provides_lifetime_audit_outline);
    try std.testing.expect(descriptor.provides_stay_in_c_decisions);
    try std.testing.expect(!descriptor.touches_live_allocators);
    try std.testing.expect(!descriptor.touches_live_refcounts);
    try std.testing.expect(!descriptor.touches_live_destructors);
}

test "skbuff bridge boundary map records stay-in-c lifetime decisions" {
    const map = SkbuffBridgeLab.boundaryMap();

    try std.testing.expectEqualStrings("net/core/skbuff.c", map.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", map.posture);
    try std.testing.expectEqual(@as(usize, 6), map.areas.len);
    try std.testing.expectEqual(@as(usize, 2), SkbuffBridgeLab.stayInCDecisionCount());
    try std.testing.expect(std.mem.indexOf(u8, SkbuffBridgeLab.nextAuditFocus(), "skb_mark_not_on_list()") != null);
    try std.testing.expect(std.mem.indexOf(u8, SkbuffBridgeLab.nextAuditFocus(), "tail = skb->prev") != null);

    try std.testing.expectEqualStrings("allocation-entrypoints", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("__alloc_skb", map.areas[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("napi_alloc_skb", map.areas[0].anchor_symbols[1]);

    try std.testing.expectEqualStrings("shared-info-refcount-ownership", map.areas[4].id);
    try std.testing.expect(map.areas[4].ownership == .stay_in_c);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[4].rationale, "dataref") != null);

    try std.testing.expectEqualStrings("destructor-and-free-path", map.areas[5].id);
    try std.testing.expect(map.areas[5].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("consume_skb", map.areas[5].anchor_symbols[2]);
}

test "skbuff bridge lifetime audit stays review-only" {
    const audit = SkbuffBridgeLab.lifetimeAudit();

    try std.testing.expectEqualStrings("net/core/skbuff.c", audit.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", audit.posture);
    try std.testing.expectEqual(@as(usize, 9), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 9), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 9), SkbuffBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "skb_mark_not_on_list()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "tail = skb->prev") != null);

    try std.testing.expectEqualStrings("dataref-header-write-split", audit.checkpoints[0].id);
    try std.testing.expect(audit.checkpoints[0].guard == .header_write_requires_private_data);
    try std.testing.expectEqualStrings("skb->hdr_len", audit.checkpoints[0].observed_fields[2]);

    try std.testing.expectEqualStrings("clone-before-expand-mutation", audit.checkpoints[1].id);
    try std.testing.expect(audit.checkpoints[1].guard == .clone_or_reallocate_before_mutation);
    try std.testing.expectEqualStrings("skb_shinfo(skb)->frag_list", audit.checkpoints[1].observed_fields[2]);

    try std.testing.expectEqualStrings("destructor-before-data-release", audit.checkpoints[2].id);
    try std.testing.expect(audit.checkpoints[2].guard == .destructor_before_frag_release);
    try std.testing.expectEqualStrings("skb_shinfo(skb)->destructor_arg", audit.checkpoints[2].observed_fields[1]);

    try std.testing.expectEqualStrings("checksum-complete-state-cache", audit.checkpoints[3].id);
    try std.testing.expect(audit.checkpoints[3].guard == .checksum_complete_state_cache);
    try std.testing.expectEqualStrings("skb->csum_complete_sw", audit.checkpoints[3].observed_fields[3]);

    try std.testing.expectEqualStrings("segmentation-orphan-and-zerocopy-handoff", audit.checkpoints[4].id);
    try std.testing.expect(audit.checkpoints[4].guard == .segmentation_orphan_and_zerocopy_handoff);
    try std.testing.expectEqualStrings("skb_shinfo(nskb)->nr_frags", audit.checkpoints[4].observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[4].blocked_by, "skb_orphan_frags(head_skb, GFP_ATOMIC)") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[4].blocked_by, "SKBFL_SHARED_FRAG") != null);

    try std.testing.expectEqualStrings("segmentation-checksum-metadata-handoff", audit.checkpoints[5].id);
    try std.testing.expect(audit.checkpoints[5].guard == .segmentation_checksum_metadata_handoff);
    try std.testing.expectEqualStrings("SKB_GSO_CB(nskb)->csum_start", audit.checkpoints[5].observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[5].blocked_by, "CHECKSUM_NONE") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[5].blocked_by, "skb_checksum()") != null);

    try std.testing.expectEqualStrings("segmentation-partial-tail-owner-transfer", audit.checkpoints[6].id);
    try std.testing.expect(audit.checkpoints[6].guard == .segmentation_partial_tail_owner_transfer);
    try std.testing.expectEqualStrings("SKB_GSO_CB(iter)->data_offset", audit.checkpoints[6].observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[6].blocked_by, "SKB_GSO_PARTIAL") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[6].blocked_by, "sock_wfree") != null);

    try std.testing.expectEqualStrings("segmentation-checksum-data-offset-crossover", audit.checkpoints[7].id);
    try std.testing.expect(audit.checkpoints[7].guard == .segmentation_checksum_data_offset_crossover);
    try std.testing.expectEqualStrings("remcsum_offload", audit.checkpoints[7].observed_fields[3]);
    try std.testing.expectEqualStrings("segs->prev", audit.checkpoints[7].observed_fields[4]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[7].blocked_by, "SKB_GSO_CB(nskb)->csum") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[7].blocked_by, "tail chain") != null);

    try std.testing.expectEqualStrings("segmentation-tail-publication-contract", audit.checkpoints[8].id);
    try std.testing.expect(audit.checkpoints[8].guard == .segmentation_tail_publication_contract);
    try std.testing.expectEqualStrings("skb_shinfo(tail)->gso_size", audit.checkpoints[8].observed_fields[2]);
    try std.testing.expectEqualStrings("skb->prev", audit.checkpoints[8].observed_fields[4]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[8].blocked_by, "segs->prev") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[8].blocked_by, "validate_xmit_skb_list()") != null);
}
