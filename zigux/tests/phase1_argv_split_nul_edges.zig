const std = @import("std");
const argv_split = @import("argv_split");

test "phase1 argv_split NUL edges preserve embedded NUL bytes inside duplicated tokens" {
    const input = "root=/dev/vda rw\x00ignored debug";
    var result = try argv_split.argvSplit(std.testing.allocator, input);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("root=/dev/vda", result.argv[0]);
    try std.testing.expectEqualSlices(u8, "rw\x00ignored", result.argv[1]);
    try std.testing.expectEqualStrings("debug", result.argv[2]);
}

test "phase1 argv_split NUL edges keep duplicated argv storage detached from caller buffer" {
    var buffer = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a', 0, 't', 'a', 'i', 'l' };
    var result = try argv_split.argv_split(std.testing.allocator, &buffer);
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualSlices(u8, "beta\x00tail", result.argv[1]);
    try std.testing.expect(@intFromPtr(result.argv[0].ptr) != @intFromPtr(&buffer[0]));
    try std.testing.expect(@intFromPtr(result.argv[1].ptr) != @intFromPtr(&buffer[6]));

    buffer[0] = 'A';
    buffer[6] = 'B';
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualSlices(u8, "beta\x00tail", result.argv[1]);
}

test "phase1 argv_split NUL edges treat mixed ASCII whitespace as separators around embedded NUL bytes" {
    const input = "\r\ninit=/init\x0bconsole=ttyS0\x0cpanic=-1\x00ignored";
    var result = try argv_split.argvSplit(std.testing.allocator, input);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("init=/init", result.argv[0]);
    try std.testing.expectEqualStrings("console=ttyS0", result.argv[1]);
    try std.testing.expectEqualSlices(u8, "panic=-1\x00ignored", result.argv[2]);
}

test "phase1 argv_split NUL edges reset result slices on explicit free" {
    var result = try argv_split.argvSplit(std.testing.allocator, "single");
    try std.testing.expectEqual(@as(usize, 1), result.argc());

    argv_split.argvFree(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}
