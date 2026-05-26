const std = @import("std");
const argv_split = @import("argv_split");

test "argvSplit collapses every ASCII whitespace separator between tokens" {
    var parsed = try argv_split.argvSplit(
        std.testing.allocator,
        " \talpha\r\nbeta\x0bgamma\x0cdelta ",
    );
    defer parsed.deinit();

    try std.testing.expectEqual(@as(usize, 4), parsed.argc());
    try std.testing.expectEqualStrings("alpha", parsed.argv[0]);
    try std.testing.expectEqualStrings("beta", parsed.argv[1]);
    try std.testing.expectEqualStrings("gamma", parsed.argv[2]);
    try std.testing.expectEqualStrings("delta", parsed.argv[3]);
}

test "argv_split keeps option-like tokens intact across mixed whitespace boundaries" {
    var parsed = try argv_split.argv_split(
        std.testing.allocator,
        "root=/dev/sda1\r\nconsole=ttyS0,115200\tquiet\x0bpanic=-1",
    );
    defer argv_split.argv_free(&parsed);

    try std.testing.expectEqual(@as(usize, 4), parsed.argc());
    try std.testing.expectEqualStrings("root=/dev/sda1", parsed.argv[0]);
    try std.testing.expectEqualStrings("console=ttyS0,115200", parsed.argv[1]);
    try std.testing.expectEqualStrings("quiet", parsed.argv[2]);
    try std.testing.expectEqualStrings("panic=-1", parsed.argv[3]);
}
