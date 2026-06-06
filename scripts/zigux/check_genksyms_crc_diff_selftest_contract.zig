const std = @import("std");

const checker_path = "scripts/zigux/check-genksyms-crc-diff.py";

test "genksyms CRC diff checker self-test emits stable pass markers" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "python3", checker_path, "--self-test" },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "GENKSYMS_CRC_SELF_TEST=pass\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "GENKSYMS_CRC_SELF_TEST_CASE_COUNT=39\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "GENKSYMS_CRC_DIFF=pass") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "GENKSYMS_CRC_REFRESH=pass") == null);
}
