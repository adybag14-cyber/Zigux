const std = @import("std");
const cmdline = @import("cmdline");

fn sliceOffset(source: []const u8, subslice: []const u8) usize {
    return @intFromPtr(subslice.ptr) - @intFromPtr(source.ptr);
}

test "phase1 cmdline token-boundary replay keeps quoted bare tokens borrowed" {
    const source = "\"two words\" tail";
    const parsed = cmdline.nextArg(source) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqualStrings("two words", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.remaining);

    try std.testing.expectEqual(std.mem.indexOf(u8, source, "two words").?, sliceOffset(source, parsed.param));
    try std.testing.expectEqual(std.mem.indexOf(u8, source, "tail").?, sliceOffset(source, parsed.remaining));
}

test "phase1 cmdline token-boundary replay keeps unterminated quoted values borrowed and terminal" {
    const source = "mode=\"fast boot";
    const parsed = cmdline.nextArg(source) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqualStrings("mode", parsed.param);
    try std.testing.expectEqualStrings("fast boot", parsed.value.?);
    try std.testing.expectEqualStrings("", parsed.remaining);

    try std.testing.expectEqual(std.mem.indexOf(u8, source, "mode").?, sliceOffset(source, parsed.param));
    try std.testing.expectEqual(std.mem.indexOf(u8, source, "fast boot").?, sliceOffset(source, parsed.value.?));
    try std.testing.expectEqual(source.len, sliceOffset(source, parsed.remaining));
}

test "phase1 cmdline token-boundary replay keeps NUL-stopped option scans and alias semantics aligned" {
    try std.testing.expect(cmdline.parseOptionStr(",\x00beta", ""));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,\x00beta", ""));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,\x00beta", "beta"));
    try std.testing.expect(cmdline.parseOptionStr("alpha,beta,\x00tail", "beta"));
    try std.testing.expect(cmdline.parse_option_str("debug,quiet", "quiet"));
}

test "phase1 cmdline token-boundary replay keeps unsigned overflow suffix rest aligned" {
    const overflow = cmdline.memparse("18446744073709551615Ktail");
    try std.testing.expectEqual(std.math.maxInt(u64), overflow.value);
    try std.testing.expectEqualStrings("tail", overflow.rest);

    const positive_invalid = cmdline.memparse("+xyz");
    try std.testing.expectEqual(@as(u64, 0), positive_invalid.value);
    try std.testing.expectEqualStrings("+xyz", positive_invalid.rest);
}
