const std = @import("std");

const usage = "Usage: genksyms_crc <input.txt>\n";

fn expectUsageFailure(argv: []const []const u8) !void {
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .limited(256),
        .stderr_limit = .limited(256),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(usage, result.stderr);
}

test "genksyms CRC CLI reports usage for missing and extra arguments" {
    try expectUsageFailure(&.{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
    });

    try expectUsageFailure(&.{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
        "input.txt",
        "unexpected.txt",
    });
}
