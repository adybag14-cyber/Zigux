const std = @import("std");
const string = @import("string");

test "phase1 string search edges keep basename boundaries explicit" {
    try std.testing.expectEqualStrings("file.txt", string.kbasename("dir/file.txt"));
    try std.testing.expectEqualStrings("", string.kbasename("/"));
    try std.testing.expectEqualStrings("", string.kbasename("dir/"));

    const embedded_nul = [_]u8{ '/', 't', 'm', 'p', '/', 'o', 'k', 0, '/', 'b', 'a', 'd' };
    try std.testing.expectEqualStrings("ok", string.kbasename(&embedded_nul));
}

test "phase1 string search edges keep forward and reverse search inside the visible C-string" {
    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(?usize, 1), string.strchr(&cstr, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strchr(&cstr, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), string.strchr(&cstr, 0));

    const reverse = [_]u8{ 'a', 'b', 'a', 0, 'c', 'a' };
    try std.testing.expectEqual(@as(?usize, 2), string.strrchr(&reverse, 'a'));
    try std.testing.expectEqual(@as(?usize, 3), string.strrchr(&reverse, 0));

    const past_nul = [_]u8{ 'a', 0, 'b', 'a' };
    try std.testing.expectEqual(@as(?usize, 0), string.strrchr(&past_nul, 'a'));
    try std.testing.expectEqual(@as(?usize, null), string.strrchr(&past_nul, 'b'));
}

test "phase1 string search edges keep accept-set and bounded search semantics aligned" {
    try std.testing.expectEqual(@as(?usize, 1), string.strpbrk("abcd", "xzbc"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk("abcd", ""));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 0), string.strpbrk(&cstr, "ax"));
    try std.testing.expectEqual(@as(?usize, null), string.strpbrk(&cstr, "cd"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abcd", 1, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnlen("abcd", 2));
    try std.testing.expectEqual(@as(usize, 0), string.strnlen("abcd", 0));

    const bounded_cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&bounded_cstr, bounded_cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded_cstr, bounded_cstr.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnlen(&bounded_cstr, bounded_cstr.len));
}

test "phase1 string search edges keep nul-returning scans on the first stop point" {
    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(usize, 4), string.strnchrNul("abcd", 4, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul("abcd", 2, 'z'));
    try std.testing.expectEqual(@as(usize, 4), string.strchrNul("abcd", 'z'));
    try std.testing.expectEqual(@as(usize, 4), string.strchrnul("abcd", 'z'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(usize, 1), string.strnchrNul(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&cstr, cstr.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrnul(&cstr, cstr.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrNul(&cstr, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrnul(&cstr, 'z'));
}
