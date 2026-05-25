const std = @import("std");
const argv_split = @import("argv_split");

test "argv_split alias duplicates tokens independently of the source buffer" {
    var source = [_]u8{
        ' ', '\t',
        'm', 'o',
        'd', 'e',
        '=', 'f',
        'a', 's',
        't', ' ',
        'p', 'a',
        't', 'h',
        '/', 'w',
        'i', 't',
        'h', '-',
        'd', 'a',
        's', 'h',
        ' ', 'q',
        'u', 'i',
        'e', 't',
        '?', ' ',
    };

    var result = try argv_split.argv_split(std.testing.allocator, source[0..]);
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("mode=fast", result.argv[0]);
    try std.testing.expectEqualStrings("path/with-dash", result.argv[1]);
    try std.testing.expectEqualStrings("quiet?", result.argv[2]);

    source[2] = 'X';
    source[13] = 'X';
    source[29] = 'X';

    try std.testing.expectEqualStrings("mode=fast", result.argv[0]);
    try std.testing.expectEqualStrings("path/with-dash", result.argv[1]);
    try std.testing.expectEqualStrings("quiet?", result.argv[2]);
}

test "argvFree clears a populated result back to the blank lifecycle state" {
    var result = try argv_split.argvSplit(std.testing.allocator, "alpha beta");

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqual(@as(usize, 2), result.argv.len);

    argv_split.argvFree(&result);

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}

test "argv_free keeps blank inputs aligned with the zero-argument contract" {
    var blank = try argv_split.argv_split(std.testing.allocator, " \n\t ");

    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);

    argv_split.argv_free(&blank);

    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);
}
