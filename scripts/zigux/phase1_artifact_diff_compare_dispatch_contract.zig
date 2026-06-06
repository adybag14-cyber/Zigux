const std = @import("std");

const source = @embedFile("artifact_diff.py");

fn has(needle: []const u8) bool {
    return std.mem.indexOf(u8, source, needle) != null;
}

fn spanBetween(start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, source, start_marker) orelse return error.StartMarkerMissing;
    const body_start = start + start_marker.len;
    const relative_end = std.mem.indexOf(u8, source[body_start..], end_marker) orelse return error.EndMarkerMissing;
    return source[body_start .. body_start + relative_end];
}

fn expectOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MarkerOutOfOrder;
        cursor += found + needle.len;
    }
}

fn currentArtifactDiffSource() bool {
    return has("MODE_CHOICES = (\"text\", \"json\", \"bytes\")") and
        has("def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:");
}

test "compare normalizes mode before path checks and dispatch" {
    if (!currentArtifactDiffSource()) return error.SkipZigTest;

    const compare_body = try spanBetween(
        "def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:\n",
        "\n\ndef emit_result",
    );

    try expectOrder(compare_body, &.{
        "mode = normalize_mode(mode)",
        "problem = path_problem_lines(expected, actual)",
        "if problem is not None:",
        "return ComparisonResult(ok=False, extra_lines=problem)",
        "if mode == \"text\":",
        "return compare_text(expected, actual)",
        "if mode == \"json\":",
        "return compare_json(expected, actual)",
        "if mode == \"bytes\":",
        "return compare_bytes(expected, actual)",
        "raise ValueError(f\"unsupported mode: {mode}\")",
    });
}

test "mode roster and legacy alias stay coupled to bytes dispatch" {
    if (!currentArtifactDiffSource()) return error.SkipZigTest;

    try std.testing.expect(has("MODE_CHOICES = (\"text\", \"json\", \"bytes\")"));
    try std.testing.expect(has("LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}"));
    try std.testing.expect(has("def normalize_mode(mode: str) -> str:\n    return LEGACY_MODE_ALIASES.get(mode, mode)"));

    const parser_body = try spanBetween(
        "def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:\n",
        "\n\ndef main()",
    );

    try expectOrder(parser_body, &.{
        "if mode is not None and mode not in MODE_CHOICES:",
        "if mode in LEGACY_MODE_ALIASES:",
        "mode = LEGACY_MODE_ALIASES[mode]",
        "else:",
        "print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)",
        "return 2",
    });
}

test "self-test covers dispatcher-owned mode and path boundaries" {
    if (!currentArtifactDiffSource()) return error.SkipZigTest;

    const self_test_body = try spanBetween(
        "def run_self_test() -> int:\n",
        "\n\ndef parse_args",
    );

    try expectOrder(self_test_body, &.{
        "compare(\"text\", expected, actual)",
        "compare(\"json\", expected_json, actual_json)",
        "compare(\"bytes\", blob_a, blob_b)",
        "compare(\"text\", missing, actual)",
        "compare(\"json\", missing, actual_json)",
        "compare(\"bytes\", missing, blob_a)",
        "run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])",
        "run_parser_probe([\"--mode\", \"yaml\", str(expected), str(actual)])",
    });

    try std.testing.expect(has("\"legacy_sha256_alias\""));
    try std.testing.expect(has("\"invalid_mode_rejected\""));
    try std.testing.expect(has("\"text_missing_expected\""));
    try std.testing.expect(has("\"json_missing_expected\""));
    try std.testing.expect(has("\"bytes_missing_expected\""));
}
