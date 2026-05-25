const std = @import("std");
const vsprintf = @import("vsprintf");

test "phase1 vsprintf max-render guard leaves direct alias and padded callers untouched" {
    const oversized = [_]u8{'x'} ** (vsprintf.max_render_bytes + 1);

    var direct = [_]u8{0xaa} ** 5;
    var alias = [_]u8{0xbb} ** 5;
    var padded = [_]u8{0xcc} ** 5;

    const direct_written = vsprintf.scnprintf(&direct, "{s}", .{oversized[0..]});
    const alias_written = vsprintf.vscnprintf(&alias, "{s}", .{oversized[0..]});
    const padded_written = vsprintf.scnprintfPad(&padded, padded.len - 1, "{s}", .{oversized[0..]});

    try std.testing.expectEqual(@as(usize, 0), direct_written);
    try std.testing.expectEqual(@as(usize, 0), alias_written);
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa }, &direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb }, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc }, &padded);
}

test "phase1 scnprintfPad logical-size-one truncation keeps a terminator slot" {
    var buffer = [_]u8{0xdd} ** 4;
    const written = vsprintf.scnprintfPad(&buffer, 1, "{s}", .{"zigux"});

    try std.testing.expectEqual(@as(usize, 1), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 0xdd, 0xdd }, &buffer);
}

test "phase1 scnprintfPad empty render pads a single logical byte then returns zero" {
    var buffer = [_]u8{0xee} ** 4;
    const written = vsprintf.scnprintfPad(&buffer, 1, "{s}", .{""});

    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 0, 0xee, 0xee }, &buffer);
}
