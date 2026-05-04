const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 string helper sample boundary keeps the shipped build helper-only" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(samples_readme);

    const phase7_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase7_build);

    const phase7_build_inventory = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_build_inventory.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase7_build_inventory);

    try std.testing.expectError(
        error.FileNotFound,
        std.Io.Dir.cwd().access(io_instance.io(), "samples/zigux/string_helpers_sample.zig", .{}),
    );

    var samples_dir = try std.Io.Dir.cwd().openDir(io_instance.io(), "samples/zigux", .{ .iterate = true });
    defer samples_dir.close(io_instance.io());

    var samples_iter = samples_dir.iterate();
    while (try samples_iter.next(io_instance.io())) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;
        try std.testing.expect(std.mem.indexOf(u8, entry.name, "string") == null);
    }

    try expectContains(samples_readme, "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(samples_readme, "treat any new `samples/zigux/*string*.zig` file as review-blocking");
    try expectContains(phase7_build, "phase7-string-helpers-tests");
    try expectContains(phase7_build, "phase7-string-helpers-survey-tests");
    try expectContains(phase7_build, "phase7-string-helpers-sample-boundary-tests");
    try expectContains(phase7_build_inventory, "\"phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(phase7_build_inventory, "\"phase7-string-helpers-sample-boundary-tests\"");
    try expectContains(phase7_build_inventory, "\"phase7-string-helpers-sample-boundary-tests\": \"repo_root\"");
    try std.testing.expect(std.mem.indexOf(u8, phase7_build, "phase7-string-helpers-sample-tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_build, "phase7_string_helpers_sample.zig") == null);
}
