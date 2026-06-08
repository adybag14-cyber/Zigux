const std = @import("std");

const installer = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectOrderedAfter(haystack: []const u8, anchor: []const u8, first: []const u8, second: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    const first_relative = std.mem.indexOf(u8, haystack[anchor_index..], first) orelse return error.MissingFirstMarker;
    const second_relative = std.mem.indexOf(u8, haystack[anchor_index..], second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_relative < second_relative);
}

test "install-zig curl path keeps retry and resume before stall guards" {
    const cmd_anchor = "cmd = [\n        'curl',";
    try expectOrderedAfter(installer, cmd_anchor, "'--retry',", "'--speed-limit',");
    try expectOrderedAfter(installer, cmd_anchor, "'--speed-limit',", "'--speed-time',");
    try expectOrderedAfter(installer, cmd_anchor, "'--speed-time',", "'--continue-at',");
    try expectOrderedAfter(installer, cmd_anchor, "'--continue-at',", "'--output',");
    try expectContains(installer, "'--retry-all-errors'");
    try expectContains(installer, "'--continue-at'");
    try expectContains(installer, "'--speed-limit'");
    try expectContains(installer, "'--speed-time'");
}

test "install-zig curl stall guard derives bounds from timeout" {
    try expectContains(installer, "str(max(5, int(timeout // 4)))");
    try expectContains(installer, "'--speed-limit',\n        '1',");
    try expectContains(installer, "str(max(30, int(timeout)))");
    try expectOrdered(
        installer,
        "'--connect-timeout',\n        str(max(5, int(timeout // 4)))",
        "'--speed-limit',\n        '1'",
    );
    try expectOrdered(
        installer,
        "'--speed-limit',\n        '1'",
        "'--speed-time',\n        str(max(30, int(timeout)))",
    );
}

test "install-zig self-test keeps curl stall guard coverage" {
    try expectContains(installer, "curl_commands: list[list[str]] = []");
    try expectContains(installer, "copy_url_to_file_with_curl(");
    try expectContains(installer, "timeout=90.0");
    try expectContains(installer, "assert '--continue-at' in curl_commands[0]");
    try expectContains(installer, "assert '--retry-all-errors' in curl_commands[0]");
}
