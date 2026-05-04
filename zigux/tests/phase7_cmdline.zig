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

const GetOptionCase = struct {
    input: []const u8,
    expected_rc: u8,
    expected_rest: []const u8,
};

const GetOptionsCase = struct {
    input: []const u8,
    expected: []const i32,
};

fn expectGetOptionCase(case: GetOptionCase) !void {
    var rest = case.input;
    var value: i32 = -1;
    try std.testing.expectEqual(case.expected_rc, cmdline.getOption(&rest, &value));
    try std.testing.expectEqualStrings(case.expected_rest, rest);
}

fn expectGetOptionsCase(case: GetOptionsCase) !void {
    var parsed = [_]i32{0} ** 16;
    _ = cmdline.getOptions(case.input, parsed.len, &parsed);
    try std.testing.expectEqualSlices(i32, case.expected, parsed[0..case.expected.len]);
    for (parsed[case.expected.len..]) |value| {
        try std.testing.expectEqual(@as(i32, 0), value);
    }

    var validate = [_]i32{0} ** 16;
    _ = cmdline.getOptions(case.input, 0, &validate);
    try std.testing.expectEqual(case.expected[0], validate[0]);
    for (validate[1..]) |value| {
        try std.testing.expectEqual(@as(i32, 0), value);
    }
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
}

test "phase 7 getOptions preserves descending-range and partial-parse stop behavior" {
    var descending = [_]i32{ 0, 0, 0, 0 };
    const descending_rest = cmdline.getOptions("4-2,9", descending.len, &descending);
    try std.testing.expectEqualStrings("2,9", descending_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 4, 0, 0 }, &descending);

    var partial = [_]i32{ 0, 0, 0 };
    const partial_rest = cmdline.getOptions("8,xx", partial.len, &partial);
    try std.testing.expectEqualStrings("xx", partial_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 8, 0 }, &partial);
}

test "phase 7 getOptions keeps array-capacity stop behavior explicit when a range is only partially stored" {
    var limited = [_]i32{ 0, 0, 0 };
    const limited_rest = cmdline.getOptions("1-4,8", limited.len, &limited);
    try std.testing.expectEqualStrings("4,8", limited_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 1, 2 }, &limited);

    var validate = [_]i32{0} ** 8;
    const validate_rest = cmdline.getOptions("1-4,8", 0, &validate);
    try std.testing.expectEqualStrings("", validate_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 0, 0, 0, 0, 0, 0, 0 }, &validate);
}

test "phase 7 getOptions fails closed on out-of-range range bounds instead of trapping" {
    var values = [_]i32{ 0, 0, 0 };
    const rest = cmdline.getOptions("2147483647-2147483648,9", values.len, &values);
    try std.testing.expectEqualStrings("2147483648,9", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 2147483647, 0 }, &values);

    var validate = [_]i32{0};
    const validate_rest = cmdline.getOptions("2147483647-2147483648", 0, &validate);
    try std.testing.expectEqualStrings("2147483648", validate_rest);
    try std.testing.expectEqual(@as(i32, 0), validate[0]);
}

test "phase 7 memparse preserves suffix scaling and stop index semantics" {
    var index: usize = 0;
    try std.testing.expectEqual(@as(u64, 64 * 1024), cmdline.memparse("64K,panic", &index));
    try std.testing.expectEqual(@as(usize, 3), index);

    try std.testing.expectEqual(@as(u64, 1 << 30), cmdline.memparse("1G", &index));
    try std.testing.expectEqual(@as(usize, 2), index);

    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("G5", &index));
    try std.testing.expectEqual(@as(usize, 1), index);

    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("0xK", &index));
    try std.testing.expectEqual(@as(usize, 1), index);
}

test "phase 7 parseOptionStr matches C empty-option edge behavior around commas" {
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug", ""));
    try std.testing.expect(!cmdline.parseOptionStr("", ""));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,", ""));
}

test "phase 7 parseOptionStr matches only exact bare options" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
}

test "phase 7 getOption keeps bare 0x in octal-style zero parsing" {
    var rest: []const u8 = "0x,tail";
    var value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, 0), value);
    try std.testing.expectEqualStrings("x,tail", rest);
}

test "phase 7 numeric helpers reject explicit leading plus signs to stay with cmdline.c simple_strtoull semantics" {
    var rest: []const u8 = "+7,panic";
    var value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, 0), value);
    try std.testing.expectEqualStrings("+7,panic", rest);

    var index: usize = 0;
    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("+32K", &index));
    try std.testing.expectEqual(@as(usize, 0), index);

    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("+0x10", &index));
    try std.testing.expectEqual(@as(usize, 0), index);
}

test "phase 7 getOption zeroes the output slot for non-empty invalid tokens" {
    var rest: []const u8 = "d=eEc";
    var value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, 0), value);
    try std.testing.expectEqualStrings("d=eEc", rest);
}

test "phase 7 nextArg matches serialized edge fixtures" {
    for (next_arg_vectors.next_arg_cases) |fixture| {
        try expectNextArgFixture(fixture);
    }
}

