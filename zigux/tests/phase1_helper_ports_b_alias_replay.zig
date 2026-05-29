const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "phase1 helper ports B keep exported aliases aligned" {
    var argv = try argv_split.argv_split(std.testing.allocator, " console=ttyS0 quiet debug ");
    defer argv_split.argv_free(&argv);

    try std.testing.expectEqual(@as(usize, 3), argv.argc());
    try std.testing.expectEqualStrings("console=ttyS0", argv.argv[0]);
    try std.testing.expectEqualStrings("quiet", argv.argv[1]);
    try std.testing.expectEqualStrings("debug", argv.argv[2]);

    try std.testing.expect(cmdline.parse_option_str("quiet,debug,nohlt", "debug"));

    const parsed = cmdline.next_arg("root=\"/dev/sda1 quiet\" panic=-1") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", parsed.value.?);
    try std.testing.expectEqualStrings("panic=-1", parsed.remaining);

    try std.testing.expectEqual(ctype.mask('A'), ctype._U | ctype._X);
    try std.testing.expectEqual(@as(u8, 'q'), ctype.tolower('Q'));

    try std.testing.expectEqual(hweight.swHweight8(0b1010_0101), hweight.__sw_hweight8(0b1010_0101));
    try std.testing.expectEqual(hweight.swHweight16(0xf0f0), hweight.__sw_hweight16(0xf0f0));
    try std.testing.expectEqual(hweight.swHweight32(0x1234_abcd), hweight.__sw_hweight32(0x1234_abcd));
    try std.testing.expectEqual(hweight.swHweight64(0x1234_abcd_5678_ffff), hweight.__sw_hweight64(0x1234_abcd_5678_ffff));
    try std.testing.expectEqual(hweight.hweightLong(0xf0f0), hweight.hweight_long(0xf0f0));
}
