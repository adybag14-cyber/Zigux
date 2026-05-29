const std = @import("std");

const direct_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const shared_helpers = [_][]const u8{
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

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase 1 direct-owner checker keeps its live gate contract visible" {
    const checker = try readRepoFile("scripts/zigux/check-phase1-direct-owner-markers.py", 192 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_HELPERS = [");
    try expectContains(checker, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(checker, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try expectOrdered(checker, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS", "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS");
    try expectContains(checker, "EXPECTED_RULE_SUMMARY");
    try expectContains(checker, "EXPECTED_ANTI_OVERLAP_RULE");

    try expectContains(checker, "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_MARKERS=pass");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_FILE_COUNT=");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_LINE_COUNT=");
    try expectContains(checker, "PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_HELPER_COUNT=");
}

test "phase 1 direct-owner helper split stays aligned with the manifest" {
    const checker = try readRepoFile("scripts/zigux/check-phase1-direct-owner-markers.py", 192 * 1024);
    defer std.testing.allocator.free(checker);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 384 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 1\"");
    try expectContains(manifest, "\"status\": \"closed\"");
    try expectContains(manifest, "\"helper_count\": 13");
    try expectContains(manifest, "\"shared_replay_parked_helpers\"");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\"");
    try expectContains(manifest, "\"rule_summary\"");
    try expectContains(manifest, "\"anti_overlap_rule\"");

    for (shared_helpers) |helper| {
        try expectContains(checker, helper);
        try expectContains(manifest, helper);
    }
    for (direct_helpers) |helper| {
        try expectContains(checker, helper);
        try expectContains(manifest, helper);
    }
}

test "phase 1 direct-owner packet keeps the four direct helpers explicit" {
    const checker = try readRepoFile("scripts/zigux/check-phase1-direct-owner-markers.py", 192 * 1024);
    defer std.testing.allocator.free(checker);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 384 * 1024);
    defer std.testing.allocator.free(manifest);

    const direct_owner_markers = [_][]const u8{
        "PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns",
        "PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask",
        "PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias",
        "PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics",
    };
    for (direct_owner_markers) |marker| {
        try expectContains(checker, marker);
    }

    try expectContains(manifest, "\"review_anchors\"");
    for (direct_helpers) |helper| {
        try expectContains(manifest, helper);
        try expectContains(manifest, "\"next_safe_step_note\"");
    }
    try expectContains(manifest, "direct helper-local follow-up anchors on current master");
    try expectContains(manifest, "shared-replay parked helpers reopen only for packet drift");
}
