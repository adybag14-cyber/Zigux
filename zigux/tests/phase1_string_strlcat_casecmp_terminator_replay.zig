const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps strlcat destination handling explicit" {
    var embedded_dest = [_]u8{ 'a', 0, 'x', 'x', 'x' };
    const embedded_src = [_]u8{ 'b', 'c', 0, 'd', 'e' };
    try std.testing.expectEqual(@as(usize, 3), string.strlcat(embedded_dest[0..], &embedded_src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0, 'x' }, embedded_dest[0..]);

    var truncated_dest = [_]u8{ 'a', 'b', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated_dest[0..], "cdef"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, truncated_dest[0..]);

    var unterminated_dest = [_]u8{ 'a', 'b', 'c' };
    try std.testing.expectEqual(@as(usize, 6), string.strlcat(unterminated_dest[0..], "xyz"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c' }, unterminated_dest[0..]);

    var empty_dest = [_]u8{};
    try std.testing.expectEqual(@as(usize, 3), string.strlcat(empty_dest[0..], "zig"));
}

test "phase1 string replay keeps casecmp boundaries explicit" {
    try std.testing.expect(string.strcasecmp("Kernel", "kernel") == 0);
    try std.testing.expect(string.strcasecmp(&[_]u8{ 'A', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }) == 0);
    try std.testing.expect(string.strcasecmp(&[_]u8{ 'A', 0, 'z' }, "ab") < 0);
    try std.testing.expect(string.strcasecmp("ab", &[_]u8{ 'A', 0, 'z' }) > 0);

    try std.testing.expect(string.strncasecmp("AbCdEf", "aBcXEf", 3) == 0);
    try std.testing.expect(string.strncasecmp("AbCdEf", "aBcXEf", 4) < 0);
    try std.testing.expect(string.strncasecmp("aBcXEf", "AbCdEf", 4) > 0);
    try std.testing.expect(string.strncasecmp(&[_]u8{ 'A', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }, 3) == 0);
    try std.testing.expect(string.strncasecmp("abcdef", "ABCXYZ", 0) == 0);
}

test "phase1 string replay keeps match-or-terminator boundaries explicit" {
    const with_nul = [_]u8{ 'a', 0, 'b', 'c' };
    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul(&with_nul, 4, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&with_nul, 4, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&with_nul, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&with_nul, 'z'));

    try std.testing.expectEqual(@as(usize, 3), string.strnchrNul("abc", 3, 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strnchrnul("abc", 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 3), string.strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&[_]u8{ 'a', 'b', 0 }, 'b'));
}
