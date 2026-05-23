const std = @import("std");
const string = @import("string");

test "phase1 string memchrInv keeps the earliest dirty byte across long windows" {
    var buf = [_]u8{0} ** 32;
    buf[21] = 4;
    try std.testing.expectEqual(@as(?usize, 21), string.memchrInv(buf[0..], 0));

    buf[7] = 1;
    try std.testing.expectEqual(@as(?usize, 7), string.memchrInv(buf[0..], 0));

    for (0..@sizeOf(usize)) |offset| {
        var backing = [_]u8{7} ** 40;
        backing[offset + 11] = 5;
        try std.testing.expectEqual(@as(?usize, 11), string.memchrInv(backing[offset .. offset + 32], 7));
    }
}

test "phase1 string memchr_inv mirrors memchrInv around the fast-path cutoff" {
    var short = [_]u8{0} ** (@sizeOf(usize) * 2 - 1);
    short[short.len - 1] = 1;
    try std.testing.expectEqual(string.memchrInv(short[0..], 0), string.memchr_inv(short[0..], 0));

    var long = [_]u8{0} ** (@sizeOf(usize) * 2);
    long[long.len - 1] = 1;
    try std.testing.expectEqual(string.memchrInv(long[0..], 0), string.memchr_inv(long[0..], 0));
}

test "phase1 string strnchr keeps count and embedded-NUL boundaries aligned" {
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(?usize, 0), string.strnchr(&[_]u8{ 'b', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 0, 'a'));
}
