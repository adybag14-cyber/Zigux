const std = @import("std");

fn expectUsageFailure(argv: []const []const u8) !void {
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
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

test "fixdep public entry reports usage for wrong argument counts" {
    try expectUsageFailure(&.{
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
    });

    try expectUsageFailure(&.{
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        "sample.d",
        "sample.o",
        "cc -c sample.c",
        "extra",
    });
}
