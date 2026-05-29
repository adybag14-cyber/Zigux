const std = @import("std");

const tests_readme = @embedFile("README.md");

const active_direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const parked_shared_replay_helpers = [_][]const u8{
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

test "tests README keeps Phase 1 direct-anchor helper boundary bounded" {
    const line = lineContaining(
        tests_readme,
        "bounded direct-anchor follow-up markers on current `master`",
    ) orelse return error.MissingDirectAnchorBoundaryLine;

    try expectContains(line, "the nine shared-replay parked helpers reopen only for packet or fixture drift");
    try expectContains(line, "only `tools/lib/bitmap.zig`");
    try expectContains(line, "`tools/lib/find_bit.zig`");
    try expectContains(line, "`tools/lib/rbtree.zig`");
    try expectContains(line, "and `tools/lib/string.zig`");

    for (active_direct_anchor_helpers) |helper| {
        try expectContains(line, helper);
    }
    for (parked_shared_replay_helpers) |helper| {
        try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, line, helper));
    }
}

test "tests README keeps Phase 1 smoke and helper replay routes visible" {
    try expectContains(
        tests_readme,
        "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    );
    try expectContains(
        tests_readme,
        "current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    );
    try expectContains(tests_readme, "`zigux/tests/phase1_host_tools_smoke.zig`");
    try expectContains(tests_readme, "`zigux/tests/phase1_helpers_build.zig`");
}

fn lineContaining(haystack: []const u8, needle: []const u8) ?[]const u8 {
    var start: usize = 0;
    while (start < haystack.len) {
        const end = std.mem.indexOfScalarPos(u8, haystack, start, '\n') orelse haystack.len;
        const line = haystack[start..end];
        if (std.mem.indexOf(u8, line, needle) != null) {
            return line;
        }
        start = end + 1;
    }
    return null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}
