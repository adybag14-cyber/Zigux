const std = @import("std");

const validator_path = "scripts/zigux/validate-phase1-closure.py";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";

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

const lane_rule_summary =
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, " ++
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local " ++
    "follow-up anchors on current master.";

const lane_rule_summary_fragments = [_][]const u8{
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, ",
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local ",
    "follow-up anchors on current master.",
};

const anti_overlap_rule =
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; " ++
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers " ++
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys.";

const anti_overlap_rule_fragments = [_][]const u8{
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; ",
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers ",
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
};

fn readFileAlloc(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MarkerOutOfOrder;
        cursor += found + needle.len;
    }
}

fn quoted(path: []const u8) []const u8 {
    return path;
}

test "phase1 manifest and closure validator keep the same helper roster" {
    const validator = try readFileAlloc(validator_path, 512 * 1024);
    defer std.testing.allocator.free(validator);
    const manifest = try readFileAlloc(manifest_path, 512 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(validator, "EXPECTED_HELPERS = [");
    try expectContains(manifest, "\"helper_count\": 13");
    try expectContains(validator, "\"helper_count\": len(EXPECTED_HELPERS)");
    try expectContains(validator, "(\"bad_helper_count\",");

    inline for (expected_helpers) |helper| {
        try expectContains(validator, quoted(helper));
        try expectContains(manifest, quoted(helper));
    }
    try expectOrdered(manifest, &expected_helpers);
}

test "phase1 shared and direct helper families stay split in validator and manifest" {
    const validator = try readFileAlloc(validator_path, 512 * 1024);
    defer std.testing.allocator.free(validator);
    const manifest = try readFileAlloc(manifest_path, 512 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try expectContains(manifest, "\"shared_replay_parked_helpers\": [");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\": [");
    try expectContains(manifest, lane_rule_summary);
    try expectContains(manifest, anti_overlap_rule);
    try expectContains(validator, "(\"stale_lane_rule_summary\",");
    try expectContains(validator, "(\"stale_anti_overlap_rule\",");

    inline for (lane_rule_summary_fragments) |fragment| {
        try expectContains(validator, fragment);
    }
    inline for (anti_overlap_rule_fragments) |fragment| {
        try expectContains(validator, fragment);
    }

    inline for (shared_replay_helpers) |helper| {
        try expectContains(validator, quoted(helper));
        try expectContains(manifest, quoted(helper));
    }
    inline for (direct_anchor_helpers) |helper| {
        try expectContains(validator, quoted(helper));
        try expectContains(manifest, quoted(helper));
    }
}

test "phase1 manifest duplicate tracking remains fail closed" {
    const validator = try readFileAlloc(validator_path, 512 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "class DuplicateTrackingDict");
    try expectContains(validator, "duplicate_keys: list[str]");
    try expectContains(validator, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(validator, "(\"duplicate_manifest_helper_count\",");
    try expectContains(validator, "(\"duplicate_manifest_lane_rule_summary\",");
}

test "phase1 direct-family review anchors stay validator-backed" {
    const validator = try readFileAlloc(validator_path, 512 * 1024);
    defer std.testing.allocator.free(validator);
    const manifest = try readFileAlloc(manifest_path, 512 * 1024);
    defer std.testing.allocator.free(manifest);

    const required_anchor_keys = [_][]const u8{
        "\"tools/lib/bitmap.zig\"",
        "\"tools/lib/find_bit.zig\"",
        "\"tools/lib/rbtree.zig\"",
        "\"tools/lib/string.zig\"",
        "\"review_packet_summary\"",
        "\"next_safe_step_note\"",
    };
    inline for (required_anchor_keys) |key| {
        try expectContains(manifest, key);
    }

    try expectContains(validator, "EXPECTED_BITMAP_REVIEW_ANCHORS");
    try expectContains(validator, "EXPECTED_FIND_BIT_REVIEW_ANCHORS");
    try expectContains(validator, "EXPECTED_RBTREE_REVIEW_ANCHORS");
    try expectContains(validator, "EXPECTED_STRING_REVIEW_ANCHORS");
    try expectContains(validator, "mutate_remove_review_key");
    try expectContains(validator, "mutate_bad_review_value");
}
