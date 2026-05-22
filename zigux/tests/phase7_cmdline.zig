const std = @import("std");
const cmdline = @import("cmdline");

test "phase 7 cmdline companion replays exact bare-option matching boundaries" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(cmdline.parse_option_str("quiet,debug,nohlt", "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug\x00,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("", ""));
}

test "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture" {
    var option_rest: []const u8 = "3-5";
    var option_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 3), cmdline.getOption(&option_rest, &option_value));
    try std.testing.expectEqual(@as(i32, 3), option_value);
    try std.testing.expectEqualStrings("-5", option_rest);

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = cmdline.getOptions("3-5,8", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 3, 4, 5, 8 }, &values);

    var malformed_negative: []const u8 = "-x";
    var malformed_negative_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&malformed_negative, &malformed_negative_value));
    try std.testing.expectEqual(@as(i32, 0), malformed_negative_value);
    try std.testing.expectEqualStrings("x", malformed_negative);

    var wrapped_positive_rest: []const u8 = "18446744073709551615,tail";
    var wrapped_positive_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&wrapped_positive_rest, &wrapped_positive_value));
    try std.testing.expectEqual(@as(i32, -1), wrapped_positive_value);
    try std.testing.expectEqualStrings("tail", wrapped_positive_rest);

    var wrapped_values = [_]i32{ 0, 0, 0 };
    const wrapped_rest = cmdline.getOptions("18446744073709551615,-18446744073709551615", wrapped_values.len, &wrapped_values);
    try std.testing.expectEqualStrings("", wrapped_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, -1, 1 }, &wrapped_values);

    var wrapped_validate = [_]i32{0};
    const wrapped_validate_rest = cmdline.getOptions("18446744073709551615,-18446744073709551615", 0, &wrapped_validate);
    try std.testing.expectEqualStrings("", wrapped_validate_rest);
    try std.testing.expectEqual(@as(i32, 2), wrapped_validate[0]);
}

test "phase 7 cmdline companion replays incomplete-hex and descending-range boundaries" {
    var incomplete_hex: []const u8 = "0x";
    var incomplete_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), cmdline.getOption(&incomplete_hex, &incomplete_hex_value));
    try std.testing.expectEqual(@as(i32, 0), incomplete_hex_value);
    try std.testing.expectEqualStrings("x", incomplete_hex);

    var plus_hex_rest: []const u8 = "+0x";
    var plus_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&plus_hex_rest, &plus_hex_value));
    try std.testing.expectEqual(@as(i32, 0), plus_hex_value);
    try std.testing.expectEqualStrings("+0x", plus_hex_rest);

    var descending = [_]i32{ 0, 0, 0, 0 };
    const descending_rest = cmdline.getOptions("4-2,9", descending.len, &descending);
    try std.testing.expectEqualStrings("2,9", descending_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 4, 0, 0 }, &descending);
}

test "phase 7 cmdline companion replays negative range expansion and negative upper-bound posture" {
    var negative_values = [_]i32{ 0, 0, 0, 0, 0 };
    const negative_rest = cmdline.getOptions("-2-1", negative_values.len, &negative_values);
    try std.testing.expectEqualStrings("", negative_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, -2, -1, 0, 1 }, &negative_values);

    var negative_upper_values = [_]i32{ 0, 0, 0, 0 };
    const negative_upper_rest = cmdline.get_options("-3--1", negative_upper_values.len, &negative_upper_values);
    try std.testing.expectEqualStrings("", negative_upper_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, -3, -2, -1 }, &negative_upper_values);
}

test "phase 7 cmdline companion replays validator-only getOption cursor movement" {
    var comma_rest: []const u8 = "16,tail";
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&comma_rest, null));
    try std.testing.expectEqualStrings("tail", comma_rest);

    var range_rest: []const u8 = "7-9";
    try std.testing.expectEqual(@as(u8, 3), cmdline.getOption(&range_rest, null));
    try std.testing.expectEqualStrings("-9", range_rest);

    var negative_rest: []const u8 = "-5,rest";
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&negative_rest, null));
    try std.testing.expectEqualStrings("rest", negative_rest);
}

