const std = @import("std");
const vsprintf = @import("vsprintf");

test "phase1 vsprintf terminator window replay keeps scnprintf and vscnprintf aligned on terminator-only views" {
    var direct = [_]u8{0xaa};
    var alias = [_]u8{0xbb};

    const direct_written = vsprintf.scnprintf(&direct, "{s}", .{"zigux"});
    const alias_written = vsprintf.vscnprintf(&alias, "{s}", .{"zigux"});

    try std.testing.expectEqual(@as(usize, 0), direct_written);
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqual(@as(u8, 0), direct[0]);
    try std.testing.expectEqual(@as(u8, 0), alias[0]);
}

test "phase1 vsprintf terminator window replay keeps exact-fit renders inside the caller terminator slot" {
    var exact = [_]u8{0xdd} ** 5;
    const exact_written = vsprintf.scnprintf(&exact, "{s}", .{"four"});

    try std.testing.expectEqual(@as(usize, 4), exact_written);
    try std.testing.expectEqualStrings("four", exact[0..exact_written]);
    try std.testing.expectEqual(@as(u8, 0), exact[exact_written]);
}

test "phase1 vsprintf terminator window replay separates padded and clipped logical windows" {
    var padded = [_]u8{0xee} ** 6;
    const padded_written = vsprintf.scnprintfPad(&padded, 5, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, &padded);

    var clipped = [_]u8{0xff} ** 5;
    const clipped_written = vsprintf.scnprintfPad(&clipped, 3, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 3), clipped_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0, 0xff }, &clipped);
}
