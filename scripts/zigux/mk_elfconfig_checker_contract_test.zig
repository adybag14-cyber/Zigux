const std = @import("std");

const checker_source = @embedFile("check-mk-elfconfig-diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "mk_elfconfig checker keeps canonical fixture packet" {
    const expected_cases = [_][]const u8{
        "\"elf32\": {\"input\": \"elf32.hex\", \"expected\": \"elf32_expected.json\"}",
        "\"elf64\": {\"input\": \"elf64.hex\", \"expected\": \"elf64_expected.json\"}",
        "\"invalid_class\": {\"input\": \"invalid_class.hex\", \"expected\": \"invalid_class_expected.json\"}",
        "\"not_elf\": {\"input\": \"not_elf.hex\", \"expected\": \"not_elf_expected.json\"}",
        "\"truncated\": {\"input\": \"truncated.hex\", \"expected\": \"truncated_expected.json\"}",
    };
    for (expected_cases) |expected_case| {
        try expectContains(checker_source, expected_case);
    }

    const expected_fixture_files = [_][]const u8{
        "\"cases.json\"",
        "\"elf32.hex\"",
        "\"elf32_expected.json\"",
        "\"elf64.hex\"",
        "\"elf64_expected.json\"",
        "\"invalid_class.hex\"",
        "\"invalid_class_expected.json\"",
        "\"not_elf.hex\"",
        "\"not_elf_expected.json\"",
        "\"truncated.hex\"",
        "\"truncated_expected.json\"",
    };
    for (expected_fixture_files) |fixture_name| {
        try expectContains(checker_source, fixture_name);
    }

    try expectContains(checker_source, "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)");
    try expectContains(checker_source, "SELF_TEST_CASE_COUNT = 5");
    try expectContains(checker_source, "EXPECTED_RESULT_KEYS = frozenset({\"stdout\", \"stderr\", \"exit_code\"})");
}

test "mk_elfconfig checker self-test still validates inventory and result shape" {
    try expectContains(checker_source, "def validate_fixture_inventory()");
    try expectContains(checker_source, "def validate_cases(cases");
    try expectContains(checker_source, "def validate_expected_result(path");
    try expectContains(checker_source, "def run_self_test()");
    try expectContains(checker_source, "validate_fixture_inventory()");
    try expectContains(checker_source, "cases = validate_cases(load_json(CASES_PATH))");
    try expectContains(checker_source, "validate_expected_result(FIXTURE_DIR / case[\"expected\"])");
    try expectContains(checker_source, "decode_hex_input(FIXTURE_DIR / case[\"input\"])");
    try expectContains(checker_source, "MK_ELFCONFIG_DIFF_SELF_TEST=pass");
    try expectContains(checker_source, "MK_ELFCONFIG_DIFF_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}");
}

test "mk_elfconfig checker still compares C and Zig results against fixtures" {
    try expectContains(checker_source, "def build_reference_c(compiler");
    try expectContains(checker_source, "def build_zig_tool(zig");
    try expectContains(checker_source, "c_result = run_tool(c_binary, input_bytes)");
    try expectContains(checker_source, "zig_result = run_tool(zig_binary, input_bytes)");
    try expectContains(checker_source, "if c_result != expected:");
    try expectContains(checker_source, "if zig_result != expected:");
    try expectContains(checker_source, "if zig_result != c_result:");
    try expectContains(checker_source, "MK_ELFCONFIG_DIFF=pass");
    try expectContains(checker_source, "MK_ELFCONFIG_CASE_COUNT={len(cases)}");
}
