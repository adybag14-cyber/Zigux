const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 rbtree survey keeps the direct anchor note aligned with the route-present shared packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const direct_anchor_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(direct_anchor_note);

    const rbtree_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-rbtree-slice.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(rbtree_slice);

    const phase7_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(phase7_build);

    const shared_packet_paths = [_][]const u8{
        "`Documentation/zigux/phase7-string-helpers-slice.md`",
        "`Documentation/zigux/phase7-argv-split-slice.md`",
        "`Documentation/zigux/phase7-rbtree-slice.md`",
        "`zigux/tests/phase7_build.zig`",
    };

    try std.testing.expectEqualStrings("P7-L13", active_lane_key);
    try expectContains(
        direct_anchor_note,
        "Current direct-readback Phase 7 rbtree anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    );
    try expectContains(
        direct_anchor_note,
        "Current directly readable shared Phase 7 packet also includes:",
    );

    for (shared_packet_paths) |path| {
        try expectContains(direct_anchor_note, path);
    }

    try expectContains(
        direct_anchor_note,
        "`string_helpers` is back on current `master` as the Phase 7 expanded starter packet",
    );
    try expectContains(
        direct_anchor_note,
        "`argv_split` and `rbtree` stay reviewable through their dedicated Phase 7 slice notes and survey gates",
    );
    try expectContains(
        direct_anchor_note,
        "`cmdline` stays reviewable through the parked Phase 1 helper packet",
    );
    try expectContains(
        direct_anchor_note,
        "Do not widen this note into broader validator, checker, manifest, fixture, or make-wrapper claims without a fresh same-lane reread of those sibling review surfaces.",
    );

    try expectContains(rbtree_slice, "`PHASE7_STATUS=parked`");
    try expectContains(rbtree_slice, "`zigux/tests/phase7_build.zig`");

    for ([_][]const u8{
        "../../lib/string_helpers.zig",
        "phase7_string_helpers.zig",
        "../../lib/cmdline.zig",
        "phase7_cmdline.zig",
        "../../lib/argv_split.zig",
        "phase7_argv_split.zig",
        "../../lib/rbtree.zig",
        "phase7_rbtree.zig",
    }) |needle| {
        try expectContains(phase7_build, needle);
    }
}
