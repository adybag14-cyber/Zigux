const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn sliceBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const body_start = start_index + start.len;
    const end_offset = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + end_offset];
}

test "artifact diff emit_result keeps public output header order stable" {
    const emit_body = try sliceBetween(
        artifact_diff_source,
        "def emit_result(status: str, mode: str, expected: Path, actual: Path, extra_lines: list[str]) -> int:\n",
        "\n\ndef run_parser_probe",
    );

    try expectBefore(emit_body, "print(f\"ARTIFACT_DIFF={status}\")", "print(f\"MODE={mode}\")");
    try expectBefore(emit_body, "print(f\"MODE={mode}\")", "print(f\"EXPECTED={expected}\")");
    try expectBefore(emit_body, "print(f\"EXPECTED={expected}\")", "print(f\"ACTUAL={actual}\")");
    try expectBefore(emit_body, "print(f\"ACTUAL={actual}\")", "for line in extra_lines:");
    try expectBefore(emit_body, "for line in extra_lines:", "print(line)");
    try expectBefore(emit_body, "print(line)", "return 0 if status == \"pass\" else 1");
}

test "artifact diff main emits the normalized parsed mode instead of recomputing display state" {
    const main_body = try sliceBetween(
        artifact_diff_source,
        "def main() -> int:\n",
        "\n\nif __name__ == \"__main__\":",
    );

    try expectContains(main_body, "parsed = parse_args(sys.argv[1:])");
    try expectBefore(main_body, "self_test, mode, expected_text, actual_text = parsed", "result = compare(mode, expected, actual)");
    try expectBefore(main_body, "result = compare(mode, expected, actual)", "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)");
}

test "artifact diff parser normalizes legacy modes before result emission" {
    const parse_body = try sliceBetween(
        artifact_diff_source,
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main() -> int:",
    );

    try expectContains(artifact_diff_source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(artifact_diff_source, "def normalize_mode(mode: str) -> str:");
    try expectContains(artifact_diff_source, "return LEGACY_MODE_ALIASES.get(mode, mode)");
    try expectBefore(parse_body, "if mode in LEGACY_MODE_ALIASES:", "mode = LEGACY_MODE_ALIASES[mode]");
    try expectBefore(parse_body, "mode = LEGACY_MODE_ALIASES[mode]", "return self_test, mode, expected, actual");
}
