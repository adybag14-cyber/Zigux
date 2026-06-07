const std = @import("std");

const source = @embedFile("artifact_diff.py");

const expected_cases = [_][]const u8{
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
};

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, source, needle) != null;
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, source[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    return count;
}

fn indexOf(needle: []const u8) !usize {
    return std.mem.indexOf(u8, source, needle) orelse error.MissingMarker;
}

test "artifact diff self-test roster remains complete and ordered" {
    try std.testing.expect(contains("SELF_TEST_CASES = ["));
    try std.testing.expectEqual(@as(usize, 23), expected_cases.len);

    var previous_index: usize = 0;
    for (expected_cases, 0..) |case_name, index| {
        const quoted = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\"", .{case_name});
        defer std.testing.allocator.free(quoted);

        try std.testing.expect(countOccurrences(quoted) >= 1);
        const current_index = try indexOf(quoted);
        if (index > 0) {
            try std.testing.expect(current_index > previous_index);
        }
        previous_index = current_index;
    }

    try std.testing.expect(contains("assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")"));
}

test "artifact diff self-test output exposes the dynamic case count and roster" {
    try std.testing.expect(contains("print(\"ARTIFACT_DIFF_SELF_TEST=pass\")"));
    try std.testing.expect(contains("print(f\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}\")"));
    try std.testing.expect(contains("print(\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES))"));
    try std.testing.expect(!contains("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=22"));
    try std.testing.expect(!contains("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=24"));
}

test "artifact diff self-test coverage includes every CLI and comparison family" {
    const required_markers = [_][]const u8{
        "text_pass",
        "json_invalid_both",
        "bytes_drift",
        "legacy_sha256_alias",
        "missing_mode_value_rejected",
        "missing_positional_arguments_rejected",
        "invalid_mode_rejected",
        "extra_positional_rejected",
    };

    for (required_markers) |marker| {
        const covered_marker = try std.fmt.allocPrint(std.testing.allocator, "covered.append(\"{s}\")", .{marker});
        defer std.testing.allocator.free(covered_marker);
        try std.testing.expect(contains(covered_marker));
    }
}