test "phase 7 nextArg keeps explicit bare and quoted empty values reviewable" {
    var bare_empty = [_]u8{ 'm', 'o', 'd', 'e', '=', 0 };
    const bare = cmdline.nextArg(bare_empty[0..]);
    try std.testing.expectEqualStrings("mode", bare.param);
    try std.testing.expect(bare.value != null);
    try std.testing.expectEqualStrings("", bare.value.?);
    try std.testing.expectEqualStrings("", cStringPrefix(bare.rest));
    try std.testing.expect(bare.value.?.ptr == bare_empty[5..].ptr);
    try std.testing.expectEqual(@as(u8, 0), bare_empty[4]);

    var quoted_empty = [_]u8{ 'm', 'o', 'd', 'e', '=', '"', '"', ' ', 'q', 'u', 'i', 'e', 't', 0 };
    const quoted = cmdline.nextArg(quoted_empty[0..]);
    try std.testing.expectEqualStrings("mode", quoted.param);
    try std.testing.expect(quoted.value != null);
    try std.testing.expectEqualStrings("", quoted.value.?);
    try std.testing.expectEqualStrings("quiet", cStringPrefix(quoted.rest));
    try std.testing.expect(quoted.value.?.ptr == quoted_empty[6..].ptr);
    try std.testing.expect(quoted.rest.ptr == quoted_empty[8..].ptr);
    try std.testing.expectEqual(@as(u8, 0), quoted_empty[4]);
    try std.testing.expectEqual(@as(u8, 0), quoted_empty[6]);
    try std.testing.expectEqual(@as(u8, 0), quoted_empty[7]);
}

test "phase 7 nextArg keeps in-place split ownership visible in the shared gate" {
    var input = [_]u8{ 'r', 'o', 'o', 't', '=', '"', '/', 'd', 'e', 'v', '/', 's', 'd', 'a', ' ', '1', '"', ' ', 'r', 'o', 0 };
    const parsed = cmdline.nextArg(input[0..]);
    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda 1", parsed.value.?);
    try std.testing.expectEqualStrings("ro", cStringPrefix(parsed.rest));
    try std.testing.expect(parsed.param.ptr == input[0..].ptr);
    try std.testing.expect(parsed.value.?.ptr == input[6..].ptr);
    try std.testing.expect(parsed.rest.ptr == input[18..].ptr);
    try std.testing.expectEqual(@as(u8, 0), input[4]);
    try std.testing.expectEqual(@as(u8, 0), input[16]);
    try std.testing.expectEqual(@as(u8, 0), input[17]);
}

test "phase 7 getOption matches malformed-token classification from the Linux KUnit corpus" {
    const cases = [_]GetOptionCase{
        .{ .input = "\"\"", .expected_rc = 0, .expected_rest = "\"\"" }, .{ .input = "", .expected_rc = 0, .expected_rest = "" }, .{ .input = "=", .expected_rc = 0, .expected_rest = "=" }, .{ .input = "\"-", .expected_rc = 0, .expected_rest = "\"-" }, .{ .input = ",", .expected_rc = 0, .expected_rest = "," }, .{ .input = "-,", .expected_rc = 0, .expected_rest = "," }, .{ .input = ",-", .expected_rc = 0, .expected_rest = ",-" }, .{ .input = "-", .expected_rc = 0, .expected_rest = "" }, .{ .input = "+,", .expected_rc = 0, .expected_rest = "+," }, .{ .input = "--", .expected_rc = 0, .expected_rest = "-" }, .{ .input = ",,", .expected_rc = 0, .expected_rest = ",," }, .{ .input = "''", .expected_rc = 0, .expected_rest = "''" }, .{ .input = "\"\",", .expected_rc = 0, .expected_rest = "\"\"," }, .{ .input = "\",\"", .expected_rc = 0, .expected_rest = "\",\"" }, .{ .input = "-\"\"", .expected_rc = 0, .expected_rest = "\"\"" }, .{ .input = "\"", .expected_rc = 0, .expected_rest = "\"" }, .{ .input = "37,", .expected_rc = 2, .expected_rest = "" }, .{ .input = "37--", .expected_rc = 3, .expected_rest = "--" }, .{ .input = "\"\"37", .expected_rc = 0, .expected_rest = "\"\"37" }, .{ .input = "-21", .expected_rc = 1, .expected_rest = "" },
    };
    for (cases) |case| try expectGetOptionCase(case);
}

