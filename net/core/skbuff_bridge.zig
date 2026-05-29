const std = @import("std");

pub const BoundaryArea = struct {
    id: []const u8,
    owner: []const u8,
    evidence: []const []const u8,
};

pub const BoundaryMap = struct {
    areas: []const BoundaryArea,
};

pub const AuditCheckpoint = struct {
    id: []const u8,
    ownership: []const u8,
    anchor_symbols: []const []const u8,
    blocked_by: []const u8,
};

pub const LifetimeAudit = struct {
    checkpoints: []const AuditCheckpoint,
    blocked_live_behaviors: []const []const u8,
};

pub const Descriptor = struct {
    name: []const u8,
    anchor: []const u8,
    posture: []const u8,
    provides_boundary_map: bool,
    provides_lifetime_audit_outline: bool,
    provides_stay_in_c_decisions: bool,
};

pub const SkbuffBridgeLab = struct {
    const areas = [_]BoundaryArea{
        .{ .id = "qdisc-facing-publication", .owner = "stay_in_c", .evidence = &.{ "validate_xmit_skb_list", "skb_mark_not_on_list" } },
        .{ .id = "queue-ownership", .owner = "stay_in_c", .evidence = &.{ "qdisc enqueue", "qdisc dequeue" } },
        .{ .id = "shared-info-refcount-ownership", .owner = "stay_in_c", .evidence = &.{ "struct skb_shared_info", "dataref", "skb_header_cloned" } },
        .{ .id = "destructor-and-free-path", .owner = "stay_in_c", .evidence = &.{ "skb_release_head_state", "skb_release_data", "consume_skb" } },
        .{ .id = "queue-facing-tail-publication", .owner = "stay_in_c", .evidence = &.{ "tail->next", "segs->prev", "tail = skb->prev" } },
        .{ .id = "segmentation-metadata", .owner = "stay_in_c", .evidence = &.{ "SKB_GSO_CB", "remcsum_offload", "SKB_GSO_PARTIAL" } },
        .{ .id = "zerocopy-frag-ownership", .owner = "stay_in_c", .evidence = &.{ "skb_orphan_frags", "skb_zerocopy_clone", "SKBFL_SHARED_FRAG" } },
    };

    const checkpoints = [_]AuditCheckpoint{
        .{ .id = "qdisc-facing-publication", .ownership = "stay_in_c", .anchor_symbols = &.{ "validate_xmit_skb_list", "skb_mark_not_on_list" }, .blocked_by = "qdisc-facing publication remains C-owned" },
        .{ .id = "queue-ownership", .ownership = "stay_in_c", .anchor_symbols = &.{ "qdisc enqueue", "qdisc dequeue" }, .blocked_by = "queue ownership remains C-owned" },
        .{ .id = "shared-info-refcount-ownership", .ownership = "stay_in_c", .anchor_symbols = &.{ "struct skb_shared_info", "dataref", "skb_header_cloned" }, .blocked_by = "shared-info refcount ownership remains C-owned" },
        .{ .id = "destructor-and-free-path", .ownership = "stay_in_c", .anchor_symbols = &.{ "skb_release_head_state", "skb_release_data", "consume_skb" }, .blocked_by = "destructor ordering remains C-owned" },
        .{ .id = "segmentation-partial-tail-owner-transfer", .ownership = "stay_in_c", .anchor_symbols = &.{ "skb_segment", "SKB_GSO_PARTIAL", "sock_wfree" }, .blocked_by = "final sock-owned tail transfer remains C-owned" },
        .{ .id = "segmentation-checksum-data-offset-crossover", .ownership = "stay_in_c", .anchor_symbols = &.{ "skb_segment", "SKB_GSO_CB", "remcsum_offload" }, .blocked_by = "checksum and data-offset crossover remains C-owned" },
        .{ .id = "zerocopy-frag-orphaning", .ownership = "stay_in_c", .anchor_symbols = &.{ "skb_orphan_frags", "skb_zerocopy_clone", "SKBFL_SHARED_FRAG" }, .blocked_by = "zerocopy fragment orphaning remains C-owned" },
        .{ .id = "tail-destructor-socket-contract", .ownership = "stay_in_c", .anchor_symbols = &.{ "sock_wfree", "tail->destructor", "tail->sk" }, .blocked_by = "socket destructor handoff remains C-owned" },
        .{ .id = "segmentation-tail-publication-consumer-contract", .ownership = "stay_in_c", .anchor_symbols = &.{ "skb_segment", "segs->prev", "validate_xmit_skb_list" }, .blocked_by = "tail->next, segs->prev, skb_mark_not_on_list(), and tail = skb->prev stay C-owned" },
    };

    const blocked = [_][]const u8{
        "qdisc-facing publication",
        "queue ownership",
        "skb lifetime ownership",
        "checksum ownership",
        "destructor coordination",
        "segmentation metadata",
        "zerocopy fragment orphaning",
        "shared-frag ownership transfer",
        "final sock-owned tail transfer",
    };

    pub fn descriptor() Descriptor {
        return .{
            .name = "skbuff_boundary_map_lab",
            .anchor = "net/core/skbuff.c",
            .posture = "boundary_map_only",
            .provides_boundary_map = true,
            .provides_lifetime_audit_outline = true,
            .provides_stay_in_c_decisions = true,
        };
    }

    pub fn boundaryMap() BoundaryMap {
        return .{ .areas = &areas };
    }

    pub fn lifetimeAudit() LifetimeAudit {
        return .{ .checkpoints = &checkpoints, .blocked_live_behaviors = &blocked };
    }

    pub fn stayInCDecisionCount() usize {
        return 3;
    }

    pub fn nextAuditFocus() []const u8 {
        return "No smaller review-only skbuff follow-up remains until live ownership blocker evidence changes.";
    }
};

test "phase14 skbuff bridge lab stays review-only" {
    try std.testing.expectEqualStrings("boundary_map_only", SkbuffBridgeLab.descriptor().posture);
    try std.testing.expectEqual(@as(usize, 7), SkbuffBridgeLab.boundaryMap().areas.len);
    try std.testing.expectEqual(@as(usize, 9), SkbuffBridgeLab.lifetimeAudit().checkpoints.len);
}
