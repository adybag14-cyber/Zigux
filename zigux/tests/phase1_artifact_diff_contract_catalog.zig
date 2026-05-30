const std = @import("std");

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

const base_contract_cases = [_][]const u8{
    "helper_self_test",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_mode_value",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "cli_extra_positional_args",
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
    "bytes_pass",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "bytes_drift",
};

const repeat_contract_cases = [_][]const u8{
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "bytes_drift_repeat",
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

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCaseArray(source: []const u8, name: []const u8, cases: []const []const u8) !void {
    try expectContains(source, name);
    for (cases) |case_name| {
        try expectContains(source, case_name);
    }
}

fn expectUniqueCases(cases: []const []const u8) !void {
    for (cases, 0..) |case_name, index| {
        for (cases[0..index]) |prior| {
            try std.testing.expect(!std.mem.eql(u8, case_name, prior));
        }
    }
}

test "phase1 artifact diff helper catalog stays pinned in the contract checker" {
    const checker = try readRepoFile("scripts/zigux/check-artifact-diff-contract.py", 96 * 1024);
    defer std.testing.allocator.free(checker);

    try expectCaseArray(checker, "HELPER_SELF_TEST_CASES", &helper_self_test_cases);
    try expectContains(checker, "ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContains(checker, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_SELF_TEST_CASES=");
    try expectUniqueCases(&helper_self_test_cases);
}

test "phase1 artifact diff contract checker preserves base and repeat gates" {
    const checker = try readRepoFile("scripts/zigux/check-artifact-diff-contract.py", 96 * 1024);
    defer std.testing.allocator.free(checker);

    try expectCaseArray(checker, "BASE_CONTRACT_CASES", &base_contract_cases);
    try expectCaseArray(checker, "REPEAT_CONTRACT_CASES", &repeat_contract_cases);
    try expectContains(checker, "ALL_CONTRACT_CASES = BASE_CONTRACT_CASES + REPEAT_CONTRACT_CASES");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT=pass");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=");
    try expectUniqueCases(&base_contract_cases);
    try expectUniqueCases(&repeat_contract_cases);
}

test "phase1 artifact diff contract self-test catalog stays review visible" {
    const checker = try readRepoFile("scripts/zigux/check-artifact-diff-contract.py", 96 * 1024);
    defer std.testing.allocator.free(checker);

    try expectCaseArray(checker, "SELF_TEST_CASES", &checker_self_test_cases);
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=");
    try expectContains(checker, "host-side artifact-diff tooling contract");
    try expectContains(checker, "owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`");
    try expectUniqueCases(&checker_self_test_cases);
}
