const std = @import("std");
const vsprintf = @import("vsprintf");

test "phase1 vsprintf render overflow returns zero and preserves caller buffers" {
    const oversized = [_]u8{'x'} ** (vsprintf.max_render_bytes + 8);

    var direct = [_]u8{0xaa} ** 6;
    var alias = [_]u8{0xbb} ** 6;

    const direct_written = vsprintf.scnprintf(&direct, "{s}", .{oversized[0..]});
    const alias_written = vsprintf.vscnprintf(&alias, "{s}", .{oversized[0..]});

    try std.testing.expectEqual(@as(usize, 0), direct_written);
    try std.testing.expectEqual(@as(usize, 0), alias_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa }, &direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb }, &alias);
}

test "phase1 scnprintfPad truncates to logical size without adding spaces once full" {
    var buffer = [_]u8{0xcc} ** 6;
    const written = vsprintf.scnprintfPad(&buffer, 4, "{s}", .{"alphabet"});

    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'l', 'p', 'h', 0, 0xcc }, &buffer);
}

test "phase1 vscnprintf zero-length caller views leave backing storage untouched" {
    var backing = [_]u8{0xdd};
    const written = vsprintf.vscnprintf(backing[0..0], "{s}", .{"zigux"});

    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0xdd), backing[0]);
}
