const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveParseTupleBoundary(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n") and
        std.mem.containsAtLeast(u8, source, 1, "return self_test, mode, expected, actual") and
        std.mem.containsAtLeast(u8, source, 1, "parsed = parse_args(sys.argv[1:])") and
        std.mem.containsAtLeast(u8, source, 1, "if isinstance(parsed, int):") and
        std.mem.containsAtLeast(u8, source, 1, "self_test, mode, expected_text, actual_text = parsed") and
        std.mem.containsAtLeast(u8, source, 1, "result = compare(mode, expected, actual)");
}

fn requireLiveParseTupleBoundary() !void {
    if (!hasLiveParseTupleBoundary(artifact_diff_source)) {
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

test "parse args keeps the int-or-four-field result boundary" {
    try requireLiveParseTupleBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    try std.testing.expect(std.mem.indexOf(u8, parse_body, "self_test = False") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "mode: str | None = None") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "positionals: list[str] = []") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "return 0") != null);
    try std.testing.expect(std.mem.containsAtLeast(u8, parse_body, 3, "return 2"));
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "expected = positionals[0] if len(positionals) >= 1 else None") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "actual = positionals[1] if len(positionals) >= 2 else None") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "return self_test, mode, expected, actual") != null);
}

test "parse tuple is emitted only after option validation and arity checks" {
    try requireLiveParseTupleBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    try std.testing.expect((try indexOfNeedle(parse_body, "if index + 1 >= len(argv):")) < (try indexOfNeedle(parse_body, "mode = argv[index + 1]")));
    try std.testing.expect((try indexOfNeedle(parse_body, "if mode is not None and mode not in MODE_CHOICES:")) < (try indexOfNeedle(parse_body, "expected = positionals[0] if len(positionals) >= 1 else None")));
    try std.testing.expect((try indexOfNeedle(parse_body, "if mode in LEGACY_MODE_ALIASES:")) < (try indexOfNeedle(parse_body, "print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)")));
    try std.testing.expect((try indexOfNeedle(parse_body, "expected = positionals[0] if len(positionals) >= 1 else None")) < (try indexOfNeedle(parse_body, "if len(positionals) > 2:")));
    try std.testing.expect((try indexOfNeedle(parse_body, "if len(positionals) > 2:")) < (try indexOfNeedle(parse_body, "return self_test, mode, expected, actual")));
}

test "main consumes parse result before self-test, path, compare, and emit work" {
    try requireLiveParseTupleBoundary();

    const main_body = try bodyBetween(
        artifact_diff_source,
        "def main() -> int:\n",
        "\n\nif __name__ == \"__main__\":",
    );

    try std.testing.expect((try indexOfNeedle(main_body, "parsed = parse_args(sys.argv[1:])")) < (try indexOfNeedle(main_body, "if isinstance(parsed, int):")));
    try std.testing.expect((try indexOfNeedle(main_body, "if isinstance(parsed, int):")) < (try indexOfNeedle(main_body, "self_test, mode, expected_text, actual_text = parsed")));
    try std.testing.expect((try indexOfNeedle(main_body, "self_test, mode, expected_text, actual_text = parsed")) < (try indexOfNeedle(main_body, "if self_test:")));
    try std.testing.expect((try indexOfNeedle(main_body, "if self_test:")) < (try indexOfNeedle(main_body, "if mode is None or expected_text is None or actual_text is None:")));
    try std.testing.expect((try indexOfNeedle(main_body, "if mode is None or expected_text is None or actual_text is None:")) < (try indexOfNeedle(main_body, "expected = Path(expected_text)")));
    try std.testing.expect((try indexOfNeedle(main_body, "actual = Path(actual_text)")) < (try indexOfNeedle(main_body, "result = compare(mode, expected, actual)")));
    try std.testing.expect((try indexOfNeedle(main_body, "result = compare(mode, expected, actual)")) < (try indexOfNeedle(main_body, "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)")));
}
