const std = @import("std");

const CmdlineValueFixture = struct {
    value: u64,
    rest: []const u8,
};

const CmdlineArgFixture = struct {
    param: []const u8,
    value: []const u8,
    remaining: []const u8,
};

const Fixture = struct {
    cmdline: struct {
        decimal_k: CmdlineValueFixture,
        signed_k: CmdlineValueFixture,
        signed_hex_k: CmdlineValueFixture,
        signed_octal_m: CmdlineValueFixture,
        saturated_positive_signed: CmdlineValueFixture,
        option_debug: bool,
        option_empty_leading: bool,
        option_empty_double_comma: bool,
        option_empty_trailing: bool,
        option_absent: bool,
        first_arg: CmdlineArgFixture,
        second_arg: CmdlineArgFixture,
        quoted_arg: CmdlineArgFixture,
        empty_quoted_arg: CmdlineArgFixture,
        unterminated_arg: CmdlineArgFixture,
        hex_m: CmdlineValueFixture,
        octal_k: CmdlineValueFixture,
        invalid: CmdlineValueFixture,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
}

test "phase1 cmdline fixture keeps signed suffix conversions" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const cmdline = parsed.value.cmdline;

    try std.testing.expectEqual(@as(u64, 18446744073709549568), cmdline.signed_k.value);
    try std.testing.expectEqualStrings(" tail", cmdline.signed_k.rest);

    try std.testing.expectEqual(@as(u64, 18446744073709549568), cmdline.signed_hex_k.value);
    try std.testing.expectEqualStrings("tail", cmdline.signed_hex_k.rest);

    try std.testing.expectEqual(@as(u64, 8388608), cmdline.signed_octal_m.value);
    try std.testing.expectEqualStrings("more", cmdline.signed_octal_m.rest);

    try std.testing.expectEqual(@as(u64, 9223372036854775807), cmdline.saturated_positive_signed.value);
    try std.testing.expectEqualStrings("", cmdline.saturated_positive_signed.rest);
}

test "phase1 cmdline fixture keeps option boundary cases" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const cmdline = parsed.value.cmdline;

    try std.testing.expect(cmdline.option_debug);
    try std.testing.expect(cmdline.option_empty_leading);
    try std.testing.expect(cmdline.option_empty_double_comma);
    try std.testing.expect(!cmdline.option_empty_trailing);
    try std.testing.expect(!cmdline.option_absent);
}

test "phase1 cmdline fixture keeps quoted argument packet" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const cmdline = parsed.value.cmdline;

    try std.testing.expectEqualStrings("console", cmdline.first_arg.param);
    try std.testing.expectEqualStrings("ttyS0,115200", cmdline.first_arg.value);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", cmdline.first_arg.remaining);

    try std.testing.expectEqualStrings("root", cmdline.second_arg.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", cmdline.second_arg.value);
    try std.testing.expectEqualStrings("panic=-1", cmdline.second_arg.remaining);

    try std.testing.expectEqualStrings("mode", cmdline.quoted_arg.param);
    try std.testing.expectEqualStrings("fast path", cmdline.quoted_arg.value);

    try std.testing.expectEqualStrings("root", cmdline.empty_quoted_arg.param);
    try std.testing.expectEqualStrings("", cmdline.empty_quoted_arg.value);
    try std.testing.expectEqualStrings("quiet", cmdline.empty_quoted_arg.remaining);

    try std.testing.expectEqualStrings("mode", cmdline.unterminated_arg.param);
    try std.testing.expectEqualStrings("fast boot", cmdline.unterminated_arg.value);
    try std.testing.expectEqualStrings("", cmdline.unterminated_arg.remaining);
}

test "phase1 cmdline fixture keeps invalid parse authority" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const cmdline = parsed.value.cmdline;

    try std.testing.expectEqual(@as(u64, 65536), cmdline.decimal_k.value);
    try std.testing.expectEqualStrings(" rest", cmdline.decimal_k.rest);
    try std.testing.expectEqual(@as(u64, 33554432), cmdline.hex_m.value);
    try std.testing.expectEqualStrings("", cmdline.hex_m.rest);
    try std.testing.expectEqual(@as(u64, 8192), cmdline.octal_k.value);
    try std.testing.expectEqualStrings("", cmdline.octal_k.rest);
    try std.testing.expectEqual(@as(u64, 0), cmdline.invalid.value);
    try std.testing.expectEqualStrings("xyz", cmdline.invalid.rest);
}
