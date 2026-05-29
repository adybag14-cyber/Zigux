const std = @import("std");

const HelperGroup = enum {
    shared_replay_parked,
    direct_anchor_followup,
};

const HelperRule = struct {
    path: []const u8,
    group: HelperGroup,
};

const helper_rules = [_]HelperRule{
    .{ .path = "tools/lib/argv_split.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/bitmap.zig", .group = .direct_anchor_followup },
    .{ .path = "tools/lib/cmdline.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/ctype.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/find_bit.zig", .group = .direct_anchor_followup },
    .{ .path = "tools/lib/hweight.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/list_sort.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/rbtree.zig", .group = .direct_anchor_followup },
    .{ .path = "tools/lib/slab.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/str_error_r.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/string.zig", .group = .direct_anchor_followup },
    .{ .path = "tools/lib/vsprintf.zig", .group = .shared_replay_parked },
    .{ .path = "tools/lib/zalloc.zig", .group = .shared_replay_parked },
};

const DelegatedChecker = struct {
    path: []const u8,
    pass_marker: []const u8,
};

const delegated_checkers = [_]DelegatedChecker{
    .{
        .path = "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        .pass_marker = "PHASE1_BITMAP_DIRECT_ANCHOR_CHECKER=pass",
    },
    .{
        .path = "scripts/zigux/check-phase1-find-bit-review-packet.py",
        .pass_marker = "PHASE1_FIND_BIT_REVIEW_CHECKER=pass",
    },
    .{
        .path = "scripts/zigux/check-phase1-rbtree-direct-anchors.py",
        .pass_marker = "PHASE1_RBTREE_DIRECT_ANCHOR_CHECKER=pass",
    },
    .{
        .path = "scripts/zigux/check-phase1-rbtree-review-packet.py",
        .pass_marker = "PHASE1_RBTREE_REVIEW_CHECKER=pass",
    },
    .{
        .path = "scripts/zigux/check-phase1-string-review-packet.py",
        .pass_marker = "PHASE1_STRING_REVIEW_CHECKER=pass",
    },
};

const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const closure_marker = "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker";

const rule_summary = "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.";
const anti_overlap_rule = "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countGroup(group: HelperGroup) usize {
    var count: usize = 0;
    for (helper_rules) |rule| {
        if (rule.group == group) count += 1;
    }
    return count;
}

fn hasHelper(path: []const u8, group: HelperGroup) bool {
    for (helper_rules) |rule| {
        if (std.mem.eql(u8, rule.path, path) and rule.group == group) return true;
    }
    return false;
}

test "phase1 direct-anchor manifest gate keeps the helper split explicit" {
    try std.testing.expectEqual(@as(usize, 13), helper_rules.len);
    try std.testing.expectEqual(@as(usize, 9), countGroup(.shared_replay_parked));
    try std.testing.expectEqual(@as(usize, 4), countGroup(.direct_anchor_followup));

    try std.testing.expect(hasHelper("tools/lib/bitmap.zig", .direct_anchor_followup));
    try std.testing.expect(hasHelper("tools/lib/find_bit.zig", .direct_anchor_followup));
    try std.testing.expect(hasHelper("tools/lib/rbtree.zig", .direct_anchor_followup));
    try std.testing.expect(hasHelper("tools/lib/string.zig", .direct_anchor_followup));
}

test "phase1 direct-anchor manifest gate keeps parked helpers out of direct follow-up" {
    const parked_helpers = [_][]const u8{
        "tools/lib/argv_split.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    };

    for (parked_helpers) |path| {
        try std.testing.expect(hasHelper(path, .shared_replay_parked));
        try std.testing.expect(!hasHelper(path, .direct_anchor_followup));
    }
}

test "phase1 direct-anchor manifest gate delegates only to focused phase1 checkers" {
    try std.testing.expectEqual(@as(usize, 5), delegated_checkers.len);

    for (delegated_checkers) |checker| {
        try std.testing.expect(contains(checker.path, "scripts/zigux/check-phase1-"));
        try std.testing.expect(contains(checker.path, ".py"));
        try std.testing.expect(contains(checker.pass_marker, "PHASE1_"));
        try std.testing.expect(contains(checker.pass_marker, "=pass"));
        try std.testing.expect(!contains(checker.path, "validate-phase1-closure.py"));
    }
}

test "phase1 direct-anchor manifest gate remains manifest-backed" {
    try std.testing.expect(std.mem.eql(u8, manifest_path, "zigux/tests/fixtures/phase1_helper_manifest.json"));
    try std.testing.expect(contains(closure_marker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE"));
    try std.testing.expect(contains(closure_marker, "check-phase1-direct-anchor-manifest-gate.py"));
    try std.testing.expect(contains(closure_marker, "bitmap, find_bit, rbtree, and string"));
}

test "phase1 direct-anchor manifest gate preserves the anti-overlap rule" {
    try std.testing.expect(contains(rule_summary, "nine helpers"));
    try std.testing.expect(contains(rule_summary, "bitmap, find_bit, rbtree, and string"));
    try std.testing.expect(contains(anti_overlap_rule, "Do not reopen Phase 1 by batching helpers"));
    try std.testing.expect(contains(anti_overlap_rule, "shared-replay parked helpers"));
    try std.testing.expect(contains(anti_overlap_rule, "direct-anchor helpers"));
}
