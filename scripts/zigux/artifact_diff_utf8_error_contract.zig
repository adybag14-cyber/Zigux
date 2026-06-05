const std = @import("std");

const artifact_diff = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

test "json utf8 errors use stable side-prefixed sentinels" {
    try expectContains(artifact_diff, "def format_utf8_error(path: Path, *, side: str, exc: UnicodeDecodeError) -> str:");
    try expectContains(artifact_diff, "return f\"{side}_UTF8_ERROR={path}:{exc.start}: {exc.reason}\"");
    try expectContains(artifact_diff, "except UnicodeDecodeError as exc:");
    try expectContains(artifact_diff, "format_utf8_error(path, side=side, exc=exc)");
    try expectContains(artifact_diff, "EXPECTED_UTF8_ERROR=");
    try expectContains(artifact_diff, "ACTUAL_UTF8_ERROR=");
}

test "json utf8 probes stay paired with invalid json probes" {
    try expectContains(artifact_diff, "invalid_expected_utf8_json = root / \"invalid-expected-utf8.json\"");
    try expectContains(artifact_diff, "invalid_actual_utf8_json = root / \"invalid-actual-utf8.json\"");
    try expectContains(artifact_diff, "invalid_expected_utf8_json.write_bytes(b\"\\xff{\\n\")");
    try expectContains(artifact_diff, "invalid_actual_utf8_json.write_bytes(b\"\\xff{\\n\")");
    try expectContains(artifact_diff, "compare(\"json\", invalid_expected_utf8_json, actual_json).extra_lines");
    try expectContains(artifact_diff, "compare(\"json\", expected_json, invalid_actual_utf8_json).extra_lines");
    try expectContains(artifact_diff, "compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines");

    try expectBefore(artifact_diff, "invalid_expected_utf8_json.write_bytes", "compare(\"json\", invalid_expected_utf8_json, actual_json).extra_lines");
    try expectBefore(artifact_diff, "invalid_actual_utf8_json.write_bytes", "compare(\"json\", expected_json, invalid_actual_utf8_json).extra_lines");
}

test "expected-side utf8 failure keeps precedence when both sides are invalid" {
    try expectContains(artifact_diff, "compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines");
    try expectContains(artifact_diff, "== [f\"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte\"]");
    try std.testing.expect(countOccurrences(artifact_diff, "json_invalid_both") >= 2);
    try expectBefore(
        artifact_diff,
        "expected_bytes, expected_error = canonical_json_bytes(expected, side=\"EXPECTED\")",
        "actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")",
    );
    try expectBefore(
        artifact_diff,
        "if expected_error is not None:",
        "if actual_error is not None:",
    );
}

test "self-test catalog retains json invalid case slots" {
    try expectContains(artifact_diff, "SELF_TEST_CASES = [");
    try expectContains(artifact_diff, "\"json_invalid_expected\",");
    try expectContains(artifact_diff, "\"json_invalid_actual\",");
    try expectContains(artifact_diff, "\"json_invalid_both\",");
    try expectContains(artifact_diff, "print(\"ARTIFACT_DIFF_SELF_TEST=pass\")");
    try expectContains(artifact_diff, "print(f\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}\")");
    try expectContains(artifact_diff, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")");
}
