const std = @import("std");
const cmdline = @import("cmdline");

fn expectBareLeadingEquals(text: []const u8, expected_param: []const u8, expected_remaining: []const u8) !void {
    const parsed = cmdline.nextArg(text) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(expected_param, parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings(expected_remaining, parsed.remaining);
}

test "phase1 cmdline replay keeps leading equals tokens out of key value splitting" {
    try expectBareLeadingEquals("=value tail", "=value", "tail");
    try expectBareLeadingEquals(" =value", "=value", "");

    const doubled = cmdline.nextArg("==value rest") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("=", doubled.param);
    try std.testing.expectEqualStrings("value", doubled.value.?);
    try std.testing.expectEqualStrings("rest", doubled.remaining);
}

test "phase1 cmdline replay keeps quoted and alias leading equals tokens bare" {
    try expectBareLeadingEquals("\"=value with spaces\" tail", "=value with spaces", "tail");

    const quoted_pair = cmdline.next_arg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", quoted_pair.param);
    try std.testing.expectEqualStrings("fast path", quoted_pair.value.?);
    try std.testing.expectEqualStrings("tail", quoted_pair.remaining);

    const alias = cmdline.next_arg("=alias") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("=alias", alias.param);
    try std.testing.expect(alias.value == null);
    try std.testing.expectEqualStrings("", alias.remaining);
}