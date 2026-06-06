const std = @import("std");
const testing = std.testing;

const artifact_diff_source = @embedFile("artifact_diff.py");

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |relative| {
        count += 1;
        index += relative + needle.len;
    }
    return count;
}

fn requireOnce(needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), countOccurrences(artifact_diff_source, needle));
}

fn requireContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) != null);
}

fn requireOrdered(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, artifact_diff_source[cursor..], marker) orelse {
            return error.MarkerOutOfOrder;
        };
        cursor += relative + marker.len;
    }
}

fn isCurrentArtifactDiff() bool {
    return std.mem.indexOf(u8, artifact_diff_source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") != null and
        std.mem.indexOf(u8, artifact_diff_source, "def main() -> int:") != null;
}

test "artifact diff main preserves parse self-test and missing-argument dispatch" {
    if (!isCurrentArtifactDiff()) return error.SkipZigTest;

    try requireOnce("def main() -> int:");
    try requireOnce("parsed = parse_args(sys.argv[1:])");
    try requireOnce("if isinstance(parsed, int):\n        return parsed");
    try requireOnce("self_test, mode, expected_text, actual_text = parsed");
    try requireOnce("if self_test:\n        return run_self_test()");
    try requireOnce("if mode is None or expected_text is None or actual_text is None:");
    try requireContains("print(MISSING_ARGUMENT_ERROR, file=sys.stderr)");
    try requireContains("return 2");

    try requireOrdered(&.{
        "def main() -> int:",
        "parsed = parse_args(sys.argv[1:])",
        "if isinstance(parsed, int):\n        return parsed",
        "self_test, mode, expected_text, actual_text = parsed",
        "if self_test:\n        return run_self_test()",
        "if mode is None or expected_text is None or actual_text is None:",
        "expected = Path(expected_text)",
    });
}

test "artifact diff main converts paths before compare and emits status from result" {
    if (!isCurrentArtifactDiff()) return error.SkipZigTest;

    try requireOnce("expected = Path(expected_text)");
    try requireOnce("actual = Path(actual_text)");
    try requireOnce("result = compare(mode, expected, actual)");
    try requireOnce("return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)");
    try requireOnce("def emit_result(status: str, mode: str, expected: Path, actual: Path, extra_lines: list[str]) -> int:");
    try requireOnce("return 0 if status == \"pass\" else 1");

    try requireOrdered(&.{
        "expected = Path(expected_text)",
        "actual = Path(actual_text)",
        "result = compare(mode, expected, actual)",
        "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)",
    });
}

test "artifact diff parse contract feeds main with stable tuple shape" {
    if (!isCurrentArtifactDiff()) return error.SkipZigTest;

    try requireOnce("def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:");
    try requireOnce("return self_test, mode, expected, actual");
    try requireOnce("if argv == [\"--help\"] or argv == [\"-h\"]:");
    try requireOnce("if arg == \"--self-test\":");
    try requireOnce("if arg == \"--mode\":");
    try requireOnce("if mode is not None and mode not in MODE_CHOICES:");
    try requireContains("if mode in LEGACY_MODE_ALIASES:");
    try requireContains("mode = LEGACY_MODE_ALIASES[mode]");

    try requireOrdered(&.{
        "def parse_args(argv: list[str])",
        "self_test = False",
        "mode: str | None = None",
        "positionals: list[str] = []",
        "if mode is not None and mode not in MODE_CHOICES:",
        "expected = positionals[0] if len(positionals) >= 1 else None",
        "actual = positionals[1] if len(positionals) >= 2 else None",
        "return self_test, mode, expected, actual",
        "def main() -> int:",
    });
}