test "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries" {
    const parsed = cmdline.nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1");
    try std.testing.expectEqualStrings("console", parsed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", parsed.value.?);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", parsed.remaining);

    const second = cmdline.next_arg(parsed.remaining);
    try std.testing.expectEqualStrings("root", second.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", second.value.?);
    try std.testing.expectEqualStrings("panic=-1", second.remaining);

    const negative = cmdline.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const bare_hex = cmdline.memparse("0xK");
    try std.testing.expectEqual(@as(u64, 0), bare_hex.value);
    try std.testing.expectEqualStrings("xK", bare_hex.rest);

    const no_conversion = cmdline.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), no_conversion.value);
    try std.testing.expectEqualStrings("+nope", no_conversion.rest);
}

test "phase 7 cmdline companion replays memparse signed clamp saturation" {
    const positive = cmdline.memparse("9223372036854775808");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), positive.value);
    try std.testing.expectEqualStrings("", positive.rest);

    const negative = cmdline.memparse("-9223372036854775809");
    try std.testing.expectEqual(@as(u64, 0x8000000000000000), negative.value);
    try std.testing.expectEqualStrings("", negative.rest);
}

test "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries" {
    const leading = cmdline.nextArg(" \tmode=fast");
    try std.testing.expectEqualStrings("", leading.param);
    try std.testing.expect(leading.value == null);
    try std.testing.expectEqualStrings("mode=fast", leading.rest);
    try std.testing.expectEqualStrings("mode=fast", leading.remaining);

    const quoted = cmdline.next_arg("\"mode=fast path\" tail");
    try std.testing.expectEqualStrings("mode", quoted.param);
    try std.testing.expectEqualStrings("fast path", quoted.value.?);
    try std.testing.expectEqualStrings("tail", quoted.remaining);

    const quoted_empty = cmdline.nextArg("flag=\"\" next");
    try std.testing.expectEqualStrings("flag", quoted_empty.param);
    try std.testing.expectEqualStrings("", quoted_empty.value.?);
    try std.testing.expectEqualStrings("next", quoted_empty.rest);
    try std.testing.expectEqualStrings("next", quoted_empty.remaining);
    try std.testing.expectEqual(@as(usize, @intFromPtr(quoted_empty.rest.ptr)), @as(usize, @intFromPtr(quoted_empty.remaining.ptr)));

    const nul_bounded = cmdline.nextArg("console=ttyS0\x00 root=/dev/vda");
    try std.testing.expectEqualStrings("console", nul_bounded.param);
    try std.testing.expectEqualStrings("ttyS0", nul_bounded.value.?);
    try std.testing.expectEqualStrings("", nul_bounded.remaining);
}

test "phase 7 cmdline companion replays whitespace-only sentinel termination" {
    const whitespace_only = cmdline.nextArg(" \t\n\x00ignored tail");
    try std.testing.expectEqualStrings("", whitespace_only.param);
    try std.testing.expect(whitespace_only.value == null);
    try std.testing.expectEqualStrings("", whitespace_only.rest);
    try std.testing.expectEqualStrings("", whitespace_only.remaining);
}

test "phase 7 cmdline companion replays bare leading-equals ownership" {
    const parsed = cmdline.nextArg("=ttyS0 tail");
    try std.testing.expectEqualStrings("=ttyS0", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.rest);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "nextArg keeps empty input borrowed from the caller slice" {
    var empty = [_]u8{};
    const empty_args = empty[0..];
    const parsed = cmdline.nextArg(empty_args);

    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("", parsed.rest);
    try std.testing.expectEqual(@as(usize, @intFromPtr(empty_args.ptr)), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(empty_args.ptr)), @as(usize, @intFromPtr(parsed.rest.ptr)));
}

