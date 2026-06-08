const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveTerminatorBoundary(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:") and
        std.mem.containsAtLeast(u8, source, 1, "if arg == \"--self-test\":") and
        std.mem.containsAtLeast(u8, source, 1, "if arg == \"--mode\":") and
        std.mem.containsAtLeast(u8, source, 1, "positionals.append(arg)") and
        std.mem.containsAtLeast(u8, source, 1, "expected = positionals[0] if len(positionals) >= 1 else None") and
        std.mem.containsAtLeast(u8, source, 1, "if len(positionals) > 2:") and
        std.mem.containsAtLeast(u8, source, 1, "if mode is None or expected_text is None or actual_text is None:") and
        std.mem.containsAtLeast(u8, source, 1, "result = compare(mode, expected, actual)");
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
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    try std.testing.expect(std.mem.indexOf(u8, parse_body, "if arg == \"--\":") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "arg == \"--\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "argv[index + 1:]") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "positionals.extend") == null);
}

test "dash dash tokens fall through as ordinary positionals" {
    try requireLiveTerminatorBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    const self_test_branch = try indexOfNeedle(parse_body, "if arg == \"--self-test\":");
    const mode_branch = try indexOfNeedle(parse_body, "if arg == \"--mode\":");
    const append_positional = try indexOfNeedle(parse_body, "positionals.append(arg)");
    const expected_assignment = try indexOfNeedle(parse_body, "expected = positionals[0] if len(positionals) >= 1 else None");
    const too_many_check = try indexOfNeedle(parse_body, "if len(positionals) > 2:");
    const tuple_return = try indexOfNeedle(parse_body, "return self_test, mode, expected, actual");

    try std.testing.expect(self_test_branch < append_positional);
    try std.testing.expect(mode_branch < append_positional);
    try std.testing.expect(append_positional < expected_assignment);
    try std.testing.expect(expected_assignment < too_many_check);
    try std.testing.expect(too_many_check < tuple_return);
}

test "missing mode remains the post-parse executable boundary" {
    try requireLiveTerminatorBoundary();

    const main_body = try bodyBetween(
        artifact_diff_source,
        "def main() -> int:\n",
        "\n\nif __name__ == \"__main__\":",
    );

    try std.testing.expect(std.mem.indexOf(u8, main_body, "self_test, mode, expected_text, actual_text = parsed") != null);
    try std.testing.expect(std.mem.indexOf(u8, main_body, "if mode is None or expected_text is None or actual_text is None:") != null);
    try std.testing.expect(std.mem.indexOf(u8, main_body, "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)") != null);
    try std.testing.expect((try indexOfNeedle(main_body, "if mode is None or expected_text is None or actual_text is None:")) < (try indexOfNeedle(main_body, "result = compare(mode, expected")));
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, "\"terminator") == null);
}
