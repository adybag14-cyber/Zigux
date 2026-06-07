const std = @import("std");

test "genksyms CRC CLI emits an empty cases packet for an empty input file" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const input_path = "empty-input.txt";
    var rooted_input_path_buffer: [160]u8 = undefined;
    const rooted_input_path = try std.fmt.bufPrint(
        &rooted_input_path_buffer,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path, input_path },
    );
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = input_path, .data = "" });

    var argv = [_][]const u8{
        "zig",
        "run",
        "scripts/zigux/genksyms_crc.zig",
        "--",
        rooted_input_path,
    };

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &argv,
        .stdout_limit = .limited(256),
        .stderr_limit = .limited(256),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("{\"cases\":[]}\n", result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, result.stdout, "crc_hex"));
}