test "nextArg stays inside the first NUL for bare and key value tokens" {
    const bare = cmdline.nextArg("debug\x00 nohlt");
    try std.testing.expectEqualStrings("debug", bare.param);
    try std.testing.expect(bare.value == null);
    try std.testing.expectEqualStrings("", bare.remaining);

    const keyed = cmdline.nextArg("console=ttyS0\x00 root=/dev/vda");
    try std.testing.expectEqualStrings("console", keyed.param);
    try std.testing.expectEqualStrings("ttyS0", keyed.value.?);
    try std.testing.expectEqualStrings("", keyed.remaining);
}

test "nextArg keeps rest and remaining as the same borrowed suffix view" {
    const leading = cmdline.nextArg(" \tconsole=ttyS0");
    try std.testing.expectEqualStrings("console=ttyS0", leading.rest);
    try std.testing.expectEqualStrings("console=ttyS0", leading.remaining);
    try std.testing.expectEqual(@as(usize, @intFromPtr(leading.rest.ptr)), @as(usize, @intFromPtr(leading.remaining.ptr)));

    const quoted_empty = cmdline.nextArg("flag=\"\" next");
    try std.testing.expectEqualStrings("next", quoted_empty.rest);
    try std.testing.expectEqualStrings("next", quoted_empty.remaining);
    try std.testing.expectEqual(@as(usize, @intFromPtr(quoted_empty.rest.ptr)), @as(usize, @intFromPtr(quoted_empty.remaining.ptr)));

    const nul_bounded = cmdline.nextArg("key=val\x00 trailing");
    try std.testing.expectEqualStrings("", nul_bounded.rest);
    try std.testing.expectEqualStrings("", nul_bounded.remaining);
    try std.testing.expectEqual(@as(usize, @intFromPtr(nul_bounded.rest.ptr)), @as(usize, @intFromPtr(nul_bounded.remaining.ptr)));
}

test "phase 7 cmdline companion replays bare quoted-empty-token ownership" {
    var quoted_empty_token = [_]u8{ '"', '"', ' ', 't', 'a', 'i', 'l', 0 };
    const parsed = cmdline.nextArg(&quoted_empty_token);
    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.rest);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&quoted_empty_token[1])), @as(usize, @intFromPtr(parsed.param.ptr)));
}

test "phase 7 cmdline companion replays quoted bare-token grouping without fabricating a value" {
    const parsed = cmdline.nextArg("\"two words\" tail");
    try std.testing.expectEqualStrings("two words", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.rest);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "phase 7 cmdline companion replays quoted leading-equals and unterminated-value boundaries" {
    const quoted_equals = cmdline.nextArg("\"=ttyS0\" tail");
    try std.testing.expectEqualStrings("=ttyS0", quoted_equals.param);
    try std.testing.expect(quoted_equals.value == null);
    try std.testing.expectEqualStrings("tail", quoted_equals.rest);
    try std.testing.expectEqualStrings("tail", quoted_equals.remaining);

    const unterminated = cmdline.nextArg("console=\"ttyS0,115200 root=/dev/vda");
    try std.testing.expectEqualStrings("console", unterminated.param);
    try std.testing.expectEqualStrings("ttyS0,115200 root=/dev/vda", unterminated.value.?);
    try std.testing.expectEqualStrings("", unterminated.rest);
    try std.testing.expectEqualStrings("", unterminated.remaining);
}

test "phase 7 cmdline companion replays quoted-value borrowed slice ownership" {
    var quoted_value = [_]u8{
        'r', 'o', 'o', 't', '=', '"', '/', 'd', 'e', 'v', '/', 'v', 'd', 'a', '1', '"', ' ', 'q', 'u', 'i', 'e', 't', 0,
    };
    const parsed_quoted_value = cmdline.nextArg(&quoted_value);
    try std.testing.expectEqualStrings("root", parsed_quoted_value.param);
    try std.testing.expectEqualStrings("/dev/vda1", parsed_quoted_value.value.?);
    try std.testing.expectEqualStrings("quiet", parsed_quoted_value.rest);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&quoted_value[0])), @as(usize, @intFromPtr(parsed_quoted_value.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&quoted_value[6])), @as(usize, @intFromPtr(parsed_quoted_value.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&quoted_value[17])), @as(usize, @intFromPtr(parsed_quoted_value.rest.ptr)));
}
