const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.zig");

fn hasLiveTerminatorBoundary(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "pub fn main(init: std.process.Init) !void {") and
        std.mem.containsAtLeast(u8, source, 1, "if (std.mem.eql(u8, arg, \"--self-test\"))") and
        std.mem.containsAtLeast(u8, source, 1, "if (std.mem.eql(u8, arg, \"--mode\"))") and
        std.mem.containsAtLeast(u8, source, 1, "try positionals.append(allocator, arg);") and
        std.mem.containsAtLeast(u8, source, 1, "if (mode == null or positionals.items.len < 2)") and
        std.mem.containsAtLeast(u8, source, 1, "if (positionals.items.len > 2)") and
        std.mem.containsAtLeast(u8, source, 1, "const result = try compare(io, allocator, mode.?, positionals.items[0], positionals.items[1]);");
}

fn requireLiveTerminatorBoundary() !void {
    if (!hasLiveTerminatorBoundary(artifact_diff_source)) {
        return error.SkipZigTest;
    }
}

fn indexOfNeedle(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingNeedle;
}

fn bodyBetween(source: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = try indexOfNeedle(source, start_marker);
    const body_start = start + start_marker.len;
    const end_rel = std.mem.indexOf(u8, source[body_start..], end_marker) orelse return error.MissingNeedle;
    return source[body_start .. body_start + end_rel];
}

test "parser has no dash dash option terminator branch" {
    try requireLiveTerminatorBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "pub fn main(init: std.process.Init) !void {\n",
        "\nfn emitStderrLine",
    );

    try std.testing.expect(std.mem.indexOf(u8, parse_body, "if (std.mem.eql(u8, arg, \"--\"):") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "arg == \"--\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "argv[index + 1..]") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "positionals.appendSlice") == null);
}

test "dash dash tokens fall through as ordinary positionals" {
    try requireLiveTerminatorBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "pub fn main(init: std.process.Init) !void {\n",
        "\nfn emitStderrLine",
    );

    const self_test_branch = try indexOfNeedle(parse_body, "if (std.mem.eql(u8, arg, \"--self-test\"))");
    const mode_branch = try indexOfNeedle(parse_body, "if (std.mem.eql(u8, arg, \"--mode\"))");
    const append_positional = try indexOfNeedle(parse_body, "try positionals.append(allocator, arg);");
    const missing_mode_check = try indexOfNeedle(parse_body, "if (mode == null or positionals.items.len < 2)");
    const too_many_check = try indexOfNeedle(parse_body, "if (positionals.items.len > 2)");
    const compare_call = try indexOfNeedle(parse_body, "const result = try compare(io, allocator, mode.?, positionals.items[0], positionals.items[1]);");

    try std.testing.expect(self_test_branch < append_positional);
    try std.testing.expect(mode_branch < append_positional);
    try std.testing.expect(append_positional < missing_mode_check);
    try std.testing.expect(missing_mode_check < too_many_check);
    try std.testing.expect(too_many_check < compare_call);
}

test "missing mode remains the post-parse executable boundary" {
    try requireLiveTerminatorBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "pub fn main(init: std.process.Init) !void {\n",
        "\nfn emitStderrLine",
    );

    try std.testing.expect(std.mem.indexOf(u8, parse_body, "if (mode == null or positionals.items.len < 2)") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "try emitStderrLine(io, missing_argument_error);") != null);
    try std.testing.expect((try indexOfNeedle(parse_body, "if (mode == null or positionals.items.len < 2)")) < (try indexOfNeedle(parse_body, "const result = try compare(io, allocator, mode.?, positionals.items[0], positionals.items[1]);")));
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, "\"terminator") == null);
}