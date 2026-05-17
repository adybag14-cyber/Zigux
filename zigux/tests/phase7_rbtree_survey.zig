const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 rbtree survey keeps the direct anchor, repo-reality warning, and helper ownership markers aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const helper_impl = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/rbtree.zig",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(helper_impl);

    const broader_packet_paths = [_][]const u8{
        "`Documentation/zigux/phase7-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase7-rbtree-slice.md`",
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "`zigux/tests/phase7_rbtree.zig`",
        "`zigux/tests/phase7_rbtree_manifest.json`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        "`zigux/tests/phase7_build.zig`",
    };

    const helper_ownership_markers = [_][]const u8{
        "pub const NodeLinked",
        "pub const RootLinked",
        "pub fn findFirst",
        "pub fn nextMatch",
        "pub fn eraseLinked",
        "pub fn clearNode",
        "pub fn eraseInit",
        "pub fn eraseInitCached",
        "pub fn replaceNode",
        "pub fn replaceNodeCached",
        "pub fn firstPostorder",
        "pub fn nextPostorder",
    };

    try std.testing.expectEqualStrings("P7-L13", active_lane_key);
    try expectContains(tests_root, "Phase 7 review packet");
    try expectContains(
        tests_root,
        "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    );
    try expectContains(tests_root, "repo-reality warning for the broader Phase 7 rbtree packet:");

    for (broader_packet_paths) |path| {
        try expectContains(tests_root, path);
    }

    try expectContains(
        tests_root,
        "treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again",
    );
    try expectContains(
        tests_root,
        "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
    );
    try expectContains(
        tests_root,
        "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree",
    );
    try expectContains(
        tests_root,
        "`scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_manifest.json`",
    );

    for (helper_ownership_markers) |marker| {
        try expectContains(helper_impl, marker);
    }
}
