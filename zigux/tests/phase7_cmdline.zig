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

    var plus_values = [_]i32{ 0, 0, 0 };
    const plus_rest = cmdline.getOptions("+7", plus_values.len, &plus_values);
    try std.testing.expectEqualStrings("", plus_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 7, 0 }, &plus_values);

    var plus_validate = [_]i32{0};
    const plus_validate_rest = cmdline.getOptions("+7", 0, &plus_validate);
    try std.testing.expectEqualStrings("", plus_validate_rest);
    try std.testing.expectEqual(@as(i32, 1), plus_validate[0]);

    var single = [_]i32{ 0, 0, 0 };
    const single_rest = cmdline.getOptions("1-1", single.len, &single);
    try std.testing.expectEqualStrings("", single_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 1, 0 }, &single);

    var single_validate = [_]i32{0};
    const single_validate_rest = cmdline.getOptions("1-1", 0, &single_validate);
    try std.testing.expectEqualStrings("", single_validate_rest);
    try std.testing.expectEqual(@as(i32, 1), single_validate[0]);
}

test "phase 7 getOption clears caller output on malformed signed and unsigned input" {
    var hyphen_only: []const u8 = "-";
    var hyphen_only_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&hyphen_only, &hyphen_only_value));
    try std.testing.expectEqual(@as(i32, 0), hyphen_only_value);
    try std.testing.expectEqualStrings("", hyphen_only);

    var malformed_negative: []const u8 = "-x";
    var malformed_negative_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&malformed_negative, &malformed_negative_value));
    try std.testing.expectEqual(@as(i32, 0), malformed_negative_value);
    try std.testing.expectEqualStrings("x", malformed_negative);

    var malformed_unsigned: []const u8 = "x";
    var malformed_unsigned_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&malformed_unsigned, &malformed_unsigned_value));
    try std.testing.expectEqual(@as(i32, 0), malformed_unsigned_value);
    try std.testing.expectEqualStrings("x", malformed_unsigned);
}

test "phase 7 getOption keeps incomplete hex prefixes aligned with Linux simple_strtoull consumption" {
    var plain_hex_rest: []const u8 = "0x";
    var plain_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&plain_hex_rest, &plain_hex_value));
    try std.testing.expectEqual(@as(i32, 0), plain_hex_value);
    try std.testing.expectEqualStrings("x", plain_hex_rest);

    var plus_hex_rest: []const u8 = "+0x";
    var plus_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&plus_hex_rest, &plus_hex_value));
    try std.testing.expectEqual(@as(i32, 0), plus_hex_value);
    try std.testing.expectEqualStrings("x", plus_hex_rest);

    var negative_hex_rest: []const u8 = "-0x";
    var negative_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&negative_hex_rest, &negative_hex_value));
    try std.testing.expectEqual(@as(i32, 0), negative_hex_value);
    try std.testing.expectEqualStrings("x", negative_hex_rest);

    var values = [_]i32{ 0, 0, 0 };
    const rest = cmdline.getOptions("0x,7", values.len, &values);
    try std.testing.expectEqualStrings("x,7", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 0, 0 }, &values);

    var validate = [_]i32{0};
    const validate_rest = cmdline.getOptions("+0x,7", 0, &validate);
    try std.testing.expectEqualStrings("x,7", validate_rest);
    try std.testing.expectEqual(@as(i32, 1), validate[0]);
}

test "phase 7 getOption and getOptions preserve oversized wrap semantics" {
    var positive: []const u8 = "2147483648";
    var positive_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&positive, &positive_value));
    try std.testing.expectEqual(@as(i32, -2147483648), positive_value);
    try std.testing.expectEqualStrings("", positive);

    var negative: []const u8 = "-2147483649";
    var negative_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&negative, &negative_value));
    try std.testing.expectEqual(@as(i32, 2147483647), negative_value);
    try std.testing.expectEqualStrings("", negative);

    var positive_full: []const u8 = "18446744073709551615";
    var positive_full_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&positive_full, &positive_full_value));
    try std.testing.expectEqual(@as(i32, -1), positive_full_value);
    try std.testing.expectEqualStrings("", positive_full);

    var negative_full: []const u8 = "-18446744073709551615";
    var negative_full_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&negative_full, &negative_full_value));
    try std.testing.expectEqual(@as(i32, 1), negative_full_value);
    try std.testing.expectEqualStrings("", negative_full);

    var values = [_]i32{ 0, 0, 0 };
    const rest = cmdline.getOptions("2147483648,-2147483649", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, -2147483648, 2147483647 }, &values);

    var validate_only = [_]i32{0};
    const validate_rest = cmdline.getOptions("2147483648,-2147483649", 0, &validate_only);
    try std.testing.expectEqualStrings("", validate_rest);
    try std.testing.expectEqual(@as(i32, 2), validate_only[0]);

    var full_values = [_]i32{ 0, 0, 0 };
    const full_rest = cmdline.getOptions("18446744073709551615,-18446744073709551615", full_values.len, &full_values);
    try std.testing.expectEqualStrings("", full_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, -1, 1 }, &full_values);

    var full_validate_only = [_]i32{0};
    const full_validate_rest = cmdline.getOptions("18446744073709551615,-18446744073709551615", 0, &full_validate_only);
    try std.testing.expectEqualStrings("", full_validate_rest);
    try std.testing.expectEqual(@as(i32, 2), full_validate_only[0]);
}

