const std = @import("std");

const artifact_diff_py = @embedFile("artifact_diff.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "artifact diff parser keeps stable mode catalog and legacy alias" {
    try requireContains(artifact_diff_py, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try requireContains(artifact_diff_py, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try requireContains(artifact_diff_py, "normalize_mode(mode)");
    try requireContains(artifact_diff_py, "\"legacy_sha256_alias\"");
    try requireContains(artifact_diff_py, "MODE=bytes");

    try requireBefore(
        artifact_diff_py,
        "if mode is not None and mode not in MODE_CHOICES:",
        "if mode is None or expected_text is None or actual_text is None:",
    );
}

test "artifact diff parser errors stay deterministic" {
    try requireContains(artifact_diff_py, "MISSING_ARGUMENT_ERROR = (");
    try requireContains(artifact_diff_py, "INVALID_MODE_ERROR_TEMPLATE = (");
    try requireContains(artifact_diff_py, "TOO_MANY_ARGUMENTS_ERROR = (");
    try requireContains(artifact_diff_py, "missing_mode_value_rejected");
    try requireContains(artifact_diff_py, "missing_positional_arguments_rejected");
    try requireContains(artifact_diff_py, "invalid_mode_rejected");
    try requireContains(artifact_diff_py, "extra_positional_rejected");

    try requireBefore(artifact_diff_py, "if argv == [\"--help\"] or argv == [\"-h\"]:", "if arg == \"--self-test\":");
    try requireBefore(artifact_diff_py, "if len(positionals) > 2:", "return self_test, mode, expected, actual");
}

test "artifact diff self-test roster pins parser cases after core modes" {
    try requireContains(artifact_diff_py, "SELF_TEST_CASES = [");
    try requireBefore(artifact_diff_py, "\"bytes_missing_both\",", "\"legacy_sha256_alias\",");
    try requireBefore(artifact_diff_py, "\"legacy_sha256_alias\",", "\"missing_mode_value_rejected\",");
    try requireBefore(artifact_diff_py, "\"missing_mode_value_rejected\",", "\"missing_positional_arguments_rejected\",");
    try requireBefore(artifact_diff_py, "\"missing_positional_arguments_rejected\",", "\"invalid_mode_rejected\",");
    try requireBefore(artifact_diff_py, "\"invalid_mode_rejected\",", "\"extra_positional_rejected\",");
    try requireContains(artifact_diff_py, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
    try requireContains(artifact_diff_py, "ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)");
}
