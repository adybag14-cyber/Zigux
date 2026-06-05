const std = @import("std");
const gen = @import("genksyms_crc.zig");

test "genksyms_crc CLI renders a real input file successfully" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "crc-input.txt",
        .data = "int\nstruct device\r\nhidden\x00ignored\n",
    });

    const input_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/crc-input.txt", .{tmp.sub_path});
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

    const hidden_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("hidden")});
    defer std.testing.allocator.free(hidden_crc);
    const hidden_untruncated_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("hidden\x00ignored")});
    defer std.testing.allocator.free(hidden_untruncated_crc);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"int\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"struct device\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"hidden\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, hidden_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, hidden_untruncated_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "ignored") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\\u0000") == null);
    try std.testing.expectEqual(@as(usize, 3), std.mem.count(u8, result.stdout, "\"crc_hex\""));
}
