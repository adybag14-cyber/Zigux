const std = @import("std");

test "genksyms_crc CLI succeeds when every input chunk is skipped" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "all-skipped-input.txt",
        .data = "\n\r\n\x00hidden\n\r\r",
    });

    const input_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/all-skipped-input.txt", .{tmp.sub_path});
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
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "crc_hex") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\\u0000") == null);
}
