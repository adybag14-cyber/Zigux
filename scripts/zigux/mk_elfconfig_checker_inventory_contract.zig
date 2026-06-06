const std = @import("std");

const build_options = @import("build_options");

const expected_cases =
    \\[\n    \\  {\n    \\    "name": "elf32",\n    \\    "input": "elf32.hex",\n    \\    "expected": "elf32_expected.json"\n    \\  },\n    \\  {\n    \\    "name": "elf64",\n    \\    "input": "elf64.hex",\n    \\    "expected": "elf64_expected.json"\n    \\  },\n    \\  {\n    \\    "name": "invalid_class",\n    \\    "input": "invalid_class.hex",\n    \\    "expected": "invalid_class_expected.json"\n    \\  },\n    \\  {\n    \\    "name": "not_elf",\n    \\    "input": "not_elf.hex",\n    \\    "expected": "not_elf_expected.json"\n    \\  },\n    \\  {\n    \\    "name": "truncated",\n    \\    "input": "truncated.hex",\n    \\    "expected": "truncated_expected.json"\n    \\  }\n    \\]\n    \\\n;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeNeedle;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterNeedle;
    try std.testing.expect(before_index < after_index);
}

test "checker source keeps mk_elfconfig fixture inventory contract explicit" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, build_options.checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "ZIG_TOOL = ROOT / \"scripts\" / \"zigux\" / \"mk_elfconfig.zig\"");
    try expectContains(checker, "FIXTURE_DIR = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"mk_elfconfig\"");
    try expectContains(checker, "CASES_PATH = FIXTURE_DIR / \"cases.json\"");
    try expectContains(checker, "EXPECTED_CASES = {");
    try expectContains(checker, "\"elf32\": {\"input\": \"elf32.hex\", \"expected\": \"elf32_expected.json\"}");
    try expectContains(checker, "\"elf64\": {\"input\": \"elf64.hex\", \"expected\": \"elf64_expected.json\"}");
    try expectContains(checker, "\"invalid_class\": {\"input\": \"invalid_class.hex\", \"expected\": \"invalid_class_expected.json\"}");
    try expectContains(checker, "\"not_elf\": {\"input\": \"not_elf.hex\", \"expected\": \"not_elf_expected.json\"}");
    try expectContains(checker, "\"truncated\": {\"input\": \"truncated.hex\", \"expected\": \"truncated_expected.json\"}");
    try expectContains(checker, "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)");
    try expectContains(checker, "EXPECTED_FIXTURE_FILES = frozenset(");
    try expectContains(checker, "EXPECTED_RESULT_KEYS = frozenset({\"stdout\", \"stderr\", \"exit_code\"})");
    try expectContains(checker, "SELF_TEST_CASE_COUNT = 5");

    try expectOrdered(checker, "validate_fixture_inventory()", "validate_cases(load_json(CASES_PATH))");
    try expectOrdered(checker, "validate_expected_result(FIXTURE_DIR / case[\"expected\"])", "decode_hex_input(FIXTURE_DIR / case[\"input\"])");
    try expectOrdered(checker, "build_reference_c(compiler, c_binary)", "build_zig_tool(zig, zig_binary)");
    try expectOrdered(checker, "if c_result != expected:", "if zig_result != expected:");
    try expectOrdered(checker, "print(\"MK_ELFCONFIG_DIFF=pass\")", "print(f\"MK_ELFCONFIG_CASE_COUNT={len(cases)}\")");
    try expectOrdered(checker, "print(\"MK_ELFCONFIG_DIFF_SELF_TEST=pass\")", "print(f\"MK_ELFCONFIG_DIFF_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}\")");
}

test "cases manifest preserves the canonical five-case mk_elfconfig order" {
    const allocator = std.testing.allocator;
    const cases = try readFile(allocator, build_options.cases_path);
    defer allocator.free(cases);

    try std.testing.expectEqualStrings(expected_cases, cases);
}

test "checker rejects drift that would silently weaken the fixture contract" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, build_options.checker_path);
    defer allocator.free(checker);

    try std.testing.expect(std.mem.indexOf(u8, checker, "EXPECTED_RESULT_KEYS = frozenset({\"stdout\", \"exit_code\"})") == null);
    try std.testing.expect(std.mem.indexOf(u8, checker, "SELF_TEST_CASE_COUNT = 4") == null);
    try std.testing.expect(std.mem.indexOf(u8, checker, "EXPECTED_CASE_ORDER = sorted(EXPECTED_CASES)") == null);
    try std.testing.expect(std.mem.indexOf(u8, checker, "subprocess.run(cmd, check=False") == null);
    try expectOrdered(checker, "return 0", "if __name__ == \"__main__\"");
}
