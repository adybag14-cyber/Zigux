const std = @import("std");
const argv_split = @import("argv_split");

test "argvSplit keeps mixed whitespace boundaries stable" {
    var result = try argv_split.argvSplit(std.testing.allocator, "\n\tzigux  lane07\r\nhelper\tpacket   ");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 4), result.argc());
    try std.testing.expectEqualStrings("zigux", result.argv[0]);
    try std.testing.expectEqualStrings("lane07", result.argv[1]);
    try std.testing.expectEqualStrings("helper", result.argv[2]);
    try std.testing.expectEqualStrings("packet", result.argv[3]);
}

test "argvFree resets the result shape after allocated tokens" {
    var result = try argv_split.argvSplit(std.testing.allocator, "alpha beta");
    try std.testing.expectEqual(@as(usize, 2), result.argc());

    argv_split.argvFree(&result);

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}

test "argvFree keeps empty parses reusable as zero-argument results" {
    var result = try argv_split.argvSplit(std.testing.allocator, " \n\t ");
    try std.testing.expectEqual(@as(usize, 0), result.argc());

    argv_split.argvFree(&result);

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}
