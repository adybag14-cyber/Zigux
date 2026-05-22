const std = @import("std");
const string = @import("string");

test "phase1 string prefix-suffix replay keeps prefix checks inside C-string boundaries" {
    const prefix_cstr = [_]u8{ 'm', 'o', 0, 'd' };
    const truncated_haystack = [_]u8{ 'm', 'o', 0, 'd', 'e' };

    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix("mode", &prefix_cstr));
    try std.testing.expectEqual(@as(usize, 2), string.str_has_prefix("mode", &prefix_cstr));
    try std.testing.expect(string.strstarts("mode", &prefix_cstr));

    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&truncated_haystack, "mode"));
    try std.testing.expect(!string.strstarts(&truncated_haystack, "mode"));
}

test "phase1 string prefix-suffix replay keeps suffix checks inside C-string boundaries" {
    const haystack_cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    const suffix_cstr = [_]u8{ 'd', 'e', 0, 'x' };
    const truncated_haystack = [_]u8{ 'm', 'o', 'd', 0, 'e' };

    try std.testing.expect(string.strEndsWith(&haystack_cstr, "de"));
    try std.testing.expect(string.str_ends_with("mode", &suffix_cstr));
    try std.testing.expect(!string.strEndsWith(&haystack_cstr, "dex"));
    try std.testing.expect(!string.strEndsWith(&truncated_haystack, "de"));
}

test "phase1 string prefix-suffix replay keeps embedded-NUL peer comparisons stable" {
    const haystack_cstr = [_]u8{ 'z', 'i', 'g', 0, 'x' };
    const prefix_cstr = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };
    const suffix_cstr = [_]u8{ 'i', 'g', 0, 'u', 'x' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&haystack_cstr, &prefix_cstr));
    try std.testing.expect(string.strstarts(&haystack_cstr, &prefix_cstr));
    try std.testing.expect(string.strEndsWith(&haystack_cstr, &suffix_cstr));
    try std.testing.expect(string.str_ends_with(&haystack_cstr, &suffix_cstr));
}
