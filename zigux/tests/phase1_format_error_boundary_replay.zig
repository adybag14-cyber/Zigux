const std = @import("std");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");

test "phase1 format helper clamps logical size and preserves caller tail" {
    var exact = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const exact_written = vsprintf.scnprintfPad(&exact, 5, "{s}", .{"abcdef"});

    try std.testing.expectEqual(@as(usize, 5), exact_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 'd', 'e', 0, 0xaa, 0xaa }, &exact);

    var padded = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb };
    const padded_written = vsprintf.scnprintfPad(&padded, 7, "{s}", .{"ok"});

    try std.testing.expectEqual(@as(usize, 7), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', 0, 0xbb }, &padded);
}

test "phase1 format and strerror helpers keep subview boundaries explicit" {
    var buffer = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    const prefix_written = vsprintf.scnprintf(&buffer, "err={d}", .{4096});

    try std.testing.expectEqual(@as(usize, 8), prefix_written);
    try std.testing.expectEqualStrings("err=4096", buffer[0..prefix_written]);
    try std.testing.expectEqual(@as(u8, 0), buffer[prefix_written]);

    const suffix = str_error_r.strErrorR(22, buffer[4..]);
    try std.testing.expectEqualStrings("Inva", suffix);
    try std.testing.expectEqualStrings("err=", buffer[0..4]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'e', 'r', 'r', '=', 'I', 'n', 'v', 'a', 0 }, &buffer);
}

test "phase1 strerror fallback reports the active caller buffer length after truncation" {
    var short = [_]u8{ 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd };
    const short_rendered = str_error_r.strErrorR(4096, &short);

    try std.testing.expectEqualStrings("INTERNAL ", short_rendered);
    try std.testing.expectEqual(@as(u8, 0), short[short.len - 1]);

    var full: [64]u8 = undefined;
    const full_rendered = str_error_r.strErrorR(4096, &full);

    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 64)=22", full_rendered);
}
