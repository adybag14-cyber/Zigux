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

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(samples_readme);

    const phase7_cmdline_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-cmdline-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase7_cmdline_slice);

    const phase7_cmdline_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_cmdline.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase7_cmdline_tests);

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
    try expectContains(roadmap, "runtime-safe leaf helpers");
    try expectContains(roadmap, "integration with validation substrate");

    try expectContains(tests_readme, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(tests_readme, "helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`");
    try expectContains(tests_readme, "cannot import fixtures outside the helper module path");
    try expectContains(samples_readme, "no `samples/zigux/*cmdline*` Phase 5 reference sample");

    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOptions preserves descending-range and partial-parse stop behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOptions keeps array-capacity stop behavior explicit when a range is only partially stored") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 memparse preserves suffix scaling and stop index semantics") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 parseOptionStr matches only exact bare options") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 numeric helpers reject explicit leading plus signs to stay with cmdline.c simple_strtoull semantics") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOption matches malformed-token classification from the Linux KUnit corpus") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 nextArg matches serialized edge fixtures") != null);

    try expectContains(phase7_cmdline_slice, "zigux/tests/phase7_cmdline.zig");
    try expectContains(phase7_cmdline_slice, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(phase7_cmdline_slice, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(phase7_cmdline_slice, "zig build test --build-file zigux/tests/phase7_build.zig");
    try expectContains(phase7_cmdline_slice, "runtime-safe leaf helpers");
    try expectContains(phase7_cmdline_slice, "integration with validation substrate through `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig`");
    try expectContains(phase7_cmdline_slice, "helper-local test runs cannot import that fixture from outside the helper module path");
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "descending-range and unparseable-suffix early stop behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "array-capacity stop behavior when a hyphen range is only partially stored") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "memory-size suffix scaling with accurate parse-stop reporting") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "rejection of explicit leading-plus numeric inputs") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "exact bare-option matching for comma-delimited flags") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "C-style stop-at-NUL handling for bare-option scans") != null);

    try expectContains(phase7_build, "phase7_cmdline_survey.zig");
    try expectContains(phase7_build, "phase7-cmdline-survey-tests");
}
