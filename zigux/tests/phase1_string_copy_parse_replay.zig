const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps copy helpers aligned with embedded NUL and truncation" {
    const embedded = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };

    var strlcpy_dest = [_]u8{ 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 3), string.strlcpy(strlcpy_dest[0..], embedded[0..]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 'x' }, strlcpy_dest[0..]);

    var strscpy_dest = [_]u8{ 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(strscpy_dest[0..], "zigux"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 0 }, strscpy_dest[0..]);

    var padded_dest = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 3), string.strscpyPad(padded_dest[0..], embedded[0..]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0, 0 }, padded_dest[0..]);

    var alias_dest = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 3), string.strscpy_pad(alias_dest[0..], embedded[0..]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0, 0 }, alias_dest[0..]);
}

test "phase1 string replay keeps signed memparse suffixes and rest aligned" {
    const negative = string.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const clamped = string.memparse("+9223372036854775808Ktail");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), clamped.value);
    try std.testing.expectEqualStrings("tail", clamped.rest);

    const invalid = string.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("-xyz", invalid.rest);
}
