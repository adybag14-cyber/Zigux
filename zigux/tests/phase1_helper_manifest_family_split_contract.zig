const std = @import("std");

const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const validation_fixture_path = "zigux/tests/.lane16_phase1_helper_manifest_family_split_fixture.json";
const local_validation_fixture_path = ".lane16_phase1_helper_manifest_family_split_fixture.json";

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

const direct_anchor_review_fields = [_][]const u8{
    "\"tools/lib/bitmap.zig\"",
    "\"tools/lib/find_bit.zig\"",
    "\"tools/lib/rbtree.zig\"",
    "\"tools/lib/string.zig\"",
    "\"phase1_helper_replay_anchor\"",
    "\"parity_fixture_keys\"",
    "\"review_packet_summary\"",
    "\"next_safe_step_note\"",
};

const parked_review_fields = [_][]const u8{
    "\"tools/lib/argv_split.zig\"",
    "\"tools/lib/cmdline.zig\"",
    "\"tools/lib/ctype.zig\"",
    "\"tools/lib/hweight.zig\"",
    "\"tools/lib/list_sort.zig\"",
    "\"tools/lib/slab.zig\"",
    "\"tools/lib/str_error_r.zig\"",
    "\"tools/lib/vsprintf.zig\"",
    "\"tools/lib/zalloc.zig\"",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn readManifest(limit: usize) ![]u8 {
    return readFile(validation_fixture_path, limit) catch |err| switch (err) {
        error.FileNotFound => return readFile(local_validation_fixture_path, limit) catch |inner_err| switch (inner_err) {
            error.FileNotFound => return readFile(manifest_path, limit),
            else => return inner_err,
        },
        else => return err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBefore;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfter;
    try std.testing.expect(before_index < after_index);
}

fn validateFamilySplit(text: []const u8) !void {
    try expectContains(text, "\"phase\": \"Phase 1\"");
    try expectContains(text, "\"status\": \"closed\"");
    try expectContains(text, "\"helper_count\": 13");
    try expectContains(text, "\"helpers\"");
    try expectContains(text, "\"shared_replay_parked_helpers\"");
    try expectContains(text, "\"direct_anchor_followup_helpers\"");
    try expectContains(text, "\"rule_summary\"");
    try expectContains(text, "\"anti_overlap_rule\"");

    inline for (shared_replay_helpers) |helper| {
        try expectContains(text, helper);
    }
    inline for (direct_anchor_helpers) |helper| {
        try expectContains(text, helper);
    }

    try expectContains(text, "Phase 1 helper follow-up stays parked on shared replay");
    try expectContains(text, "bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors");
    try expectContains(text, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");
    try expectContains(text, "shared-replay parked helpers reopen only for packet drift");
    try expectContains(text, "direct-anchor helpers reopen only for their existing helper-local anchors");

    try expectOrdered(text, "\"shared_replay_parked_helpers\"", "\"direct_anchor_followup_helpers\"");
    try expectOrdered(text, "\"direct_anchor_followup_helpers\"", "\"anti_overlap_rule\"");
}

fn validateReviewAnchorSchema(text: []const u8) !void {
    try expectContains(text, "\"review_anchors\"");
    inline for (direct_anchor_review_fields) |field| {
        try expectContains(text, field);
    }
    inline for (parked_review_fields) |field| {
        try expectContains(text, field);
    }

    try expectContains(text, "\"shared_replay_summary\"");
    try expectContains(text, "\"shared_logical_fixture_keys\"");
    try expectContains(text, "\"shared_range_fixture_keys\"");
    try expectContains(text, "\"cached_root_direct_review_summary\"");
    try expectContains(text, "\"memparse_review_anchors\"");
    try expectContains(text, "\"sysfs_review_summary\"");
    try expectContains(text, "\"review_packet_summary\"");
    try expectContains(text, "\"next_safe_step_note\"");
}

test "phase1 helper manifest keeps the closed helper family split explicit" {
    const manifest = try readManifest(1024 * 1024);
    defer std.testing.allocator.free(manifest);

    try validateFamilySplit(manifest);
}

test "phase1 helper manifest keeps direct and parked review anchors visible" {
    const manifest = try readManifest(1024 * 1024);
    defer std.testing.allocator.free(manifest);

    try validateReviewAnchorSchema(manifest);
}

test "phase1 helper manifest contract fixtures fail closed for stale split wording" {
    const stale =
        \\{
        \\  "phase": "Phase 1",
        \\  "status": "closed",
        \\  "helper_count": 13,
        \\  "shared_replay_parked_helpers": ["tools/lib/argv_split.zig"],
        \\  "direct_anchor_followup_helpers": ["tools/lib/bitmap.zig"],
        \\  "rule_summary": "Phase 1 helper follow-up is open to any helper.",
        \\  "anti_overlap_rule": "Batch helpers freely.",
        \\  "review_anchors": {}
        \\}
    ;

    try expectContains(stale, "\"shared_replay_parked_helpers\"");
    try expectContains(stale, "\"direct_anchor_followup_helpers\"");
    try expectNotContains(stale, "shared-replay parked helpers reopen only for packet drift");
    try expectNotContains(stale, "direct-anchor helpers reopen only for their existing helper-local anchors");
}
