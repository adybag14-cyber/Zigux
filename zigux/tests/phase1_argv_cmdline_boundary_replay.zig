const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");

fn expectArgv(result: *const argv_split.ArgvSplitResult, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, result.argc());
    try std.testing.expectEqual(expected.len, result.argv.len);
    for (expected, result.argv) |want, got| {
        try std.testing.expectEqualStrings(want, got);
    }
}

test "argv split result owns reusable duplicated tokens" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "  root=/dev/vda  console=ttyS0,115200\tpanic=-1 ",
    );
    defer argv_split.argvFree(&split);

    try expectArgv(&split, &.{ "root=/dev/vda", "console=ttyS0,115200", "panic=-1" });
    split.argv[1][0] = 'C';
    try std.testing.expectEqualStrings("Console=ttyS0,115200", split.argv[1]);

    var second = try argv_split.argv_split(std.testing.allocator, "init=/init quiet");
    defer argv_split.argv_free(&second);
    try expectArgv(&second, &.{ "init=/init", "quiet" });
}

test "argv split preserves embedded nul tokens and clears result on free" {
    var split = try argv_split.argv_split(std.testing.allocator, "key=value path\\name\x00tail");
    try expectArgv(&split, &.{ "key=value", "path\\name\x00tail" });
    try std.testing.expectEqual(@as(u8, 0), split.argv[1][9]);

    argv_split.argv_free(&split);
    try std.testing.expectEqual(@as(usize, 0), split.argc());
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
}

test "cmdline option and memparse boundaries stay fenced" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug\x00late", ""));
    try std.testing.expect(cmdline.parse_option_str("quiet,,debug\x00late", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,,debug\x00late", "late"));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));

    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const invalid_signed = cmdline.memparse("+not-a-number");
    try std.testing.expectEqual(@as(u64, 0), invalid_signed.value);
    try std.testing.expectEqualStrings("+not-a-number", invalid_signed.rest);
}
