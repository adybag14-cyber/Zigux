const std = @import("std");
const cmdline = @import("cmdline");

fn expectNullValue(arg: cmdline.NextArgResult, expected_param: []const u8, expected_remaining: []const u8) !void {
    try std.testing.expectEqualStrings(expected_param, arg.param);
    try std.testing.expect(arg.value == null);
    try std.testing.expectEqualStrings(expected_remaining, arg.remaining);
}

fn expectValue(arg: cmdline.NextArgResult, expected_param: []const u8, expected_value: []const u8, expected_remaining: []const u8) !void {
    try std.testing.expectEqualStrings(expected_param, arg.param);
    try std.testing.expectEqualStrings(expected_value, arg.value.?);
    try std.testing.expectEqualStrings(expected_remaining, arg.remaining);
}

test "phase1 cmdline unmatched-quote replay keeps a leading quoted bare token open until input end" {
    const parsed = cmdline.nextArg("\"debug level quiet root") orelse return error.TestUnexpectedResult;
    try expectNullValue(parsed, "debug level quiet root", "");
}

test "phase1 cmdline unmatched-quote replay keeps a leading quoted key value pair attached to the same token" {
    const parsed = cmdline.nextArg("\"console=ttyS0,115200 panic=-1 quiet") orelse return error.TestUnexpectedResult;
    try expectValue(parsed, "console", "ttyS0,115200 panic=-1 quiet", "");

    const alias = cmdline.next_arg("\"console=ttyS0,115200 panic=-1 quiet") orelse return error.TestUnexpectedResult;
    try expectValue(alias, "console", "ttyS0,115200 panic=-1 quiet", "");
}

test "phase1 cmdline unmatched-quote replay keeps an unmatched quoted value open past internal spaces" {
    const parsed = cmdline.nextArg("root=\"/dev/sda1 quiet debug loglevel=7") orelse return error.TestUnexpectedResult;
    try expectValue(parsed, "root", "/dev/sda1 quiet debug loglevel=7", "");
}

test "phase1 cmdline unmatched-quote replay resumes normal token boundaries after a closed quoted token" {
    const first = cmdline.nextArg("\"mode=fast path\" audit=1 next") orelse return error.TestUnexpectedResult;
    try expectValue(first, "mode", "fast path", "audit=1 next");

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try expectValue(second, "audit", "1", "next");

    const third = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
    try expectNullValue(third, "next", "");
}