test "phase 7 getOption preserves validator-only numeric acceptance" {
    var plain: []const u8 = "7";
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&plain, null));
    try std.testing.expectEqualStrings("", plain);

    var comma: []const u8 = "+9,tail";
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&comma, null));
    try std.testing.expectEqualStrings("tail", comma);

    var range: []const u8 = "5-8";
    try std.testing.expectEqual(@as(u8, 3), cmdline.getOption(&range, null));
    try std.testing.expectEqualStrings("-8", range);
}

test "phase 7 memparse preserves suffix scaling, leading plus, and stop index semantics" {
    var index: usize = 0;
    try std.testing.expectEqual(@as(u64, 64 * 1024), cmdline.memparse("64K,panic", &index));
    try std.testing.expectEqual(@as(usize, 3), index);
    try std.testing.expectEqual(@as(u64, 1 << 30), cmdline.memparse("1G", &index));
    try std.testing.expectEqual(@as(usize, 2), index);
    try std.testing.expectEqual(@as(u64, 1024), cmdline.memparse("+1K", &index));
    try std.testing.expectEqual(@as(usize, 3), index);
    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("0xK", &index));
    try std.testing.expectEqual(@as(usize, 1), index);
    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("K", &index));
    try std.testing.expectEqual(@as(usize, 1), index);
    try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("krest", &index));
    try std.testing.expectEqual(@as(usize, 1), index);
}

test "phase 7 parseOptionStr matches only exact bare options" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug\x00,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("", ""));
}

test "phase 7 nextArg matches serialized edge fixtures" {
    for (next_arg_vectors.next_arg_cases) |fixture| {
        try expectNextArgFixture(fixture);
    }
}

test "phase 7 nextArg keeps caller-owned buffer slices and sentinel writes explicit" {
    var buffer = [_]u8{ 'r', 'o', 'o', 't', '=', '"', '/', 'd', 'e', 'v', '/', 's', 'd', 'a', '1', '"', ' ', 'r', 'o', 0 };
    const parsed = cmdline.nextArg(&buffer);
    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1", parsed.value.?);
    try std.testing.expectEqualStrings("ro", cStringPrefix(parsed.rest));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[0])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[6])), @as(usize, @intFromPtr(parsed.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[17])), @as(usize, @intFromPtr(parsed.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), buffer[4]);
    try std.testing.expectEqual(@as(u8, 0), buffer[15]);
    try std.testing.expectEqual(@as(u8, 0), buffer[16]);
}

test "phase 7 nextArg keeps empty-input and leading-whitespace ownership explicit" {
    var empty = [_]u8{};
    const empty_args = empty[0..];
    const parsed_empty = cmdline.nextArg(empty_args);
    try std.testing.expectEqualStrings("", parsed_empty.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed_empty.value);
    try std.testing.expectEqualStrings("", cStringPrefix(parsed_empty.rest));
    try std.testing.expectEqual(@as(usize, @intFromPtr(empty_args.ptr)), @as(usize, @intFromPtr(parsed_empty.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(empty_args.ptr)), @as(usize, @intFromPtr(parsed_empty.rest.ptr)));

    var leading_whitespace = [_]u8{ ' ', '\t', 'f', 'o', 'o', '=', '1', 0 };
    const parsed_leading_whitespace = cmdline.nextArg(&leading_whitespace);
    try std.testing.expectEqualStrings("", parsed_leading_whitespace.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed_leading_whitespace.value);
    try std.testing.expectEqualStrings("foo=1", cStringPrefix(parsed_leading_whitespace.rest));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&leading_whitespace[0])), @as(usize, @intFromPtr(parsed_leading_whitespace.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&leading_whitespace[2])), @as(usize, @intFromPtr(parsed_leading_whitespace.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), leading_whitespace[0]);
}
