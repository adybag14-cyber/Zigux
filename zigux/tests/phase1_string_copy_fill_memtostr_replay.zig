const std = @import("std");
const string = @import("string");

test "phase1 string copy-fill replay keeps raw copy helpers aligned" {
    const raw_src = [_]u8{ 'a', 0, 'b', 'c', 'd' };

    var direct = [_]u8{ 9, 9, 9, 9, 9, 9 };
    var alias = [_]u8{ 8, 8, 8, 8, 8, 8 };

    string.memcpyAndPad(direct[0..], &raw_src, 4, '.');
    string.memcpy_and_pad(alias[0..], &raw_src, 4, '.');

    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 0, 'b', 'c', '.', '.' }, direct[0..]);
    try std.testing.expectEqualSlices(u8, direct[0..], alias[0..]);
}

test "phase1 string copy-fill replay keeps strtomem boundaries explicit" {
    const cstr_src = [_]u8{ 'h', 'i', 0, 'x' };

    var copied = [_]u8{ 9, 9, 9, 9, 9 };
    string.strtomem(copied[0..], &cstr_src);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 9, 9, 9 }, copied[0..]);

    var padded = [_]u8{ 7, 7, 7, 7, 7 };
    string.strtomem_pad(padded[0..], &cstr_src, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', '.', '.', '.' }, padded[0..]);
}

test "phase1 string copy-fill replay keeps memtostr termination and padding aligned" {
    var bounded = [_]u8{ 9, 9, 9, 9, 9 };
    string.memtostr(bounded[0..], &[_]u8{ 'o', 'k', '!' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', '!', 0, 9 }, bounded[0..]);

    var embedded_nul = [_]u8{ 9, 9, 9, 9, 9 };
    string.memtostr(embedded_nul[0..], &[_]u8{ 'h', 'i', 0, 'x' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 9, 9 }, embedded_nul[0..]);

    var padded = [_]u8{ 9, 9, 9, 9, 9 };
    string.memtostrPad(padded[0..], &[_]u8{ 'a', 'b', 'c' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0, 0 }, padded[0..]);

    var alias_single = [_]u8{7};
    string.memtostr_pad(alias_single[0..], &[_]u8{'y'});
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, alias_single[0..]);
}
