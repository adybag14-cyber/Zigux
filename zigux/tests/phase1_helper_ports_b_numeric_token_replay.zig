const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

const has_argv_result = @hasDecl(argv_split, "ArgvSplitResult");
const SplitResult = if (has_argv_result) argv_split.ArgvSplitResult else [][]u8;

fn splitArgs(allocator: std.mem.Allocator, text: []const u8) !SplitResult {
    return try argv_split.argvSplit(allocator, text);
}

fn freeArgs(allocator: std.mem.Allocator, result: *SplitResult) void {
    if (has_argv_result) {
        result.deinit();
    } else {
        argv_split.argvFree(allocator, result.*);
    }
}

fn argc(result: SplitResult) usize {
    return if (has_argv_result) result.argc() else result.len;
}

fn argAt(result: SplitResult, index: usize) []const u8 {
    return if (has_argv_result) result.argv[index] else result[index];
}

fn tokenMaskSummary(token: []const u8) u32 {
    var summary: u32 = 0;
    for (token) |ch| {
        summary |= @as(u32, ctype.mask(ch));
    }
    return summary;
}

test "numeric command-line tokens preserve split and parse boundaries" {
    var args = try splitArgs(std.testing.allocator, "mem=0x2AK root=0755K debug=1 quiet");
    defer freeArgs(std.testing.allocator, &args);

    try std.testing.expectEqual(@as(usize, 4), argc(args));
    try std.testing.expectEqualStrings("mem=0x2AK", argAt(args, 0));
    try std.testing.expectEqualStrings("root=0755K", argAt(args, 1));
    try std.testing.expectEqualStrings("debug=1", argAt(args, 2));
    try std.testing.expectEqualStrings("quiet", argAt(args, 3));

    try std.testing.expect(cmdline.parseOptionStr("mem,root,debug,quiet", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("mem,root,debug=1,quiet", "debug"));

    const hex_value = cmdline.memparse(argAt(args, 0)["mem=".len..]);
    try std.testing.expectEqual(@as(u64, 0x2a << 10), hex_value.value);
    try std.testing.expectEqualStrings("", hex_value.rest);

    const octal_value = cmdline.memparse(argAt(args, 1)["root=".len..]);
    try std.testing.expectEqual(@as(u64, 0o755 << 10), octal_value.value);
    try std.testing.expectEqualStrings("", octal_value.rest);
}

test "token classification and hweight masks stay aligned" {
    const token = "mem=0x2AK";
    const summary = tokenMaskSummary(token);

    try std.testing.expect((summary & ctype._L) != 0);
    try std.testing.expect((summary & ctype._D) != 0);
    try std.testing.expect((summary & ctype._P) != 0);
    try std.testing.expect((summary & ctype._X) != 0);
    try std.testing.expect(!ctype.isspace('='));
    try std.testing.expect(ctype.ispunct('='));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));

    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight8(summary));
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight16(summary));
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight32(summary));
    try std.testing.expectEqual(@as(u64, 5), hweight.swHweight64(summary));
    try std.testing.expectEqual(@as(usize, 5), hweight.hweightLong(summary));
}
