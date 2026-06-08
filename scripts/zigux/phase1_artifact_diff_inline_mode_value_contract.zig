const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveInlineModeBoundary(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") and
        std.mem.containsAtLeast(u8, source, 1, "HELP_LINES = [") and
        std.mem.containsAtLeast(u8, source, 1, "if arg == \"--mode\":") and
        std.mem.containsAtLeast(u8, source, 1, "mode = argv[index + 1]") and
        std.mem.containsAtLeast(u8, source, 1, "positionals.append(arg)") and
        std.mem.containsAtLeast(u8, source, 1, "if mode is not None and mode not in MODE_CHOICES:") and
        std.mem.containsAtLeast(u8, source, 1, "if len(positionals) > 2:");
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
        "HELP_LINES = [\n",
        "\n]\nMISSING_ARGUMENT_ERROR = (",
    );
    try std.testing.expect(std.mem.indexOf(u8, help_body, "--mode {text,json,bytes}") != null);
    try std.testing.expect(std.mem.indexOf(u8, help_body, "--mode={text,json,bytes}") == null);

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "if arg == \"--mode\":") != null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "arg.startswith(\"--mode=\")") == null);
    try std.testing.expect(std.mem.indexOf(u8, parse_body, "arg.split(\"=\", 1)") == null);
}

test "inline mode tokens fall through the positional path" {
    try requireLiveInlineModeBoundary();

    const parse_body = try bodyBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    try std.testing.expect((try indexOfNeedle(parse_body, "if arg == \"--mode\":")) < (try indexOfNeedle(parse_body, "positionals.append(arg)")));
    try std.testing.expect((try indexOfNeedle(parse_body, "positionals.append(arg)")) < (try indexOfNeedle(parse_body, "expected = positionals[0] if len(positionals) >= 1 else None")));
    try std.testing.expect((try indexOfNeedle(parse_body, "expected = positionals[0] if len(positionals) >= 1 else None")) < (try indexOfNeedle(parse_body, "if len(positionals) > 2:")));
    try std.testing.expect((try indexOfNeedle(parse_body, "if len(positionals) > 2:")) < (try indexOfNeedle(parse_body, "return self_test, mode, expected, actual")));
}

test "missing mode remains the executable boundary after inline positional parsing" {
    try requireLiveInlineModeBoundary();

    const main_body = try bodyBetween(
        artifact_diff_source,
        "def main() -> int:\n",
        "\n\nif __name__ == \"__main__\":",
    );

    try std.testing.expect(std.mem.indexOf(u8, main_body, "self_test, mode, expected_text, actual_text = parsed") != null);
    try std.testing.expect(std.mem.indexOf(u8, main_body, "if mode is None or expected_text is None or actual_text is None:") != null);
    try std.testing.expect(std.mem.indexOf(u8, main_body, "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)") != null);
    try std.testing.expect((try indexOfNeedle(main_body, "if mode is None or expected_text is None or actual_text is None:")) < (try indexOfNeedle(main_body, "result = compare(mode, expected, actual)")));
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, "\"inline_mode") == null);
}
