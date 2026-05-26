const std = @import("std");
const vsprintf = @import("vsprintf");

test "phase1 scnprintfPad keeps single-byte logical-size exact fits unpadded" {
    var buffer = [_]u8{0xaa} ** 4;
    const written = vsprintf.scnprintfPad(&buffer, 1, "{s}", .{"z"});

    try std.testing.expectEqual(@as(usize, 1), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 0xaa, 0xaa }, &buffer);
}

test "phase1 scnprintfPad keeps empty single-byte logical sizes on the pad path" {
    var buffer = [_]u8{0xbb} ** 4;
    const written = vsprintf.scnprintfPad(&buffer, 1, "{s}", .{""});

    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 0, 0xbb, 0xbb }, &buffer);
}

test "phase1 scnprintfPad keeps exact-fit logical sizes free of trailing fill" {
    var buffer = [_]u8{0xcc} ** 6;
    const written = vsprintf.scnprintfPad(&buffer, 4, "{s}", .{"wxyz"});

    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'x', 'y', 'z', 0, 0xcc }, &buffer);
}
