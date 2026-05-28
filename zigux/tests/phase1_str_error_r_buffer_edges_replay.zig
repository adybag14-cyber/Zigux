const std = @import("std");
const str_error_r = @import("str_error_r");

test "str_error_r buffer edges preserve caller ownership" {
    var known = [_]u8{0xaa} ** 8;
    const known_rendered = str_error_r.strErrorR(13, &known);
    try std.testing.expectEqualStrings("Permiss", known_rendered);
    try std.testing.expectEqual(@as(usize, 7), known_rendered.len);
    try std.testing.expectEqual(@as(u8, 0), known[7]);

    var fallback = [_]u8{0xbb} ** 8;
    const fallback_rendered = str_error_r.strErrorR(4096, &fallback);
    try std.testing.expectEqualStrings("INTERNA", fallback_rendered);
    try std.testing.expectEqual(@as(usize, 7), fallback_rendered.len);
    try std.testing.expectEqual(@as(u8, 0), fallback[7]);
}

test "str_error_r zero length buffers return an empty borrowed slice" {
    var empty = [_]u8{};
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(13, empty[0..]).len);
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(4096, empty[0..]).len);
}

test "str_error_r exact one byte buffers write only the terminator" {
    var known = [_]u8{0xaa};
    const known_rendered = str_error_r.strErrorR(2, &known);
    try std.testing.expectEqualStrings("", known_rendered);
    try std.testing.expectEqual(@as(u8, 0), known[0]);

    var fallback = [_]u8{0xbb};
    const fallback_rendered = str_error_r.strErrorR(12345, &fallback);
    try std.testing.expectEqualStrings("", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0), fallback[0]);
}
