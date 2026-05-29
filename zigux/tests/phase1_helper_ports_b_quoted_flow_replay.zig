const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn digitMask(text: []const u8) u32 {
    var result: u32 = 0;
    for (text, 0..) |ch, idx| {
        if (ctype.isdigit(ch)) {
            result |= @as(u32, 1) << @intCast(idx);
        }
    }
    return result;
}

fn punctuationMask(text: []const u8) u32 {
    var result: u32 = 0;
    for (text, 0..) |ch, idx| {
        if (ctype.ispunct(ch)) {
            result |= @as(u32, 1) << @intCast(idx);
        }
    }
    return result;
}

test "quoted cmdline values feed argv_split token classification" {
    const first = cmdline.nextArg("root=\"/dev/vda1 ro\" console=ttyS0,115200n8 quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", first.param);
    try std.testing.expectEqualStrings("/dev/vda1 ro", first.value.?);
    try std.testing.expectEqualStrings("console=ttyS0,115200n8 quiet", first.remaining);

    var split_root = try argv_split.argvSplit(std.testing.allocator, first.value.?);
    defer split_root.deinit();
    try std.testing.expectEqual(@as(usize, 2), split_root.argc());
    try std.testing.expectEqualStrings("/dev/vda1", split_root.argv[0]);
    try std.testing.expectEqualStrings("ro", split_root.argv[1]);

    const root_digits = digitMask(split_root.argv[0]);
    const root_punct = punctuationMask(split_root.argv[0]);
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight32(root_digits));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(root_punct));
    try std.testing.expect(ctype.isalpha(split_root.argv[1][0]));
    try std.testing.expect(ctype.isalpha(split_root.argv[1][1]));

    const second = cmdline.next_arg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("console", second.param);
    try std.testing.expectEqualStrings("ttyS0,115200n8", second.value.?);
    try std.testing.expectEqualStrings("quiet", second.remaining);

    const console_digits = digitMask(second.value.?);
    const console_punct = punctuationMask(second.value.?);
    try std.testing.expectEqual(@as(u32, 8), hweight.__sw_hweight32(console_digits));
    try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight32(console_punct));
    try std.testing.expect(cmdline.parseOptionStr("ro,quiet,console", second.remaining));
}

test "quoted numeric tokens keep memparse rest and class masks aligned" {
    const parsed = cmdline.nextArg("mem=\"64K low\" panic=-1") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mem", parsed.param);
    try std.testing.expectEqualStrings("64K low", parsed.value.?);
    try std.testing.expectEqualStrings("panic=-1", parsed.remaining);

    var split_mem = try argv_split.argv_split(std.testing.allocator, parsed.value.?);
    defer argv_split.argv_free(&split_mem);
    try std.testing.expectEqual(@as(usize, 2), split_mem.argc());

    const amount = cmdline.memparse(split_mem.argv[0]);
    try std.testing.expectEqual(@as(u64, 64 << 10), amount.value);
    try std.testing.expectEqualStrings("", amount.rest);

    const amount_digits = digitMask(split_mem.argv[0]);
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(amount_digits));
    try std.testing.expect(ctype.isupper(split_mem.argv[0][2]));
    try std.testing.expectEqual(@as(u8, 'k'), ctype.fastTolower(split_mem.argv[0][2]));

    const panic = cmdline.next_arg(parsed.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("panic", panic.param);
    try std.testing.expectEqualStrings("-1", panic.value.?);
    try std.testing.expectEqualStrings("", panic.remaining);

    const panic_value = cmdline.memparse(panic.value.?);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -1))), panic_value.value);
    try std.testing.expectEqualStrings("", panic_value.rest);
    try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight8(punctuationMask(panic.value.?)));
    try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight8(digitMask(panic.value.?)));
}