test "phase 7 getOption matches leading-integer pointer advance from the Linux KUnit corpus" {
    const cases = [_]GetOptionCase{
        .{ .input = "37\"\"", .expected_rc = 1, .expected_rest = "\"\"" }, .{ .input = "37=", .expected_rc = 1, .expected_rest = "=" }, .{ .input = "37\"-", .expected_rc = 1, .expected_rest = "\"-" }, .{ .input = "37,", .expected_rc = 2, .expected_rest = "" }, .{ .input = "37-,", .expected_rc = 3, .expected_rest = "-," }, .{ .input = "37,-", .expected_rc = 2, .expected_rest = "-" }, .{ .input = "37-", .expected_rc = 3, .expected_rest = "-" }, .{ .input = "37+,", .expected_rc = 1, .expected_rest = "+," }, .{ .input = "37--", .expected_rc = 3, .expected_rest = "--" }, .{ .input = "37,,", .expected_rc = 2, .expected_rest = "," }, .{ .input = "37''", .expected_rc = 1, .expected_rest = "''" }, .{ .input = "37\"\",", .expected_rc = 1, .expected_rest = "\"\"," }, .{ .input = "37\",\"", .expected_rc = 1, .expected_rest = "\",\"" }, .{ .input = "37\"", .expected_rc = 1, .expected_rest = "\"" }, .{ .input = "37-\"\"", .expected_rc = 3, .expected_rest = "-\"\"" },
    };
    for (cases) |case| try expectGetOptionCase(case);
}

test "phase 7 getOption matches trailing-integer pointer advance from the Linux KUnit corpus" {
    const cases = [_]GetOptionCase{
        .{ .input = "\"\"37", .expected_rc = 0, .expected_rest = "\"\"37" }, .{ .input = "=37", .expected_rc = 0, .expected_rest = "=37" }, .{ .input = "\"-37", .expected_rc = 0, .expected_rest = "\"-37" }, .{ .input = ",37", .expected_rc = 0, .expected_rest = ",37" }, .{ .input = "-,37", .expected_rc = 0, .expected_rest = ",37" }, .{ .input = ",-37", .expected_rc = 0, .expected_rest = ",-37" }, .{ .input = "-37", .expected_rc = 1, .expected_rest = "" }, .{ .input = "+,37", .expected_rc = 0, .expected_rest = "+,37" }, .{ .input = "--37", .expected_rc = 0, .expected_rest = "-37" }, .{ .input = ",,37", .expected_rc = 0, .expected_rest = ",,37" }, .{ .input = "''37", .expected_rc = 0, .expected_rest = "''37" }, .{ .input = "\"\",37", .expected_rc = 0, .expected_rest = "\"\",37" }, .{ .input = "\",\"37", .expected_rc = 0, .expected_rest = "\",\"37" }, .{ .input = "-\"\"37", .expected_rc = 0, .expected_rest = "\"\"37" }, .{ .input = "\"37", .expected_rc = 0, .expected_rest = "\"37" }, .{ .input = "37", .expected_rc = 1, .expected_rest = "" },
    };
    for (cases) |case| try expectGetOptionCase(case);
}

test "phase 7 getOptions matches malformed-range counting from the Linux KUnit corpus" {
    const cases = [_]GetOptionsCase{
        .{ .input = "-7", .expected = &[_]i32{ 1, -7 } }, .{ .input = "--7", .expected = &[_]i32{ 0, 0 } }, .{ .input = "-1-2", .expected = &[_]i32{ 4, -1, 0, 1, 2 } }, .{ .input = "7--9", .expected = &[_]i32{ 0, 7 } }, .{ .input = "7-", .expected = &[_]i32{ 0, 7 } }, .{ .input = "-7--9", .expected = &[_]i32{ 0, -7 } }, .{ .input = "7-9,", .expected = &[_]i32{ 3, 7, 8, 9, 0 } }, .{ .input = "9-7", .expected = &[_]i32{ 0, 9 } }, .{ .input = "5-a", .expected = &[_]i32{ 0, 5 } }, .{ .input = "a-5", .expected = &[_]i32{ 0, 0 } }, .{ .input = "5-8", .expected = &[_]i32{ 4, 5, 6, 7, 8 } }, .{ .input = ",8-5", .expected = &[_]i32{ 0, 0 } }, .{ .input = "+,1", .expected = &[_]i32{ 0, 0 } }, .{ .input = "-,4", .expected = &[_]i32{ 0, 0 } }, .{ .input = "-3,0-1,6", .expected = &[_]i32{ 4, -3, 0, 1, 6 } }, .{ .input = "4,-", .expected = &[_]i32{ 1, 4 } }, .{ .input = " +2", .expected = &[_]i32{ 0, 0 } }, .{ .input = " -9", .expected = &[_]i32{ 0, 0 } }, .{ .input = "0-1,-3,6", .expected = &[_]i32{ 4, 0, 1, -3, 6 } }, .{ .input = "- 9", .expected = &[_]i32{ 0, 0 } },
    };
    for (cases) |case| try expectGetOptionsCase(case);
}

test "phase 7 large wrapped numeric inputs stay runtime-safe and match low-word C semantics" {
    var positive_rest: []const u8 = "18446744073709551615,tail";
    var positive_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&positive_rest, &positive_value));
    try std.testing.expectEqual(@as(i32, -1), positive_value);
    try std.testing.expectEqualStrings("tail", positive_rest);

    var negative_rest: []const u8 = "-18446744073709551615,tail";
    var negative_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&negative_rest, &negative_value));
    try std.testing.expectEqual(@as(i32, 1), negative_value);
    try std.testing.expectEqualStrings("tail", negative_rest);
}