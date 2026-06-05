const std = @import("std");

test "genksyms_crc CLI succeeds for a zero-byte input file" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "empty-input.txt",
        .data = "",
    });

    const input_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/empty-input.txt", .{tmp.sub_path});
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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expectEqualStrings("{\"cases\":[]}\n", result.stdout);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "input") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "crc_hex") == null);
}
