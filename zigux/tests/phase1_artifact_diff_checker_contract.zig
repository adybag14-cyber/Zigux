const std = @import("std");
const options = @import("artifact_diff_checker_contract_options");

const checker_source = options.checker_source;
const helper_source = options.helper_source;

const helper_self_test_cases = [_][]const u8{
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
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "invalid_mode_rejected",
};

const base_contract_cases = [_][]const u8{
    "helper_self_test",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
};

const repeat_contract_cases = [_][]const u8{
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
};

const checker_self_test_cases = [_][]const u8{
    "catalog_shape",
    "review_note_marker_round_trip",
    "review_note_owner_marker_drift",
    "review_note_marker_drift",
    "cli_help_round_trip",
    "cli_help_line_drift",
    "cli_missing_argument_parser_round_trip",
    "cli_missing_argument_parser_stderr_drift",
    "cli_invalid_mode_parser_round_trip",
    "cli_invalid_mode_parser_stderr_drift",
    "helper_summary_round_trip",
    "contract_summary_round_trip",
    "helper_summary_status_drift",
    "helper_summary_count_drift",
    "helper_summary_duplicate_case_drift",
    "helper_summary_case_order_drift",
    "contract_summary_status_drift",
    "contract_summary_base_count_drift",
    "contract_summary_base_case_order_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_repeat_case_order_drift",
    "contract_summary_case_count_drift",
    "contract_summary_duplicate_case_drift",
    "contract_summary_case_order_drift",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContainsAny(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (contains(haystack, needle)) return;
    }
    try std.testing.expect(false);
}

fn expectExactOccurrences(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |found| {
        count += 1;
        offset = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectUniqueCatalog(comptime cases: []const []const u8) !void {
    for (cases, 0..) |case, index| {
        for (cases[0..index]) |previous| {
            try std.testing.expect(!std.mem.eql(u8, case, previous));
        }
    }
}

test "artifact diff contract checker keeps helper binding and summary markers" {
    try expectContainsAny(checker_source, &.{
        "HELPER_REL = Path(\"scripts\") / \"zigux\" / \"artifact_diff.py\"",
        "ARTIFACT_DIFF = ROOT / \"scripts\" / \"zigux\" / \"artifact_diff.py\"",
    });
    try expectContains(checker_source, "BASE_CONTRACT_CASES = [");
    try expectContains(checker_source, "REPEAT_CONTRACT_CASES = [");
    try expectContainsAny(checker_source, &.{
        "ALL_CONTRACT_CASES = BASE_CONTRACT_CASES + REPEAT_CONTRACT_CASES",
        "EXPECTED_CONTRACT_CASES = [",
    });
    try expectContains(checker_source, "\"ARTIFACT_DIFF_CONTRACT=pass\"");
    try expectContains(checker_source, "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=");
    try expectContains(checker_source, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=");
    try expectContains(checker_source, "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=");
    try expectContains(checker_source, "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass");
    try expectContains(checker_source, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=");
    try expectContains(checker_source, "owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`");
    try expectContains(checker_source, "rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`");
    try expectContains(checker_source, "ARTIFACT_DIFF_CONTRACT_CASES=");
}

test "artifact diff helper and checker catalogs stay aligned" {
    try expectUniqueCatalog(helper_self_test_cases[0..]);
    try expectUniqueCatalog(base_contract_cases[0..]);
    try expectUniqueCatalog(repeat_contract_cases[0..]);
    try expectUniqueCatalog(checker_self_test_cases[0..]);

    try expectContainsAny(helper_source, &.{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "choices=['text', 'json', 'sha256']",
    });
    try expectContainsAny(checker_source, &.{
        "HELPER_SELF_TEST_CASES = [",
        "EXPECTED_CONTRACT_CASES = [",
    });

    for (helper_self_test_cases) |case| {
        try expectContains(helper_source, case);
        try expectContains(checker_source, case);
    }
    for (base_contract_cases) |case| {
        try expectContains(checker_source, case);
    }
    for (repeat_contract_cases) |case| {
        try expectContains(checker_source, case);
    }
    for (checker_self_test_cases) |case| {
        try expectContains(checker_source, case);
    }

    const live_digest_mode = contains(helper_source, "bytes_pass") and
        contains(checker_source, "bytes_drift_repeat");
    const legacy_digest_mode = contains(helper_source, "sha256_pass") and
        contains(checker_source, "sha256_drift_repeat");
    try std.testing.expect(live_digest_mode or legacy_digest_mode);
}

test "checker fail-closes parser, repeatability, and digest drift cases" {
    try expectContainsAny(checker_source, &.{ "MISSING_ARGUMENT_ERROR = (", "MISSING_ARGUMENT_ERROR_NORMALIZED = (" });
    try expectContainsAny(checker_source, &.{ "INVALID_MODE_ERROR = (", "INVALID_MODE_ERROR_NORMALIZED = (" });
    try expectContainsAny(checker_source, &.{ "run_error_case(", "run_error_contract_case(" });
    try expectContains(checker_source, "repeat_count=2");
    try expectContains(checker_source, "SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576");
    try expectContains(checker_source, "EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576");
    try expectContains(checker_source, "ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94");
    try expectContains(checker_source, "helper_self_test_repeat");
    if (contains(checker_source, "bytes_drift_repeat")) {
        try expectContains(checker_source, "bytes_drift_repeat");
    } else {
        try expectContains(checker_source, "sha256_drift_repeat");
    }
}
