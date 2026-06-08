const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveMissingModeValueSurface(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") and
        std.mem.containsAtLeast(u8, source, 1, "MISSING_ARGUMENT_ERROR = (") and
        std.mem.containsAtLeast(u8, source, 1, "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:") and
        std.mem.containsAtLeast(u8, source, 1, "if arg == \"--mode\":") and
        std.mem.containsAtLeast(u8, source, 1, "missing_mode_value = run_parser_probe([\"--mode\"])");
}

fn requireLiveMissingModeValueSurface() !void {
    if (!hasLiveMissingModeValueSurface(artifact_diff_source)) {
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

test "missing mode value uses the shared required-argument diagnostic" {
    try requireLiveMissingModeValueSurface();

    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source,
        \\"usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source,
        \\"[expected] [actual] artifact_diff.py: error: --mode, expected, and actual "
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source,
        \\"are required unless --self-test is set"
    ) != null);
}

test "parser fail-closes before consuming a missing --mode value" {
    try requireLiveMissingModeValueSurface();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );
    const mode_branch = try bodyBetween(
        parse_body,
        "        if arg == \"--mode\":\n",
        "        positionals.append(arg)\n",
    );

    try std.testing.expect(std.mem.indexOf(u8, mode_branch, "            if index + 1 >= len(argv):\n                print(MISSING_ARGUMENT_ERROR, file=sys.stderr)\n                return 2\n") != null);
    try std.testing.expect((try indexOfNeedle(mode_branch, "if index + 1 >= len(argv):")) < (try indexOfNeedle(mode_branch, "mode = argv[index + 1]")));
    try std.testing.expect((try indexOfNeedle(mode_branch, "return 2")) < (try indexOfNeedle(mode_branch, "index += 2")));
}

test "self-test keeps missing mode value before missing positionals and invalid mode" {
    try requireLiveMissingModeValueSurface();

    const self_test_body = try bodyBetween(
        artifact_diff_source,
        "def run_self_test() -> int:\n",
        "\n\ndef parse_args",
    );
    try std.testing.expect((try indexOfNeedle(artifact_diff_source, "\"missing_mode_value_rejected\",")) < (try indexOfNeedle(artifact_diff_source, "\"missing_positional_arguments_rejected\",")));
    try std.testing.expect((try indexOfNeedle(artifact_diff_source, "\"missing_mode_value_rejected\",")) < (try indexOfNeedle(artifact_diff_source, "\"invalid_mode_rejected\",")));
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "missing_mode_value = run_parser_probe([\"--mode\"])") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "assert_case(missing_mode_value.returncode == 2, \"missing_mode_value_rejected\")") != null);
    try std.testing.expect((try indexOfNeedle(self_test_body, "missing_mode_value = run_parser_probe([\"--mode\"])")) < (try indexOfNeedle(self_test_body, "assert_case(missing_mode_value.returncode == 2, \"missing_mode_value_rejected\")")));
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "\" \".join(missing_mode_value.stderr.split()) == MISSING_ARGUMENT_ERROR") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "covered.append(\"missing_mode_value_rejected\")") != null);
}
