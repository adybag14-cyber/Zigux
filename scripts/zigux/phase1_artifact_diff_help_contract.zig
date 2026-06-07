const std = @import("std");
const testing = std.testing;

const artifact_diff = @embedFile("artifact_diff.py");

const current_self_test_cases = [_][]const u8{
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

const legacy_self_test_cases = [_][]const u8{
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
    "sha256_pass",
    "sha256_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "invalid_mode_rejected",
};

fn requireNeedle(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn requireCaseOrder(haystack: []const u8, cases: []const []const u8) !void {
    var cursor: usize = 0;
    for (cases) |case_name| {
        const index = std.mem.indexOfPos(u8, haystack, cursor, case_name) orelse return error.MissingSelfTestCase;
        cursor = index + case_name.len;
    }
}

fn isCurrentArtifactDiff() bool {
    return std.mem.indexOf(u8, artifact_diff, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") != null;
}

test "current artifact diff help surface is pinned when bytes mode is present" {
    if (!isCurrentArtifactDiff()) return error.SkipZigTest;

    try requireNeedle(artifact_diff, "HELP_LINES = [");
    try requireNeedle(artifact_diff, "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]");
    try requireNeedle(artifact_diff, "Compare two artifacts in a stable mode.");
    try requireNeedle(artifact_diff, "--mode {text,json,bytes}");
    try requireNeedle(artifact_diff, "--self-test Run built-in deterministic comparison checks.");
    try requireNeedle(artifact_diff, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try requireNeedle(artifact_diff, "MISSING_ARGUMENT_ERROR = (");
    try requireNeedle(artifact_diff, "TOO_MANY_ARGUMENTS_ERROR = (");
    try requireNeedle(artifact_diff, "INVALID_MODE_ERROR_TEMPLATE = (");
    try requireNeedle(artifact_diff, "if argv == [\"--help\"] or argv == [\"-h\"]:");
    try requireNeedle(artifact_diff, "if mode in LEGACY_MODE_ALIASES:");
    try requireOrdered(artifact_diff, "\"bytes\"", "\"legacy_sha256_alias\"");
}

test "current artifact diff self-test catalog keeps bytes and parser cases ordered" {
    if (!isCurrentArtifactDiff()) return error.SkipZigTest;

    try requireNeedle(artifact_diff, "SELF_TEST_CASES = [");
    try requireNeedle(artifact_diff, "ARTIFACT_DIFF_SELF_TEST=pass");
    try requireNeedle(artifact_diff, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}");
    try requireNeedle(artifact_diff, "ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)");
    try requireCaseOrder(artifact_diff, current_self_test_cases[0..]);
    try testing.expect(current_self_test_cases.len == 23);
    try requireOrdered(artifact_diff, "\"bytes_missing_both\"", "\"legacy_sha256_alias\"");
    try requireOrdered(artifact_diff, "\"missing_mode_value_rejected\"", "\"extra_positional_rejected\"");
}

test "legacy artifact diff scaffold remains validation-compatible only before bytes mode" {
    if (isCurrentArtifactDiff()) return error.SkipZigTest;

    try requireNeedle(artifact_diff, "EXPECTED_SELF_TEST_CASES = [");
    try requireNeedle(artifact_diff, "sha256_pass");
    try requireNeedle(artifact_diff, "sha256_drift");
    try requireNeedle(artifact_diff, "invalid_mode_rejected");
    try requireCaseOrder(artifact_diff, legacy_self_test_cases[0..]);
    try testing.expect(legacy_self_test_cases.len == 19);
}
