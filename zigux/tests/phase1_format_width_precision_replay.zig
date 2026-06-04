const std = @import("std");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");

test "phase1 format helper preserves width precision and terminator boundaries" {
    var buffer: [24]u8 = @splat(0xaa);
    const written = vsprintf.scnprintf(&buffer, "{s: >8}|{d:0>4}|{d:.2}", .{
        "xy",
        37,
        @as(f64, 3.125),
    });

    try std.testing.expectEqual(@as(usize, 18), written);
    try std.testing.expectEqualStrings("      xy|0037|3.13", buffer[0..written]);
    try std.testing.expectEqual(@as(u8, 0), buffer[written]);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[written + 1]);
}

test "phase1 format helper truncates after formatted precision without clobbering tail" {
    var buffer: [12]u8 = @splat(0xbb);
    const written = vsprintf.vscnprintf(&buffer, "{d:.2}:{d:0>6}", .{
        @as(f64, 3.125),
        42,
    });

    try std.testing.expectEqual(@as(usize, 11), written);
    try std.testing.expectEqualStrings("3.13:000042", buffer[0..written]);
    try std.testing.expectEqual(@as(u8, 0), buffer[written]);
}

test "phase1 padded format keeps logical precision window and caller tail" {
    var buffer: [14]u8 = @splat(0xcc);
    const written = vsprintf.scnprintfPad(buffer[2..12], 8, "{d:.2}", .{@as(f64, 3.125)});

    try std.testing.expectEqual(@as(usize, 8), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc }, buffer[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '3', '.', '1', '3', ' ', ' ', ' ', ' ', 0, 0xcc }, buffer[2..12]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc }, buffer[12..14]);
}

test "phase1 strerror fallback reports zero active caller window" {
    var buffer = [_]u8{ 0xdd, 0xdd, 0xdd, 0xdd };
    const rendered = str_error_r.strErrorR(4096, buffer[1..1]);

    try std.testing.expectEqual(@as(usize, 0), rendered.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0xdd, 0xdd, 0xdd }, &buffer);
}
