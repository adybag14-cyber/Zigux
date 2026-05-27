const std = @import("std");
const string = @import("string");

test "trimSpaces trims outer whitespace without shifting the caller prefix" {
    var buf = [_]u8{ ' ', '\t', 'x', ' ', 'y', ' ', '\n' };

    const trimmed = string.trimSpaces(&buf);

    try std.testing.expectEqualStrings("x y", trimmed);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ ' ', '\t', 'x', ' ', 'y', 0, '\n' },
        &buf,
    );
}

test "removeSpaces compacts the trimmed subslice and preserves bytes before it" {
    var buf = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'q' };

    const trimmed = string.strim(&buf);
    const compacted = string.removeSpaces(trimmed);

    try std.testing.expectEqualStrings("ab", compacted);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ ' ', 'a', 'b', 0, 0, 0, 'q' },
        &buf,
    );
}

test "replaceChar aliases stop at embedded NUL inside a caller subslice" {
    var buf = [_]u8{ '#', '-', 'x', 0, '-', 'y' };

    const replaced_len = string.replaceChar(buf[1..], '-', '+');
    try std.testing.expectEqual(@as(usize, 2), replaced_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '+', 'x', 0, '-', 'y' }, &buf);

    var alias_buf = [_]u8{ '#', '-', 'x', 0, '-', 'y' };
    const alias_len = string.strreplace(alias_buf[1..], '-', '+');
    try std.testing.expectEqual(@as(usize, 2), alias_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '+', 'x', 0, '-', 'y' }, &alias_buf);
}
