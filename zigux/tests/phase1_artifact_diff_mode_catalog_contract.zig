const std = @import("std");
const options = @import("artifact_diff_mode_catalog_contract_options");

const helper_source = options.helper_source;

const expected_self_test_cases = [_][]const u8{
    "\"text_pass\"",
    "\"text_mismatch\"",
    "\"json_pass\"",
    "\"json_mismatch\"",
    "\"json_invalid_expected\"",
    "\"json_invalid_actual\"",
    "\"json_invalid_both\"",
    "\"json_missing_expected\"",
    "\"json_missing_actual\"",
    "\"json_missing_both\"",
    "\"bytes_pass\"",
    "\"bytes_drift\"",
    "\"text_missing_expected\"",
    "\"text_missing_actual\"",
    "\"text_missing_both\"",
    "\"bytes_missing_expected\"",
    "\"bytes_missing_actual\"",
    "\"bytes_missing_both\"",
    "\"legacy_sha256_alias\"",
    "\"missing_mode_value_rejected\"",
    "\"missing_positional_arguments_rejected\"",
    "\"invalid_mode_rejected\"",
    "\"extra_positional_rejected\"",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectUnique(comptime items: []const []const u8) !void {
    for (items, 0..) |item, index| {
        for (items[0..index]) |previous| {
            try std.testing.expect(!std.mem.eql(u8, item, previous));
        }
    }
}

test "artifact diff mode roster stays canonical" {
    try expectContains(helper_source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(helper_source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(helper_source, "MODE={mode}");
    try expectContains(helper_source, "mode = LEGACY_MODE_ALIASES[mode]");

    try expectContains(helper_source, "if mode == \"text\":");
    try expectContains(helper_source, "if mode == \"json\":");
    try expectContains(helper_source, "if mode == \"bytes\":");
}

test "artifact diff parser errors cover required operands and invalid modes" {
    try expectContains(helper_source, "MISSING_ARGUMENT_ERROR = (");
    try expectContains(helper_source, "INVALID_MODE_ERROR_TEMPLATE = (");
    try expectContains(helper_source, "TOO_MANY_ARGUMENTS_ERROR = (");
    try expectContains(helper_source, "are required unless --self-test is set");
    try expectContains(helper_source, "invalid ");
    try expectContains(helper_source, "choice: {value!r} (choose from text, json, bytes)");
    try expectContains(helper_source, "expected exactly two positional ");
    try expectContains(helper_source, "arguments");
}

test "artifact diff self-test catalog keeps every mode and failure branch" {
    try expectUnique(expected_self_test_cases[0..]);
    try expectContains(helper_source, "SELF_TEST_CASES = [");
    try expectContains(helper_source, "covered == SELF_TEST_CASES");
    try expectContains(helper_source, "ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContains(helper_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
    try expectContains(helper_source, "ARTIFACT_DIFF_SELF_TEST_CASES=");

    for (expected_self_test_cases) |case| {
        try expectContains(helper_source, case);
    }
}

test "artifact diff digest mode reports stable bytes labels" {
    try expectContains(helper_source, "SHA256={expected_digest}");
    try expectContains(helper_source, "EXPECTED_SHA256={expected_digest}");
    try expectContains(helper_source, "ACTUAL_SHA256={actual_digest}");
    try expectContains(helper_source, "EXPECTED_EXISTS={expected_exists}");
    try expectContains(helper_source, "ACTUAL_EXISTS={actual_exists}");
}
