const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.zig");

fn hasLiveInlineModeBoundary(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "pub const Mode = enum {") and
        std.mem.containsAtLeast(u8, source, 1, "if (std.mem.eql(u8, raw, \"sha256\")) return .bytes;") and
        std.mem.containsAtLeast(u8, source, 1, "if (std.mem.eql(u8, arg, \"--mode\"))") and
        std.mem.containsAtLeast(u8, source, 1, "mode = Mode.parse(argv[index]) orelse") and
        std.mem.containsAtLeast(u8, source, 1, "try positionals.append(allocator, arg);") and
        std.mem.containsAtLeast(u8, source, 1, "if (positionals.items.len > 2)");
}

fn requireLiveInlineModeBoundary() !void {
    if (!hasLiveInlineModeBoundary(artifact_diff_source)) {
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

test "help and parser expose only separated mode values" {
    try requireLiveInlineModeBoundary();

    const help_body = try bodyBetween(
        artifact_diff_source,
        "const help =\n",
        ";\n        var stdout_buffer",
    );
    try std.testing.expect(std.mem.indexOf(u8, help_body, "--mode {text,json,bytes}") != null);
    try std.testing.expect(std.mem.indexOf(u8, help_body, "--mode={text,json,bytes}") == null);

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "pub fn main(init: std.process.Init) !void {\n",
        "\nfn emitStderrLine",
    );
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "if (std.mem.eql(u8, arg, \"--mode\"))") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "startsWith(\"--mode=\")") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "splitScalar(u8, arg, '=')") == null);
}

test "inline mode tokens fall through the positional path" {
    try requireLiveInlineModeBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "pub fn main(init: std.process.Init) !void {\n",
        "\nfn emitStderrLine",
    );

    try std.testing.expect((try indexOfNeedle(parse_body, "if (std.mem.eql(u8, arg, \"--mode\"))")) < (try indexOfNeedle(parse_body, "try positionals.append(allocator, arg);")));
    try std.testing.expect((try indexOfNeedle(parse_body, "try positionals.append(allocator, arg);")) < (try indexOfNeedle(parse_body, "if (mode == null or positionals.items.len < 2)")));
    try std.testing.expect((try indexOfNeedle(parse_body, "if (mode == null or positionals.items.len < 2)")) < (try indexOfNeedle(parse_body, "if (positionals.items.len > 2)")));
    try std.testing.expect((try indexOfNeedle(parse_body, "if (positionals.items.len > 2)")) < (try indexOfNeedle(parse_body, "const result = try compare(io, allocator, mode.?, positionals.items[0], positionals.items[1]);")));
}

test "missing mode remains the executable boundary after inline positional parsing" {
    try requireLiveInlineModeBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "pub fn main(init: std.process.Init) !void {\n",
        "\nfn emitStderrLine",
    );

    try std.testing.expect(std.mem.indexOf(u8, parse_body, "if (mode == null or positionals.items.len < 2)") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "try emitStderrLine(io, missing_argument_error);") != null);
    try std.testing.expect((try indexOfNeedle(parse_body, "if (mode == null or positionals.items.len < 2)")) < (try indexOfNeedle(parse_body, "const result = try compare(io, allocator, mode.?, positionals.items[0], positionals.items[1]);")));
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, "\"inline_mode") == null);
}