const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 rbtree survey keeps the direct anchor and repo-reality warning aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const parity_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-rbtree-parity.py",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(parity_checker);

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
    try expectContains(parity_checker, "helper_impl_linked_type_marker");
    try expectContains(parity_checker, "helper_impl_clear_linked_node_marker");
    try expectContains(parity_checker, "helper_impl_add_linked_marker");
    try expectContains(parity_checker, "helper_impl_erase_linked_marker");
}
