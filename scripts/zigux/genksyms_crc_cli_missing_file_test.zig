const std = @import("std");

test "genksyms_crc CLI fails without emitting json for a missing input file" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/missing-input.txt", .{tmp.sub_path});
    defer std.testing.allocator.free(input_path);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "scripts/zigux/genksyms_crc.zig",
            "--",
            input_path,
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expect(code != 0),
        else => try std.testing.expect(false),
    }
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expect(result.stderr.len > 0);
    try std.testing.expect(std.mem.indexOf(u8, result.stderr, "FileNotFound") != null or std.mem.indexOf(u8, result.stderr, "error") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "cases") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "crc_hex") == null);
}
