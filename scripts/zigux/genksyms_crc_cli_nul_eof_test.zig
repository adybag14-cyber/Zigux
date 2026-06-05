const std = @import("std");
const gen = @import("genksyms_crc.zig");

test "genksyms crc CLI truncates a final NUL record at EOF" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = "nul-eof-input.txt";
    var rooted_input_path_buffer: [128]u8 = undefined;
    const rooted_input_path = try std.fmt.bufPrint(
        &rooted_input_path_buffer,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path, input_path },
    );
    const input = "struct device\nunsigned int visible\x00hidden eof bytes\r\r";
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = input_path, .data = input });

    var argv = [_][]const u8{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
        rooted_input_path,
    };

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.GenksymsCrcCliDidNotExit,
    }
    try std.testing.expectEqualStrings("", result.stderr);

    const visible_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("unsigned int visible")},
    );
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("hidden eof bytes")},
    );
    defer std.testing.allocator.free(hidden_crc);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"struct device\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"unsigned int visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "hidden eof bytes") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, result.stdout, 0) == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, result.stdout, "crc_hex"));
}
