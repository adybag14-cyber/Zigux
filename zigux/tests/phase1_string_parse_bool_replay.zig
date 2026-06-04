const std = @import("std");
const string = @import("string");

test "phase1 string strtobool keeps stable Linux first-token forms explicit" {
    try std.testing.expect(try string.strtobool("yes"));
    try std.testing.expect(try string.strtobool("Y=forced"));
    try std.testing.expect(try string.strtobool("On\n"));
    try std.testing.expect(try string.strtobool("1=forced"));

    try std.testing.expect(!(try string.strtobool("nope")));
    try std.testing.expect(!(try string.strtobool("N=clear")));
    try std.testing.expect(!(try string.strtobool("off\x00trailing")));
    try std.testing.expect(!(try string.strtobool("0=clear")));

    try std.testing.expectError(error.Invalid, string.strtobool(null));
    try std.testing.expectError(error.Invalid, string.strtobool(""));
    try std.testing.expectError(error.Invalid, string.strtobool("o"));
    try std.testing.expectError(error.Invalid, string.strtobool("+1"));
}

test "phase1 string memparse preserves base suffix and rest boundaries" {
    const hex_k = string.memparse("0x10K-rest");
    try std.testing.expectEqual(@as(u64, 16 * 1024), hex_k.value);
    try std.testing.expectEqualStrings("-rest", hex_k.rest);

    const octal = string.memparse("0755xyz");
    try std.testing.expectEqual(@as(u64, 493), octal.value);
    try std.testing.expectEqualStrings("xyz", octal.rest);

    const signed_suffix = string.memparse("-42Ktail");
    try std.testing.expectEqual(@as(i64, -42 * 1024), @as(i64, @bitCast(signed_suffix.value)));
    try std.testing.expectEqualStrings("tail", signed_suffix.rest);

    const plus_hex_suffix = string.memparse("+0x10Mrest");
    try std.testing.expectEqual(@as(u64, 16 * 1024 * 1024), plus_hex_suffix.value);
    try std.testing.expectEqualStrings("rest", plus_hex_suffix.rest);

    const no_digits = string.memparse("+x10");
    try std.testing.expectEqual(@as(u64, 0), no_digits.value);
    try std.testing.expectEqualStrings("+x10", no_digits.rest);
}

test "phase1 string memdup keeps embedded NUL bytes independent" {
    var source = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };
    const duplicate = try string.memdup(std.testing.allocator, &source);
    defer std.testing.allocator.free(duplicate);

    try std.testing.expectEqualSlices(u8, &source, duplicate);

    source[0] = 'Z';
    source[4] = 'U';
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 'u', 'x' }, duplicate);
    try std.testing.expectEqual(@as(u8, 0), duplicate[3]);
}
