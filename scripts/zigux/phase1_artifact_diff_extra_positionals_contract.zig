const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveExtraPositionalsSurface(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "TOO_MANY_ARGUMENTS_ERROR = (") and
        std.mem.containsAtLeast(u8, source, 1, "\"extra_positional_rejected\",") and
        std.mem.containsAtLeast(u8, source, 1, "extra_positional = run_parser_probe(") and
        std.mem.containsAtLeast(u8, source, 1, "if len(positionals) > 2:") and
        std.mem.containsAtLeast(u8, source, 1, "print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)");
}

fn requireLiveExtraPositionalsSurface() !void {
    if (!hasLiveExtraPositionalsSurface(artifact_diff_source)) {
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

test "too many positionals use a dedicated parser diagnostic" {
    try requireLiveExtraPositionalsSurface();

    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source,
        \\"usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source,
        \\"[expected] [actual] artifact_diff.py: error: expected exactly two positional "
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source,
        \\"arguments"
    ) != null);
}

test "parser rejects extra positionals after mode validation" {
    try requireLiveExtraPositionalsSurface();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    try std.testing.expect((try indexOfNeedle(parse_body, "if mode is not None and mode not in MODE_CHOICES:")) < (try indexOfNeedle(parse_body, "if len(positionals) > 2:")));
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "    if len(positionals) > 2:\n        print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)\n        return 2\n") != null);
    try std.testing.expect((try indexOfNeedle(parse_body, "if len(positionals) > 2:")) < (try indexOfNeedle(parse_body, "return self_test, mode, expected, actual")));
}

test "self-test pins the extra positional probe and error wording" {
    try requireLiveExtraPositionalsSurface();

    const self_test_body = try bodyBetween(
        artifact_diff_source,
        "def run_self_test() -> int:\n",
        "\n\ndef parse_args",
    );

    try std.testing.expect((try indexOfNeedle(artifact_diff_source, "\"missing_positional_arguments_rejected\",")) < (try indexOfNeedle(artifact_diff_source, "\"extra_positional_rejected\",")));
    try std.testing.expect((try indexOfNeedle(artifact_diff_source, "\"invalid_mode_rejected\",")) < (try indexOfNeedle(artifact_diff_source, "\"extra_positional_rejected\",")));
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "extra_positional = run_parser_probe(") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "[\"--mode\", \"text\", str(expected), str(actual), str(missing)]") != null);
    try std.testing.expect((try indexOfNeedle(self_test_body, "extra_positional = run_parser_probe(")) < (try indexOfNeedle(self_test_body, "[\"--mode\", \"text\", str(expected), str(actual), str(missing)]")));
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "assert_case(extra_positional.returncode == 2, \"extra_positional_rejected\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "\" \".join(extra_positional.stderr.split()) == TOO_MANY_ARGUMENTS_ERROR") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "covered.append(\"extra_positional_rejected\")") != null);
}
