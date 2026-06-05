const std = @import("std");

const artifact_diff_py = @embedFile("artifact_diff.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireLiveArtifactDiff() !void {
    if (std.mem.indexOf(u8, artifact_diff_py, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") == null) {
        return error.SkipZigTest;
    }
}

test "artifact diff path problem guard owns stable missing and non-file markers" {
    try requireLiveArtifactDiff();

    try requireContains(artifact_diff_py, "def path_problem_lines(expected: Path, actual: Path) -> list[str] | None:");
    try requireContains(artifact_diff_py, "expected_exists = expected.exists()");
    try requireContains(artifact_diff_py, "actual_exists = actual.exists()");
    try requireContains(artifact_diff_py, "EXPECTED_EXISTS={expected_exists}");
    try requireContains(artifact_diff_py, "ACTUAL_EXISTS={actual_exists}");
    try requireContains(artifact_diff_py, "expected_is_file = expected.is_file()");
    try requireContains(artifact_diff_py, "actual_is_file = actual.is_file()");
    try requireContains(artifact_diff_py, "EXPECTED_IS_FILE={expected_is_file}");
    try requireContains(artifact_diff_py, "ACTUAL_IS_FILE={actual_is_file}");

    try requireBefore(artifact_diff_py, "if not expected_exists or not actual_exists:", "expected_is_file = expected.is_file()");
    try requireBefore(artifact_diff_py, "if expected_is_file and actual_is_file:", "return [\n        f\"EXPECTED_IS_FILE={expected_is_file}\"");
}

test "artifact diff compare runs path validation before mode dispatch" {
    try requireLiveArtifactDiff();

    const compare_start = std.mem.indexOf(u8, artifact_diff_py, "def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:") orelse return error.MissingCompare;
    const compare_body = artifact_diff_py[compare_start..];
    try requireBefore(compare_body, "problem = path_problem_lines(expected, actual)", "if mode == \"text\":");
    try requireBefore(compare_body, "problem = path_problem_lines(expected, actual)", "if mode == \"json\":");
    try requireBefore(compare_body, "problem = path_problem_lines(expected, actual)", "if mode == \"bytes\":");
    try requireBefore(compare_body, "return ComparisonResult(ok=False, extra_lines=problem)", "if mode == \"text\":");
}

test "artifact diff self-test catalog keeps path cases before parser probes" {
    try requireLiveArtifactDiff();

    try requireContains(artifact_diff_py, "\"json_missing_expected\",");
    try requireContains(artifact_diff_py, "\"json_missing_actual\",");
    try requireContains(artifact_diff_py, "\"json_missing_both\",");
    try requireContains(artifact_diff_py, "\"text_missing_expected\",");
    try requireContains(artifact_diff_py, "\"text_missing_actual\",");
    try requireContains(artifact_diff_py, "\"text_missing_both\",");
    try requireContains(artifact_diff_py, "\"bytes_missing_expected\",");
    try requireContains(artifact_diff_py, "\"bytes_missing_actual\",");
    try requireContains(artifact_diff_py, "\"bytes_missing_both\",");
    try requireContains(artifact_diff_py, "\"legacy_sha256_alias\",");
    try requireContains(artifact_diff_py, "\"missing_mode_value_rejected\",");
    try requireContains(artifact_diff_py, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")");

    try requireBefore(artifact_diff_py, "\"json_missing_both\",", "\"bytes_pass\",");
    try requireBefore(artifact_diff_py, "\"bytes_missing_both\",", "\"legacy_sha256_alias\",");
    try requireBefore(artifact_diff_py, "\"legacy_sha256_alias\",", "\"missing_mode_value_rejected\",");
    try requireBefore(artifact_diff_py, "\"invalid_mode_rejected\",", "\"extra_positional_rejected\",");
}
