const std = @import("std");
const cmdline = @import("cmdline");

fn sliceOffset(source: []const u8, subslice: []const u8) usize {
    return @intFromPtr(subslice.ptr) - @intFromPtr(source.ptr);
}

test "phase1 cmdline replay keeps nextArg slices borrowed from the caller buffer" {
    const source = "  root=\"/dev/sda1 quiet\" debug=1";
    const parsed = cmdline.nextArg(source) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", parsed.value.?);
    try std.testing.expectEqualStrings("debug=1", parsed.remaining);

    try std.testing.expectEqual(std.mem.indexOf(u8, source, "root").?, sliceOffset(source, parsed.param));
    try std.testing.expectEqual(std.mem.indexOf(u8, source, "/dev/sda1 quiet").?, sliceOffset(source, parsed.value.?));
    try std.testing.expectEqual(std.mem.indexOf(u8, source, "debug=1").?, sliceOffset(source, parsed.remaining));
}

test "phase1 cmdline replay keeps exact bare-option matching aligned through alias exports" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug,\x00ignored", ""));
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug,\x00ignored", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet\x00debug", "debug"));
    try std.testing.expect(cmdline.parse_option_str(",profile", ""));
    try std.testing.expect(cmdline.parse_option_str("profile,quiet", "profile"));
}

test "phase1 cmdline replay keeps signed and invalid memparse edges aligned" {
    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    const positive_overflow = cmdline.memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), positive_overflow.value);
    try std.testing.expectEqualStrings("", positive_overflow.rest);

    const negative_invalid = cmdline.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), negative_invalid.value);
    try std.testing.expectEqualStrings("-xyz", negative_invalid.rest);
}

test "phase1 cmdline replay keeps quoted-token and empty-value handling aligned" {
    const quoted_pair = cmdline.nextArg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", quoted_pair.param);
    try std.testing.expectEqualStrings("fast path", quoted_pair.value.?);
    try std.testing.expectEqualStrings("tail", quoted_pair.remaining);

    const empty_value = cmdline.nextArg("flag=\"\" next") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("flag", empty_value.param);
    try std.testing.expectEqualStrings("", empty_value.value.?);
    try std.testing.expectEqualStrings("next", empty_value.remaining);
}
