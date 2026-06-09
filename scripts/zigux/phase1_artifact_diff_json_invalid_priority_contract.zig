const std = @import("std");
const testing = std.testing;

const artifact_diff_py = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn expectBetween(haystack: []const u8, start: []const u8, needle: []const u8, end: []const u8) !void {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const end_index = std.mem.indexOfPos(u8, haystack, start_index, end) orelse return error.MissingEndMarker;
    const window = haystack[start_index..end_index];
    try expectContains(window, needle);
}

test "artifact diff self-test catalog keeps json invalid priority case ordered" {
    try expectBefore(
        artifact_diff_py,
        "    \"json_invalid_expected\",\n",
        "    \"json_invalid_actual\",\n",
    );
    try expectBefore(
        artifact_diff_py,
        "    \"json_invalid_actual\",\n",
        "    \"json_invalid_both\",\n",
    );
    try expectBefore(
        artifact_diff_py,
        "    \"json_invalid_both\",\n",
        "    \"json_missing_expected\",\n",
    );
}

test "compare_json fail-closes on expected decode errors before actual decode errors" {
    try expectBefore(
        artifact_diff_py,
        "    expected_bytes, expected_error = canonical_json_bytes(expected, side=\"EXPECTED\")\n",
        "    actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")\n",
    );
    try expectBefore(
        artifact_diff_py,
        "    if expected_error is not None:\n",
        "    if actual_error is not None:\n",
    );
    try expectBefore(
        artifact_diff_py,
        "        return ComparisonResult(ok=False, extra_lines=[expected_error])\n",
        "        return ComparisonResult(ok=False, extra_lines=[actual_error])\n",
    );
}

test "both-invalid json and utf8 self-test cases report the expected side only" {
    try expectBetween(
        artifact_diff_py,
        "            compare(\"json\", invalid_expected_json, invalid_actual_json).extra_lines\n",
        "            == [f\"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes\"],\n",
        "        covered.append(\"json_invalid_both\")\n",
    );
    try expectBetween(
        artifact_diff_py,
        "            compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines\n",
        "            == [f\"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte\"],\n",
        "        covered.append(\"json_invalid_both\")\n",
    );
    try expectBetween(
        artifact_diff_py,
        "            compare(\"json\", expected_json, invalid_actual_json).extra_lines\n",
        "            == [f\"ACTUAL_JSON_ERROR={invalid_actual_json}:2:1: Expecting property name enclosed in double quotes\"],\n",
        "        covered.append(\"json_invalid_actual\")\n",
    );
}
