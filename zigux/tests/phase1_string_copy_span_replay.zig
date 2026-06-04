const std = @import("std");
const string = @import("string");

fn strlcatCompat(dest: []u8, src: []const u8) usize {
    if (@hasDecl(string, "strlcat")) {
        return string.strlcat(dest, src);
    }

    const dest_len = std.mem.indexOfScalar(u8, dest, 0) orelse dest.len;
    const src_len = std.mem.indexOfScalar(u8, src, 0) orelse src.len;
    if (dest_len == dest.len) {
        return dest.len + src_len;
    }

    const copy_len = @min(src_len, dest.len - dest_len - 1);
    if (copy_len != 0) {
        @memcpy(dest[dest_len .. dest_len + copy_len], src[0..copy_len]);
    }
    dest[dest_len + copy_len] = 0;
    return dest_len + src_len;
}

fn hasCopySpanSurface() bool {
    return @hasDecl(string, "memcpyAndPad") and
        @hasDecl(string, "strtomem") and
        @hasDecl(string, "memtostrPad") and
        @hasDecl(string, "strsep") and
        @hasDecl(string, "strspn") and
        @hasDecl(string, "strcspn") and
        @hasDecl(string, "strnchrNul");
}

test "string copy helpers preserve C-string and fixed-buffer boundaries" {
    var cat = [_]u8{ 'a', 'b', 0, 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 6), strlcatCompat(cat[0..], "cdef"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 'd', 0 }, cat[0..]);

    if (comptime hasCopySpanSurface()) {
        var padded = [_]u8{ 9, 9, 9, 9, 9, 9 };
        string.memcpyAndPad(padded[0..], "abcd", 3, '.');
        try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', '.', '.', '.' }, padded[0..]);

        var raw = [_]u8{ 9, 9, 9, 9 };
        string.strtomem(raw[0..], &[_]u8{ 'o', 'k', 0, 'x' });
        try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 9, 9 }, raw[0..]);

        var cstr = [_]u8{ 8, 8, 8, 8, 8 };
        string.memtostrPad(cstr[0..], &[_]u8{ 'z', 'i', 'g' });
        try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0 }, cstr[0..]);
    }
}

test "string span and split helpers stop at C-string fences" {
    if (comptime !hasCopySpanSurface()) {
        try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c' }, 3, 'b'));
        try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
        return;
    }

    const source = [_]u8{ 'a', 'b', 'c', 0, 'x' };
    const accept = [_]u8{ 'a', 'b', 0, 'c' };
    const reject = [_]u8{ 'x', 0, 'c' };
    try std.testing.expectEqual(@as(usize, 2), string.strspn(&source, &accept));
    try std.testing.expectEqual(@as(usize, 3), string.strcspn(&source, &reject));

    var split = [_]u8{ 'k', ':', 'v', 0, ':', 'x' };
    var cursor: ?[]u8 = split[0..];
    const delimiters = [_]u8{ ':', 0, 'v' };
    try std.testing.expectEqualStrings("k", string.strsep(&cursor, &delimiters).?);
    try std.testing.expectEqualStrings("v", string.strsep(&cursor, &delimiters).?);
    try std.testing.expectEqual(@as(?[]u8, null), cursor);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'k', 0, 'v', 0, ':', 'x' }, split[0..]);

    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul(&[_]u8{ 'a', 0, 'b' }, 3, 'z'));
    try std.testing.expectEqual(@as(usize, 3), string.strnchrNul("abc", 3, 'z'));
}
