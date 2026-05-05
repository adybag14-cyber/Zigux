const std = @import("std");
const cmdline = @import("cmdline");
const next_arg_vectors = @import("fixtures/phase7_cmdline_next_arg_vectors.zig");

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn expectNextArgFixture(fixture: next_arg_vectors.NextArgCase) !void {
    var buffer = [_]u8{0} ** 128;
    try std.testing.expect(fixture.input.len <= buffer.len);
    @memcpy(buffer[0..fixture.input.len], fixture.input);

    const parsed = cmdline.nextArg(buffer[0..fixture.input.len]);
    try std.testing.expectEqualStrings(fixture.expected_param, parsed.param);

    if (fixture.expected_value) |expected| {
        try std.testing.expect(parsed.value != null);
        try std.testing.expectEqualStrings(expected, parsed.value.?);
    } else {
        try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    }

    try std.testing.expectEqualStrings(fixture.expected_rest, cStringPrefix(parsed.rest));
}

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

    var single = [_]i32{ 0, 0, 0 };
    const single_rest = cmdline.getOptions("1-1", single.len, &single);
    try std.testing.expectEqualStrings("", single_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 1, 0 }, &single);

    var validate = [_]i32{0};
    const validate_rest = cmdline.getOptions("1-1", 0, &validate);
    try std.testing.expectEqualStrings("", validate_rest);
    try std.testing.expectEqual(@as(i32, 1), validate[0]);
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

test "phase 7 nextArg matches serialized edge fixtures" {
    for (next_arg_vectors.next_arg_cases) |fixture| {
        try expectNextArgFixture(fixture);
    }
}
