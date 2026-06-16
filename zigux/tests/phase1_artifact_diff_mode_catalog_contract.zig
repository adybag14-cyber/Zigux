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
    try expectContains(helper_source, "pub const Mode = enum {");
    try expectContains(helper_source, "if (std.mem.eql(u8, raw, \"sha256\")) return .bytes;");
    try expectContains(helper_source, "MODE={s}");
    try expectContains(helper_source, "mode.name()");

    try expectContains(helper_source, ".text => try compareText");
    try expectContains(helper_source, ".json => try compareJson");
    try expectContains(helper_source, ".bytes => try compareBytes");
}

test "artifact diff parser errors cover required operands and invalid modes" {
    try expectContains(helper_source, "const missing_argument_error =");
    try expectContains(helper_source, "const too_many_arguments_error =");
    try expectContains(helper_source, "are required unless --self-test is set");
    try expectContains(helper_source, "invalid choice: '{s}' (choose from text, json, bytes)");
    try expectContains(helper_source, "expected exactly two positional ");
    try expectContains(helper_source, "arguments");
}

test "artifact diff self-test catalog keeps every mode and failure branch" {
    try expectUnique(expected_self_test_cases[0..]);
    try expectContains(helper_source, "pub const self_test_case_names = [_][]const u8{");
    try expectContains(helper_source, "self_test_case_names.len");
    try expectContains(helper_source, "ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContains(helper_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
    try expectContains(helper_source, "ARTIFACT_DIFF_SELF_TEST_CASES=");

    for (expected_self_test_cases) |case| {
        try expectContains(helper_source, case);
    }
}

test "artifact diff digest mode reports stable bytes labels" {
    try expectContains(helper_source, "SHA256={s}");
    try expectContains(helper_source, "EXPECTED_SHA256={s}");
    try expectContains(helper_source, "ACTUAL_SHA256={s}");
    try expectContains(helper_source, "EXPECTED_EXISTS={s}");
    try expectContains(helper_source, "ACTUAL_EXISTS={s}");
}