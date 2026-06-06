const std = @import("std");
const testing = std.testing;

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

fn isCurrentArtifactDiff() bool {
    return std.mem.indexOf(u8, source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") != null and
        std.mem.indexOf(u8, source, "SELF_TEST_CASES = [") != null;
}

fn requireCurrentArtifactDiff() !void {
    if (!isCurrentArtifactDiff()) return error.SkipZigTest;
}

fn requireContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireAbsent(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, source, needle) == null);
}

fn indexOfAfter(needle: []const u8, after: usize) !usize {
    const rel = std.mem.indexOf(u8, source[after..], needle) orelse return error.MissingMarker;
    return after + rel;
}

fn requireBefore(earlier: []const u8, later: []const u8) !void {
    const earlier_index = indexOfAfter(earlier, 0) catch return error.MissingMarker;
    const later_index = indexOfAfter(later, 0) catch return error.MissingMarker;
    try testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |rel| {
        count += 1;
        cursor += rel + needle.len;
    }
    return count;
}

fn literalFor(buffer: []u8, prefix: []const u8, case_name: []const u8, suffix: []const u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "{s}{s}{s}", .{ prefix, case_name, suffix });
}

test "artifact diff self-test case roster stays ordered and bytes-mode current" {
    try requireCurrentArtifactDiff();
    try requireContains("LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try requireContains("\"legacy_sha256_alias\",");
    try requireContains("\"bytes_pass\",");
    try requireContains("\"bytes_drift\",");
    try requireAbsent("\"sha256_pass\",");
    try requireAbsent("\"sha256_drift\",");

    const roster_start = try indexOfAfter("SELF_TEST_CASES = [", 0);
    const roster_end = try indexOfAfter("]\n\n\n@dataclass", roster_start);
    const roster = source[roster_start..roster_end];

    var cursor: usize = 0;
    for (expected_cases) |case_name| {
        var literal_buf: [80]u8 = undefined;
        const literal = try literalFor(&literal_buf, "\"", case_name, "\",");
        const rel = std.mem.indexOf(u8, roster[cursor..], literal) orelse return error.MissingCase;
        cursor += rel + literal.len;
    }

    try testing.expectEqual(@as(usize, expected_cases.len), countOccurrences(roster, "\","));
}

test "artifact diff self-test requires exact covered-case replay before success" {
    try requireCurrentArtifactDiff();

    var cursor = try indexOfAfter("covered: list[str] = []", 0);
    for (expected_cases) |case_name| {
        var append_buf: [96]u8 = undefined;
        const append_marker = try literalFor(&append_buf, "covered.append(\"", case_name, "\")");
        cursor = try indexOfAfter(append_marker, cursor);
    }

    const equality_marker = "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")";
    const first_print_marker = "print(\"ARTIFACT_DIFF_SELF_TEST=pass\")";
    try requireBefore(equality_marker, first_print_marker);
    try testing.expectEqual(@as(usize, expected_cases.len), countOccurrences(source, "covered.append("));
}

test "artifact diff self-test emits stable pass count and ordered case list" {
    try requireCurrentArtifactDiff();

    const pass_marker = "print(\"ARTIFACT_DIFF_SELF_TEST=pass\")";
    const count_marker = "print(f\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}\")";
    const cases_marker = "print(\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES))";
    const return_marker = "return 0";

    try requireBefore(pass_marker, count_marker);
    try requireBefore(count_marker, cases_marker);
    try requireBefore(cases_marker, return_marker);
    try requireBefore("if self_test:\n        return run_self_test()", "if mode is None or expected_text is None or actual_text is None:");
}
