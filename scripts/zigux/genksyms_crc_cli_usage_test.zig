const std = @import("std");

fn expectUsageFailure(argv: []const []const u8) !void {
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(256),
        .stderr_limit = .limited(256),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings("Usage: genksyms_crc <input.txt>\n", result.stderr);
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, result.stdout, "cases"));
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, result.stderr, "crc_hex"));
}

test "genksyms CRC CLI reports usage for missing or extra input paths" {
    const missing_input = [_][]const u8{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
    };
    try expectUsageFailure(&missing_input);

    const extra_input = [_][]const u8{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
        "first.txt",
        "second.txt",
    };
    try expectUsageFailure(&extra_input);
}
