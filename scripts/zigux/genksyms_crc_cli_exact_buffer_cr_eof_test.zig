const std = @import("std");
const gen = @import("genksyms_crc.zig");

test "genksyms crc CLI trims exact-buffer EOF carriage returns" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = "exact-buffer-cr-eof-input.txt";
    var rooted_input_path_buffer: [192]u8 = undefined;
    const rooted_input_path = try std.fmt.bufPrint(
        &rooted_input_path_buffer,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path, input_path },
    );

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 4095);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "exact_buffer_symbol_");
    try input.appendNTimes(std.testing.allocator, 'x', 4095 - input.items.len - 2);
    const trimmed_len = input.items.len;
    try input.append(std.testing.allocator, '\r');
    try input.append(std.testing.allocator, '\r');
    try std.testing.expectEqual(@as(usize, 4095), input.items.len);
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = input_path, .data = input.items });

    var argv = [_][]const u8{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
        rooted_input_path,
    };

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &argv,
        .stdout_limit = .limited(16384),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.GenksymsCrcCliDidNotExit,
    }
    try std.testing.expectEqualStrings("", result.stderr);

    const trimmed_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(input.items[0..trimmed_len])},
    );
    defer std.testing.allocator.free(trimmed_crc);
    const untrimmed_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(input.items)},
    );
    defer std.testing.allocator.free(untrimmed_crc);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"exact_buffer_symbol_") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, trimmed_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, untrimmed_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\\r") == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, result.stdout, '\r') == null);
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, result.stdout, "crc_hex"));
}
