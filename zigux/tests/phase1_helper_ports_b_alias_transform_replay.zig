const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "helper ports b aliases remain wired to primary entrypoints" {
    var split = try argv_split.argv_split(std.testing.allocator, " \talpha beta\n gamma  ");
    defer argv_split.argv_free(&split);

    try std.testing.expectEqual(@as(usize, 3), split.argc());
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);

    try std.testing.expect(cmdline.parse_option_str("quiet,debug\x00,nohlt", "debug"));
    try std.testing.expect(!cmdline.parse_option_str("quiet,debug\x00,nohlt", "nohlt"));

    try std.testing.expectEqual(hweight.swHweight8(0xa5), hweight.__sw_hweight8(0xa5));
    try std.testing.expectEqual(hweight.swHweight16(0xa55a), hweight.__sw_hweight16(0xa55a));
    try std.testing.expectEqual(hweight.swHweight32(0xa55a_9669), hweight.__sw_hweight32(0xa55a_9669));
    try std.testing.expectEqual(
        hweight.swHweight64(0xa55a_9669_f00f_0ff0),
        hweight.__sw_hweight64(0xa55a_9669_f00f_0ff0),
    );
    try std.testing.expectEqual(hweight.hweightLong(0xa55a), hweight.hweight_long(0xa55a));
}

test "cmdline and ctype transforms preserve cursor and case boundaries" {
    const first = cmdline.next_arg("\"mode=fast boot\" root=/dev/sda1") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", first.param);
    try std.testing.expectEqualStrings("fast boot", first.value.?);
    try std.testing.expectEqualStrings("root=/dev/sda1", first.remaining);

    const suffix = cmdline.memparse("+0x10K,tail");
    try std.testing.expectEqual(@as(u64, 0x10 << 10), suffix.value);
    try std.testing.expectEqualStrings(",tail", suffix.rest);

    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower('A'));
    try std.testing.expectEqual(@as(u8, 'A'), ctype.toupper('a'));
    try std.testing.expectEqual(@as(u8, 'z'), ctype.fastTolower('Z'));
    try std.testing.expectEqual(@as(u8, 0x7f), ctype.toascii(0xff));
    try std.testing.expect(ctype.isascii(0x7f));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isxdigit('g'));
}

test "hweight narrow helpers count only their owned lanes" {
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(0xffff_ff00));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight16(0xffff_0000));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight16(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xf0f0_0f0f));
    try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_0f0f_f00f_0ff0));
}
