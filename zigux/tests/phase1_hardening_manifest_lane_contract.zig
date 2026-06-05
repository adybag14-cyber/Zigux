const std = @import("std");
const testing = std.testing;

const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const validator_path = "scripts/zigux/validate-phase1-closure.py";

const all_helpers = [_][]const u8{
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

const shared_replay_parked_helpers = [_][]const u8{
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

const direct_anchor_followup_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase1 helper manifest pins closed helper roster" {
    const manifest = try readRepoFile(testing.allocator, manifest_path);
    defer testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 1\"");
    try expectContains(manifest, "\"status\": \"closed\"");
    try expectContains(manifest, "\"helper_count\": 13");
    try expectContains(manifest, "\"helpers\": [");
    try expectContains(manifest, "\"lane_sequencing\": {");
    try expectContains(manifest, "\"review_anchors\": {");

    for (all_helpers) |helper| {
        try expectContains(manifest, helper);
    }
}

test "phase1 helper manifest keeps shared and direct lanes disjoint" {
    const manifest = try readRepoFile(testing.allocator, manifest_path);
    defer testing.allocator.free(manifest);

    try expectContains(manifest, "\"shared_replay_parked_helpers\": [");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\": [");
    try expectContains(manifest, "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above");
    try expectContains(manifest, "bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors");
    try expectContains(manifest, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");
    try expectContains(manifest, "shared-replay parked helpers reopen only for packet drift");
    try expectContains(manifest, "direct-anchor helpers reopen only for their existing helper-local anchors");

    for (shared_replay_parked_helpers) |helper| {
        try expectContains(manifest, helper);
    }
    for (direct_anchor_followup_helpers) |helper| {
        try expectContains(manifest, helper);
    }

    try testing.expectEqual(all_helpers.len, shared_replay_parked_helpers.len + direct_anchor_followup_helpers.len);
}

test "phase1 closure validator mirrors manifest lane contract" {
    const validator = try readRepoFile(testing.allocator, validator_path);
    defer testing.allocator.free(validator);

    try expectContains(validator, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try expectContains(validator, "PHASE1_HELPER_COUNT=13");
    try expectContains(validator, "scripts/zigux/validate-phase1-closure.py");
    try expectNotContains(validator, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
}
