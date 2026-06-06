const std = @import("std");
const gen = @import("genksyms_crc.zig");

test "genksyms crc CLI truncates exact-buffer hidden tail after NUL" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = "exact-buffer-nul-hidden-tail-input.txt";
    var rooted_input_path_buffer: [192]u8 = undefined;
    const rooted_input_path = try std.fmt.bufPrint(
        &rooted_input_path_buffer,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path, input_path },
    );

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 4104);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "exact_buffer_visible_symbol");
    const visible_len = input.items.len;
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden_tail_crc_must_not_escape");
    try input.appendNTimes(std.testing.allocator, 'h', 4095 - input.items.len);
    try std.testing.expectEqual(@as(usize, 4095), input.items.len);
    try input.appendSlice(std.testing.allocator, "\nnext_visible\n");
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

    const visible_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(input.items[0..visible_len])},
    );
    defer std.testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("hidden_tail_crc_must_not_escape")},
    );
    defer std.testing.allocator.free(hidden_crc);
    const next_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("next_visible")},
    );
    defer std.testing.allocator.free(next_crc);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"exact_buffer_visible_symbol\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, visible_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"next_visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, next_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "hidden_tail_crc_must_not_escape") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, hidden_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\\u0000") == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, result.stdout, 0) == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, result.stdout, "crc_hex"));
}
