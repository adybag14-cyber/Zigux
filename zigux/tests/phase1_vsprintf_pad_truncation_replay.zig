const std = @import("std");
const vsprintf = @import("vsprintf");

test "phase1 vsprintf replay keeps truncation and alias writes aligned" {
    var direct = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    var alias = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb };

    const direct_written = vsprintf.scnprintf(&direct, "{s}:{d}", .{ "zigux", 42 });
    const alias_written = vsprintf.vscnprintf(&alias, "{s}:{d}", .{ "zigux", 42 });

    try std.testing.expectEqual(@as(usize, 5), direct_written);
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqualStrings("zigux", direct[0..direct_written]);
    try std.testing.expectEqualStrings(direct[0..direct_written], alias[0..alias_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[direct_written]);
    try std.testing.expectEqual(@as(u8, 0), alias[alias_written]);
}

test "phase1 vsprintf replay keeps padding bounded by logical size" {
    var padded = [_]u8{0xcc} ** 8;
    const written = vsprintf.scnprintfPad(&padded, 6, "{s}", .{"id"});

    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', ' ', ' ', 0, 0xcc }, &padded);
}

test "phase1 vsprintf replay clamps oversized logical size and preserves zero-sized callers" {
    var clamped = [_]u8{0xdd} ** 5;
    const clamped_written = vsprintf.scnprintfPad(&clamped, 99, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 3), clamped_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', 0 }, &clamped);

    var zero_logical = [_]u8{0xee} ** 3;
    const zero_logical_written = vsprintf.scnprintfPad(&zero_logical, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), zero_logical_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0xee, 0xee }, &zero_logical);

    var empty_backing = [_]u8{0xf0};
    const empty_written = vsprintf.scnprintf(empty_backing[0..0], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0xf0), empty_backing[0]);
}
