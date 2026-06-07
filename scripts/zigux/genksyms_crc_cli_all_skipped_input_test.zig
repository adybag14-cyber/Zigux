const std = @import("std");
const Io = std.Io;

fn expectNoNeedle(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "genksyms crc cli emits empty packet when every input chunk is skipped" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;

    const input_path = ".zig-cache-lane19-crc-cli-all-skipped-input.txt";
    Io.Dir.cwd().deleteFile(io, input_path) catch {};
    defer Io.Dir.cwd().deleteFile(io, input_path) catch {};
    try Io.Dir.cwd().writeFile(io, .{
        .sub_path = input_path,
        .data = "\n\r\n\x00hidden\n\r\r\x00also-hidden",
    });

    const result = try std.process.run(allocator, io, .{
        .argv = &.{
            "zig",
            "run",
            "scripts/zigux/genksyms_crc.zig",
            "--",
            input_path,
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("{\"cases\":[]}\n", result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
    try expectNoNeedle(result.stdout, "hidden");
    try expectNoNeedle(result.stdout, "crc_hex");
}
