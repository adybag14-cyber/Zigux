const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");

fn sliceWithin(haystack: []const u8, needle: []const u8) bool {
    const haystack_start = @intFromPtr(haystack.ptr);
    const haystack_end = haystack_start + haystack.len;
    const needle_start = @intFromPtr(needle.ptr);
    const needle_end = needle_start + needle.len;
    return needle_start >= haystack_start and needle_end <= haystack_end;
}

test "phase1 cmdline argv borrowed replay keeps mixed whitespace tokenization owned and stable" {
    var source = [_]u8{ ' ', '\r', 'a', 'l', 'p', 'h', 'a', '\x0b', 'b', 'e', 't', 'a', '\x0c', 'g', 'a', 'm', 'm', 'a', '\t' };
    var split = try argv_split.argvSplit(std.testing.allocator, &source);
    defer split.deinit();

    try std.testing.expectEqual(@as(usize, 3), split.argc());
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);

    source[2] = 'Z';
    source[8] = 'Y';
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
}

test "phase1 cmdline argv borrowed replay keeps nextArg slices inside the caller buffer" {
    var buffer = [_]u8{ ' ', ' ', '"', 'm', 'o', 'd', 'e', '=', 'f', 'a', 's', 't', ' ', 'p', 'a', 't', 'h', '"', ' ', ' ', ' ', 'r', 'o', 'o', 't', '=', '/', 'd', 'e', 'v', '/', 'v', 'd', 'a', '1', ' ', ' ', ' ', 'q', 'u', 'i', 'e', 't', ' ', '\n' };
    const caller = buffer[0..];

    const first = cmdline.nextArg(caller) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", first.param);
    try std.testing.expectEqualStrings("fast path", first.value.?);
    try std.testing.expectEqualStrings("root=/dev/vda1   quiet \n", first.remaining);
    try std.testing.expect(sliceWithin(caller, first.param));
    try std.testing.expect(sliceWithin(caller, first.value.?));
    try std.testing.expect(sliceWithin(caller, first.remaining));

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", second.param);
    try std.testing.expectEqualStrings("/dev/vda1", second.value.?);
    try std.testing.expectEqualStrings("quiet \n", second.remaining);
    try std.testing.expect(sliceWithin(caller, second.param));
    try std.testing.expect(sliceWithin(caller, second.value.?));

    const third = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("quiet", third.param);
    try std.testing.expect(third.value == null);
    try std.testing.expectEqualStrings("", third.remaining);
    try std.testing.expect(sliceWithin(caller, third.param));
}

test "phase1 cmdline argv borrowed replay keeps signed prefix and bare option edges aligned" {
    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    try std.testing.expect(cmdline.parseOptionStr("rw,debug\x00,quiet", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("rw,debug\x00,quiet", "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
}
