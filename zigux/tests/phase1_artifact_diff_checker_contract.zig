const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase 1 artifact-diff checker keeps its published contract catalog visible" {
    const checker = try readRepoFile("scripts/zigux/check-artifact-diff-contract.py", 128 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "artifact_diff.py");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT=pass");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_BASE_CASES=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_CASES=");

    try expectContains(checker, "helper_self_test");
    try expectContains(checker, "cli_missing_mode_value");
    try expectContains(checker, "cli_missing_actual_operand");
    try expectContains(checker, "text_missing_both");
    try expectContains(checker, "json_invalid_both");
    try expectContains(checker, "bytes_drift_repeat");
    try expectContains(checker, "BASE_CONTRACT_CASES");
    try expectContains(checker, "REPEAT_CONTRACT_CASES");
}

test "phase 1 artifact-diff checker self-test guards catalog drift" {
    const checker = try readRepoFile("scripts/zigux/check-artifact-diff-contract.py", 128 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=");
    try expectContains(checker, "catalog_shape");
    try expectContains(checker, "review_note_marker_round_trip");
    try expectContains(checker, "helper_summary_duplicate_case_drift");
    try expectContains(checker, "contract_summary_duplicate_case_drift");
    try expectContains(checker, "contract_summary_case_order_drift");
    try expectOrdered(checker, "helper_summary_round_trip", "contract_summary_round_trip");
}

test "phase 1 artifact-diff helper keeps stable outward line markers" {
    const helper = try readRepoFile("scripts/zigux/artifact_diff.py", 96 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(helper, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(helper, "canonical_json_bytes");
    try expectContains(helper, "sha256_hex");
    try expectContains(helper, "ARTIFACT_DIFF=pass");
    try expectContains(helper, "ARTIFACT_DIFF=fail");
    try expectContains(helper, "MODE=");
    try expectContains(helper, "EXPECTED=");
    try expectContains(helper, "ACTUAL=");
    try expectContains(helper, "EXPECTED_EXISTS=False");
    try expectContains(helper, "ACTUAL_EXISTS=False");
    try expectContains(helper, "EXPECTED_JSON_ERROR=");
    try expectContains(helper, "ACTUAL_JSON_ERROR=");
    try expectContains(helper, "EXPECTED_SHA256=");
    try expectContains(helper, "ACTUAL_SHA256=");
}
