const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 cmdline survey keeps the helper-only handoff explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(roadmap);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const cmdline_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-cmdline-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(cmdline_slice);

    const phase7_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase7_build);

    try expectContains(roadmap, "## Phase 7: In-Kernel Leaf Libraries");
    try expectContains(roadmap, "lib/cmdline.c");
    try expectContains(roadmap, "- `lib/cmdline.zig`");

    try expectContains(tests_readme, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(tests_readme, "helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`");

    try expectContains(cmdline_slice, "zigux/tests/phase7_cmdline.zig");
    try expectContains(cmdline_slice, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(cmdline_slice, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(cmdline_slice, "zig build test --build-file zigux/tests/phase7_build.zig");

    try expectContains(phase7_build, "phase7_cmdline_survey.zig");
    try expectContains(phase7_build, "phase7-cmdline-survey-tests");
}
