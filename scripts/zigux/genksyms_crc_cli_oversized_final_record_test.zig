const std = @import("std");
const gen = @import("genksyms_crc.zig");

const c_line_payload_len = 4095;

test "genksyms crc CLI splits an oversized final EOF record like fgets" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = "oversized-final-record.txt";
    var rooted_input_path_buffer: [160]u8 = undefined;
    const rooted_input_path = try std.fmt.bufPrint(
        &rooted_input_path_buffer,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path, input_path },
    );

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 4);
    defer input.deinit(std.testing.allocator);
    try input.appendNTimes(std.testing.allocator, 'a', c_line_payload_len);
    try input.appendSlice(std.testing.allocator, "tail");
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
        .stdout_limit = .limited(20000),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.GenksymsCrcCliDidNotExit,
    }
    try std.testing.expectEqualStrings("", result.stderr);

    const full_chunk_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(input.items[0..c_line_payload_len])},
    );
    defer std.testing.allocator.free(full_chunk_crc);
    const tail_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("tail")},
    );
    defer std.testing.allocator.free(tail_crc);
    const unsplit_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(input.items)},
    );
    defer std.testing.allocator.free(unsplit_crc);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, full_chunk_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, tail_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, unsplit_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"tail\"") != null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, result.stdout, "crc_hex"));
}
