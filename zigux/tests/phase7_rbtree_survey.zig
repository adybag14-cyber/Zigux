const std = @import("std");

const active_lane_key = "P7-L14";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps reusable leaf-library ownership evidence explicit" {
    const allocator = std.testing.allocator;

    const rbtree_slice = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(rbtree_slice);
    const rbtree_manifest = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(rbtree_manifest);
    const argv_split_manifest = try readRepoFile(allocator, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(argv_split_manifest);

    try std.testing.expectEqualStrings("P7-L14", active_lane_key);

    for ([_][]const u8{
        "`PHASE7_STATUS=parked`",
        "`PHASE7_SLICE=rbtree-runtime-leaf`",
        "`lib/rbtree.zig`",
        "`zigux/tests/phase7_rbtree.zig`",
        "`zigux/tests/phase7_rbtree_survey.zig`",
        "`zigux/tests/phase7_rbtree_manifest.json`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "`zigux/tests/phase7_build.zig`",
        "`lib/argv_split.zig`",
        "`zigux/tests/phase7_argv_split.zig`",
        "detached-node ownership stays explicit",
        "duplicate-key traversal stay reviewable",
        "route-present cross-packet reminder",
    }) |needle| {
        try expectContains(rbtree_slice, needle);
    }

    for ([_][]const u8{
        "\"lane_key\": \"P7-L13\"",
        "\"anchor\": \"lib/rbtree.c\"",
        "\"lib/rbtree.zig\"",
        "\"zigux/tests/phase7_rbtree.zig\"",
        "\"zigux/tests/phase7_rbtree_survey.zig\"",
        "\"zigux/tests/phase7_rbtree_manifest.json\"",
        "\"scripts/zigux/check-phase7-rbtree-parity.py\"",
        "\"current_replay_status\": \"route_present_on_master\"",
        "duplicate-key range helpers keep ordered match ownership explicit through findFirst() and nextMatch() instead of hidden cursors",
        "detached-node ownership stays explicit through clearNode(), eraseInit(), and eraseInitCached() after erase paths",
        "linked-node teardown reconnects prev and next ownership together with leftmost continuity during eraseLinked()",
        "replaceNode() copies victim links onto replacement nodes before reconnecting parent and child ownership",
        "postorder traversal helpers treat cleared detached nodes as empty so stale parent walks do not leak past the reusable leaf packet",
    }) |needle| {
        try expectContains(rbtree_manifest, needle);
    }

    for ([_][]const u8{
        "\"lane_key\": \"P7-L09\"",
        "\"anchor\": \"lib/argv_split.c\"",
        "\"lib/argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split_survey.zig\"",
        "\"scripts/zigux/check-phase7-argv-split-packet.py\"",
        "\"current_replay_status\": \"route_present_on_master\"",
        "\"lib/rbtree.zig\"",
        "\"zigux/tests/phase7_rbtree.zig\"",
        "copied token-buffer ownership and later source-mutation isolation",
        "owned-storage reuse keeps token pointers inside caller-managed storage",
        "non-blank results keep storage, argv slices, and C-argv views distinct across callers",
        "argvFree on one live non-blank result does not disturb another caller-owned split result",
        "deinit on one live non-blank result does not disturb another caller-owned split result",
        "blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
    }) |needle| {
        try expectContains(argv_split_manifest, needle);
    }
}
