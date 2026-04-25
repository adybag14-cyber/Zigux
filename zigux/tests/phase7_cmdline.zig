const std = @import("std");
const cmdline = @import("cmdline");

test "phase 7 cmdline module imports cleanly" {
    _ = cmdline;
}

test "phase 7 getOption and getOptions preserve Linux-style range parsing" {
    var option_rest: []const u8 = "3-5";
    var option_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 3), cmdline.getOption(&option_rest, &option_value));
    try std.testing.expectEqual(@as(i32, 3), option_value);
    try std.testing.expectEqualStrings("-5", option_rest);

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = cmdline.getOptions("3-5,8", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 3, 4, 5, 8 }, &values);
}

test "phase 7 memparse preserves suffix scaling and stop index semantics" {
    var index: usize = 0;
    try std.testing.expectEqual(@as(u64, 64 * 1024), cmdline.memparse("64K,panic", &index));
    try std.testing.expectEqual(@as(usize, 3), index);

    try std.testing.expectEqual(@as(u64, 1 << 30), cmdline.memparse("1G", &index));
    try std.testing.expectEqual(@as(usize, 2), index);
}

test "phase 7 parseOptionStr matches only exact bare options" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
}

test "phase 7 nextArg keeps quoted values together and advances to the next token" {
    var pair = [_]u8{ 'r', 'o', 'o', 't', '=', '"', '/', 'd', 'e', 'v', '/', 's', 'd', 'a', ' ', '1', '"', ' ', 'r', 'o', 0 };
    const parsed_pair = cmdline.nextArg(&pair);
    try std.testing.expectEqualStrings("root", parsed_pair.param);
    try std.testing.expectEqualStrings("/dev/sda 1", parsed_pair.value.?);
    try std.testing.expectEqualStrings("ro", parsed_pair.rest[0..2]);

    var quoted = [_]u8{ '"', 'n', 'o', 'p', 'a', 'r', 'a', 'm', ' ', 'v', 'a', 'l', 'u', 'e', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed_quoted = cmdline.nextArg(&quoted);
    try std.testing.expectEqualStrings("noparam value", parsed_quoted.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed_quoted.value);
    try std.testing.expectEqualStrings("next", parsed_quoted.rest[0..4]);
}
