const std = @import("std");

const manifest_json = @embedFile("fixtures/phase1_helper_manifest.json");

const expected_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const shared_replay_helpers = [_][]const u8{
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

const direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const LaneSequencing = struct {
    shared_replay_parked_helpers: []const []const u8,
    direct_anchor_followup_helpers: []const []const u8,
    rule_summary: []const u8,
    anti_overlap_rule: []const u8,
};

const HelperManifest = struct {
    phase: []const u8,
    status: []const u8,
    helper_count: u64,
    helpers: []const []const u8,
    lane_sequencing: LaneSequencing,
};

fn loadManifest() !std.json.Parsed(HelperManifest) {
    return std.json.parseFromSlice(HelperManifest, std.testing.allocator, manifest_json, .{ .ignore_unknown_fields = true });
}

fn expectStringRoster(expected: []const []const u8, actual: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_item, actual_item| {
        try std.testing.expectEqualStrings(expected_item, actual_item);
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn containsString(roster: []const []const u8, needle: []const u8) bool {
    for (roster) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

test "phase1 helper manifest pins the closed helper roster" {
    var parsed = try loadManifest();
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("Phase 1", manifest.phase);
    try std.testing.expectEqualStrings("closed", manifest.status);
    try std.testing.expectEqual(@as(u64, expected_helpers.len), manifest.helper_count);
    try expectStringRoster(&expected_helpers, manifest.helpers);
}

test "phase1 helper manifest keeps shared replay and direct anchor lanes disjoint" {
    var parsed = try loadManifest();
    defer parsed.deinit();
    const sequencing = parsed.value.lane_sequencing;

    try expectStringRoster(&shared_replay_helpers, sequencing.shared_replay_parked_helpers);
    try expectStringRoster(&direct_anchor_helpers, sequencing.direct_anchor_followup_helpers);

    for (sequencing.shared_replay_parked_helpers) |shared_helper| {
        try std.testing.expect(!containsString(sequencing.direct_anchor_followup_helpers, shared_helper));
        try std.testing.expect(containsString(parsed.value.helpers, shared_helper));
    }
    for (sequencing.direct_anchor_followup_helpers) |direct_helper| {
        try std.testing.expect(!containsString(sequencing.shared_replay_parked_helpers, direct_helper));
        try std.testing.expect(containsString(parsed.value.helpers, direct_helper));
    }

    try std.testing.expectEqual(
        parsed.value.helpers.len,
        sequencing.shared_replay_parked_helpers.len + sequencing.direct_anchor_followup_helpers.len,
    );
}

test "phase1 helper manifest rule text names both lane ownership classes" {
    var parsed = try loadManifest();
    defer parsed.deinit();
    const sequencing = parsed.value.lane_sequencing;

    try expectContains(sequencing.rule_summary, "shared replay");
    try expectContains(sequencing.rule_summary, "bitmap, find_bit, rbtree, and string");
    try expectContains(sequencing.rule_summary, "direct helper-local follow-up anchors");
    try expectContains(sequencing.anti_overlap_rule, "Do not reopen Phase 1 by batching helpers across those two sets");
    try expectContains(sequencing.anti_overlap_rule, "shared-replay parked helpers reopen only for packet drift");
    try expectContains(sequencing.anti_overlap_rule, "direct-anchor helpers reopen only");
}
