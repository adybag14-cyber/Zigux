const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

const text_case_names = [_][]const u8{
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
};

const current_text_surface = [_][]const u8{
    "def compare_text(expected: Path, actual: Path) -> ComparisonResult:",
    "if read_bytes(expected) == read_bytes(actual):",
    "return ComparisonResult(ok=True, extra_lines=[])",
    "return ComparisonResult(ok=False, extra_lines=[])",
    "mode == \"text\"",
};

const legacy_text_surface = [_][]const u8{
    "if mode == 'text':",
    "expected_value = read_text(expected)",
    "actual_value = read_text(actual)",
    "assert_detail_shape(details, mode='text'",
    "render_result_lines(matched, details) == [",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |offset| {
        count += 1;
        index += offset + needle.len;
    }
    return count;
}

fn quotedCount(haystack: []const u8, name: []const u8) usize {
    var single_buffer: [128]u8 = undefined;
    var double_buffer: [128]u8 = undefined;
    const single = std.fmt.bufPrint(&single_buffer, "'{s}'", .{name}) catch unreachable;
    const double = std.fmt.bufPrint(&double_buffer, "\"{s}\"", .{name}) catch unreachable;
    return countOccurrences(haystack, single) + countOccurrences(haystack, double);
}

fn expectQuotedName(haystack: []const u8, name: []const u8) !void {
    try std.testing.expect(quotedCount(haystack, name) > 0);
}

test "artifact diff keeps text self-test catalog explicit" {
    try std.testing.expect(
        std.mem.indexOf(u8, artifact_diff_source, "SELF_TEST_CASES") != null or
            std.mem.indexOf(u8, artifact_diff_source, "EXPECTED_SELF_TEST_CASES") != null,
    );
    try expectContains(artifact_diff_source, "run_self_test");
    for (text_case_names) |name| {
        try expectQuotedName(artifact_diff_source, name);
    }

    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST_CASES=");
}

test "artifact diff text mode remains exact and separate from json and byte digest modes" {
    const has_current_surface =
        std.mem.indexOf(u8, artifact_diff_source, current_text_surface[0]) != null;
    const has_legacy_surface =
        std.mem.indexOf(u8, artifact_diff_source, legacy_text_surface[0]) != null;

    try std.testing.expect(has_current_surface or has_legacy_surface);
    try std.testing.expect(
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"json\"") != null or
            std.mem.indexOf(u8, artifact_diff_source, "mode == 'json'") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"bytes\"") != null or
            std.mem.indexOf(u8, artifact_diff_source, "mode == 'sha256'") != null,
    );

    if (has_current_surface) {
        try expectContainsAll(artifact_diff_source, &current_text_surface);
    } else {
        try expectContainsAll(artifact_diff_source, &legacy_text_surface);
    }
}

test "artifact diff text results report identity without digest noise" {
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF=pass");
    try expectContains(artifact_diff_source, "print(f\"ARTIFACT_DIFF={status}\")");
    try expectContains(artifact_diff_source, "\"pass\" if result.ok else \"fail\"");
    try expectContains(artifact_diff_source, "MODE=");
    try expectContains(artifact_diff_source, "EXPECTED=");
    try expectContains(artifact_diff_source, "ACTUAL=");

    const has_current_sha_surface =
        std.mem.indexOf(u8, artifact_diff_source, "def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:") != null;
    if (has_current_sha_surface) {
        try expectContains(artifact_diff_source, "return ComparisonResult(ok=True, extra_lines=[f\"SHA256={expected_digest}\"])");
    } else {
        try expectContains(artifact_diff_source, "if mode == 'sha256':");
        try expectContains(artifact_diff_source, "details['expected_sha256'] = expected_value");
        try expectContains(artifact_diff_source, "if 'expected_sha256' in details:");
    }

    try expectNotContains(artifact_diff_source, "text_sha256");
    try expectNotContains(artifact_diff_source, "TEXT_SHA256");
}

test "artifact diff text mode shares stable missing-file reporting" {
    const has_current_path_problem_surface =
        std.mem.indexOf(u8, artifact_diff_source, "def path_problem_lines(expected: Path, actual: Path)") != null;
    const has_current_missing_surface =
        std.mem.indexOf(u8, artifact_diff_source, "def missing_lines(expected: Path, actual: Path)") != null;
    if (has_current_path_problem_surface) {
        try expectContains(artifact_diff_source, "EXPECTED_EXISTS={expected_exists}");
        try expectContains(artifact_diff_source, "ACTUAL_EXISTS={actual_exists}");
        try expectContains(artifact_diff_source, "EXPECTED_IS_FILE={expected_is_file}");
        try expectContains(artifact_diff_source, "ACTUAL_IS_FILE={actual_is_file}");
    } else if (has_current_missing_surface) {
        try expectContains(artifact_diff_source, "EXPECTED_EXISTS={expected_exists}");
        try expectContains(artifact_diff_source, "ACTUAL_EXISTS={actual_exists}");
    } else {
        try expectContains(artifact_diff_source, "details['expected_exists'] = expected.exists()");
        try expectContains(artifact_diff_source, "details['actual_exists'] = actual.exists()");
        try expectContains(artifact_diff_source, "assert_detail_shape(details, mode='text'");
    }

    try expectQuotedName(artifact_diff_source, "text_missing_expected");
    try expectQuotedName(artifact_diff_source, "text_missing_actual");
    try expectQuotedName(artifact_diff_source, "text_missing_both");
}
