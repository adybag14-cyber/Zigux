const std = @import("std");

const manifest = @embedFile("fixtures/phase1_helper_manifest.json");

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

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, manifest, marker) != null);
}

fn requireSingleMarker(marker: []const u8) !void {
    try requireMarker(marker);
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, manifest, marker));
}

fn requireHelperRoster(helper_names: []const []const u8) !void {
    for (helper_names) |helper| {
        try requireMarker(helper);
    }
}

test "phase 1 helper manifest pins the closed helper roster" {
    try requireSingleMarker("\"phase\": \"Phase 1\"");
    try requireSingleMarker("\"status\": \"closed\"");
    try requireSingleMarker("\"helper_count\": 13");
    try requireHelperRoster(&all_helpers);
}

test "phase 1 helper manifest keeps lane families disjoint" {
    try requireSingleMarker("\"shared_replay_parked_helpers\"");
    try requireSingleMarker("\"direct_anchor_followup_helpers\"");
    try requireHelperRoster(&shared_replay_parked_helpers);
    try requireHelperRoster(&direct_anchor_followup_helpers);

    for (shared_replay_parked_helpers) |shared_helper| {
        for (direct_anchor_followup_helpers) |direct_helper| {
            try std.testing.expect(!std.mem.eql(u8, shared_helper, direct_helper));
        }
    }
}

test "phase 1 helper manifest keeps anti-overlap lane rule explicit" {
    try requireSingleMarker(
        "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    );
    try requireSingleMarker(
        "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
    );
}
