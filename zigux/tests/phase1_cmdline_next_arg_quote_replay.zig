const std = @import("std");
const cmdline = @import("cmdline");

fn expectNextArg(
    args: []const u8,
    expected_param: []const u8,
    expected_value: ?[]const u8,
    expected_remaining: []const u8,
) !void {
    const parsed = cmdline.nextArg(args) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(expected_param, parsed.param);
    if (expected_value) |value| {
        try std.testing.expectEqualStrings(value, parsed.value.?);
    } else {
        try std.testing.expect(parsed.value == null);
    }
    try std.testing.expectEqualStrings(expected_remaining, parsed.remaining);
}

test "phase1 nextArg replay keeps quoted whole-token boundaries exact" {
    try expectNextArg(
        "\"mode=fast path\" root=/dev/sda1 rw",
        "mode",
        "fast path",
        "root=/dev/sda1 rw",
    );
    try expectNextArg(
        "console=\"ttyS0=115200 keep\" panic=-1",
        "console",
        "ttyS0=115200 keep",
        "panic=-1",
    );
    try expectNextArg(
        "root=\"UUID=alpha beta\" mode=fast=1",
        "root",
        "UUID=alpha beta",
        "mode=fast=1",
    );
}

test "phase1 nextArg replay keeps quoted edge values and alias calls aligned" {
    try expectNextArg(
        "\"=recovery shell\" next=tail",
        "",
        "recovery shell",
        "next=tail",
    );
    try expectNextArg(
        "root=\"\"   loglevel=7",
        "root",
        "",
        "loglevel=7",
    );

    const alias = cmdline.next_arg("flag quiet-mode") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("flag", alias.param);
    try std.testing.expect(alias.value == null);
    try std.testing.expectEqualStrings("quiet-mode", alias.remaining);
}
