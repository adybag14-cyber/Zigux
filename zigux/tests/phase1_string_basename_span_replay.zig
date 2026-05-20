const std = @import("std");
const string = @import("string");

test "phase1 string replay keeps basename and span helpers inside C-string bounds" {
    const path = [_]u8{
        '/', 's', 'y', 's', '/', 'd', 'e', 'v', 'i', 'c', 'e', 's', '/',
        'z', 'i', 'g', 'u', 'x', '0', 0,   '/', 'x',
    };
    const slashy = [_]u8{ '/', 'm', 'o', 'd', 'e', 0, 'x' };
    const accept_only_x = [_]u8{ 'x', 0, '/' };
    const accept_slash_or_digit = [_]u8{ '/', '0', 0, 'x' };
    const prefix = [_]u8{ '/', '/', '/', 'z', 'i', 'g', 0, '/' };

    try std.testing.expectEqualStrings("zigux0", string.kbasename(path[0..]));
    try std.testing.expectEqual(@as(?usize, 12), string.strrchr(path[0..], '/'));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(slashy[0..], accept_only_x[0..]));
    try std.testing.expectEqual(@as(?usize, 0), string.strpbrk(path[0..], accept_slash_or_digit[0..]));
    try std.testing.expectEqual(@as(usize, 3), string.strspn(prefix[0..], "/"));
    try std.testing.expectEqual(@as(usize, 1), string.strspn("0x1", accept_slash_or_digit[0..]));
}

test "phase1 string replay keeps counted NUL-fallback searches aligned" {
    const cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, '-', 'x' };
    const missing = [_]u8{ 'z', 'i', 'g', 0, 'x' };

    try std.testing.expectEqual(@as(usize, 4), string.strchrNul(cstr[0..], '-'));
    try std.testing.expectEqual(@as(usize, 4), string.strchrnul(cstr[0..], '-'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(cstr[0..], 2, 'd'));
    try std.testing.expectEqual(@as(usize, 4), string.strnchrnul(cstr[0..], cstr.len, '-'));
    try std.testing.expectEqual(@as(usize, 3), string.strnlen(missing[0..], missing.len));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(missing[0..], missing.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 2), string.strchr(missing[0..], 'g'));
}
