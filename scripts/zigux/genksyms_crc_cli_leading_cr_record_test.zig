const std = @import("std");
const gen = @import("genksyms_crc.zig");

test "genksyms crc CLI preserves leading carriage returns in visible records" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = "leading-cr-record.txt";
    var rooted_input_path_buffer: [160]u8 = undefined;
    const rooted_input_path = try std.fmt.bufPrint(
        &rooted_input_path_buffer,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path, input_path },
    );

    const leading_cr_record = "\r\rvisible";
    const input = leading_cr_record ++ "\r\nplain\n";
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

    const leading_cr_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(leading_cr_record)},
    );
    defer std.testing.allocator.free(leading_cr_crc);
    const stripped_leading_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("visible")},
    );
    defer std.testing.allocator.free(stripped_leading_crc);
    const untrimmed_trailing_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32(leading_cr_record ++ "\r")},
    );
    defer std.testing.allocator.free(untrimmed_trailing_crc);
    const plain_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{gen.crc32("plain")},
    );
    defer std.testing.allocator.free(plain_crc);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"\\r\\rvisible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, leading_cr_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, stripped_leading_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, untrimmed_trailing_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"visible\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"plain\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, plain_crc) != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, result.stdout, '\r') == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, result.stdout, "crc_hex"));
}
