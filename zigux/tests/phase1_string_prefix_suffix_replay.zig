const std = @import("std");
const string = @import("string");

test "phase1 string prefix suffix replay keeps C-string prefix cutoffs and aliases aligned" {
    const text = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    const exact = [_]u8{ 'm', 'o', 'd', 'e', 0, 'y' };
    const longer = [_]u8{ 'm', 'o', 'd', 'e', 'x', 0 };

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&text, &exact));
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(&text, &exact));
    try std.testing.expect(string.strstarts(&text, &exact));

    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&text, &longer));
    try std.testing.expectEqual(@as(usize, 0), string.str_has_prefix(&text, &longer));
    try std.testing.expect(!string.strstarts(&text, &longer));
}

test "phase1 string prefix suffix replay keeps empty prefix and suffix false on the current surface" {
    const text = [_]u8{ 'z', 'i', 'g', 'u', 'x', 0 };
    const empty = [_]u8{0};

    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&text, &empty));
    try std.testing.expectEqual(@as(usize, 0), string.strHasSuffix(&text, &empty));
    try std.testing.expect(!string.strstarts(&text, &empty));
    try std.testing.expect(!string.strEndsWith(&text, &empty));
    try std.testing.expect(!string.str_ends_with(&text, &empty));
    try std.testing.expect(!string.strends(&text, &empty));
}

test "phase1 string prefix suffix replay keeps suffix cutoffs and aliases aligned" {
    const text = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', '-', 'm', 'o', 'd', 'e', 0, 'x' };
    const exact = [_]u8{ 'm', 'o', 'd', 'e', 0, 'y' };
    const longer = [_]u8{ '-', 'm', 'o', 'd', 'e', 'x', 0 };

    try std.testing.expectEqual(@as(usize, 4), string.strHasSuffix(&text, &exact));
    try std.testing.expectEqual(@as(usize, 4), string.str_has_suffix(&text, &exact));
    try std.testing.expect(string.strEndsWith(&text, &exact));
    try std.testing.expect(string.str_ends_with(&text, &exact));
    try std.testing.expect(string.strends(&text, &exact));

    try std.testing.expectEqual(@as(usize, 0), string.strHasSuffix(&text, &longer));
    try std.testing.expectEqual(@as(usize, 0), string.str_has_suffix(&text, &longer));
    try std.testing.expect(!string.strEndsWith(&text, &longer));
    try std.testing.expect(!string.str_ends_with(&text, &longer));
    try std.testing.expect(!string.strends(&text, &longer));
}

test "phase1 string prefix suffix replay ignores bytes after embedded NUL when matching suffixes" {
    const text = [_]u8{ 'a', 'b', 'c', 0, 't', 'a', 'i', 'l' };
    const exact = [_]u8{ 'b', 'c', 0, 'x' };
    const mismatch = [_]u8{ 'c', 'x', 0 };

    try std.testing.expectEqual(@as(usize, 2), string.strHasSuffix(&text, &exact));
    try std.testing.expect(string.strEndsWith(&text, &exact));
    try std.testing.expectEqual(@as(usize, 0), string.strHasSuffix(&text, &mismatch));
    try std.testing.expect(!string.strEndsWith(&text, &mismatch));
}
