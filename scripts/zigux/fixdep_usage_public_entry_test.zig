const std = @import("std");

fn expectUsage(argv_tail: []const []const u8) !void {
    const base_argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
    };

    var argv = try std.ArrayList([]const u8).initCapacity(
        std.testing.allocator,
        base_argv.len + argv_tail.len,
    );
    defer argv.deinit(std.testing.allocator);
    try argv.appendSlice(std.testing.allocator, base_argv);
    try argv.appendSlice(std.testing.allocator, argv_tail);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv.items,
        .cwd = .{ .path = "../.." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(
        "Usage: fixdep <depfile> <target> <cmdline>\n",
        result.stderr,
    );
}

test "fixdep reports usage errors through the public entry path" {
    try expectUsage(&.{});
    try expectUsage(&.{
        "sample.d",
        "sample.o",
        "clang -c sample.c -o sample.o",
        "unexpected-extra-argument",
    });
}
