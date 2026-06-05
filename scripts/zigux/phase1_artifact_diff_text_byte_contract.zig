const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");
const current_mode_marker = "MODE_CHOICES = (\"text\", \"json\", \"bytes\")";

fn requireCurrentArtifactDiff() !void {
    if (!std.mem.containsAtLeast(u8, artifact_diff_source, 1, current_mode_marker)) {
        return error.SkipZigTest;
    }
}

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) []const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return "";
    const after_start = haystack[start..];
    const end = std.mem.indexOf(u8, after_start, end_marker) orelse return after_start;
    return after_start[0..end];
}

fn assertContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn assertOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "artifact diff text mode stays byte exact rather than utf8 decoded" {
    try requireCurrentArtifactDiff();

    const compare_text = sliceBetween(
        artifact_diff_source,
        "def compare_text(expected: Path, actual: Path) -> ComparisonResult:",
        "def compare_json(expected: Path, actual: Path) -> ComparisonResult:",
    );

    try assertContains(compare_text, "if read_bytes(expected) == read_bytes(actual):");
    try assertContains(compare_text, "return ComparisonResult(ok=True, extra_lines=[])");
    try assertContains(compare_text, "return ComparisonResult(ok=False, extra_lines=[])");
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text, 1, "load_text("));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text, 1, "format_utf8_error("));
}

test "artifact diff dispatch keeps text before json and bytes modes" {
    try requireCurrentArtifactDiff();

    const compare_dispatch = sliceBetween(
        artifact_diff_source,
        "def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:",
        "def emit_result(status: str, mode: str, expected: Path, actual: Path, extra_lines: list[str]) -> int:",
    );

    try assertContains(compare_dispatch, "problem = path_problem_lines(expected, actual)");
    try assertContains(compare_dispatch, "if mode == \"text\":");
    try assertContains(compare_dispatch, "return compare_text(expected, actual)");
    try assertContains(compare_dispatch, "if mode == \"json\":");
    try assertContains(compare_dispatch, "if mode == \"bytes\":");
    try assertOrder(compare_dispatch, "if mode == \"text\":", "if mode == \"json\":");
    try assertOrder(compare_dispatch, "if mode == \"json\":", "if mode == \"bytes\":");
}

test "artifact diff text self-test catalog remains explicitly covered" {
    try requireCurrentArtifactDiff();

    const self_tests = sliceBetween(
        artifact_diff_source,
        "SELF_TEST_CASES = [",
        "]",
    );

    try assertOrder(self_tests, "\"text_pass\"", "\"text_mismatch\"");
    try assertOrder(self_tests, "\"text_mismatch\"", "\"json_pass\"");
    try assertOrder(self_tests, "\"text_missing_expected\"", "\"text_missing_actual\"");
    try assertOrder(self_tests, "\"text_missing_actual\"", "\"text_missing_both\"");
    try assertOrder(self_tests, "\"text_missing_both\"", "\"bytes_missing_expected\"");
    try assertContains(artifact_diff_source, "actual.write_text(\"alpha\\nBETA\\n\", encoding=\"utf-8\", newline=\"\\n\")");
    try assertContains(artifact_diff_source, "assert_case(not compare(\"text\", expected, actual).ok, \"text_mismatch\")");
}
