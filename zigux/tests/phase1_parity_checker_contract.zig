const std = @import("std");

const expected_sections = [_][]const u8{
    "\"find_bit\"",
    "\"bitmap\"",
    "\"string\"",
    "\"rbtree\"",
    "\"argv_split\"",
    "\"cmdline\"",
    "\"ctype\"",
    "\"hweight\"",
    "\"list_sort\"",
    "\"zalloc\"",
    "\"str_error_r\"",
    "\"slab\"",
    "\"vsprintf\"",
};

const required_fixture_keys = [_][]const u8{
    "\"inclusive_boundary_next\"",
    "\"tail_clamped_first\"",
    "\"truncated_scnprintf_len\"",
    "\"truncated_scnprintf\"",
    "\"replace_char_cstr_bytes\"",
    "\"next_match_terminal_null\"",
    "\"bool_sorted_ordinals\"",
    "\"zero_after_kmalloc\"",
    "\"scnprintf_text\"",
};

test "phase1 parity checker keeps the required file packet" {
    const files = try readContractFiles();
    defer files.deinit();

    try expectMarker(files.parity_checker, "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try expectMarker(files.parity_checker, "HARNESS_REL = Path(\"zigux/tests/fixtures/phase1_helpers_c_harness.c\")");
    try expectMarker(files.parity_checker, "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.py\")");
    try expectMarker(files.parity_checker, "missing:");
    try expectMarker(files.parity_checker, "PHASE1_PARITY=fail");
    try expectMarker(files.parity_checker, "PHASE1_PARITY=pass");
}

test "phase1 parity checker and fixture keep the canonical section roster" {
    const files = try readContractFiles();
    defer files.deinit();

    for (expected_sections) |section| {
        try expectMarker(files.parity_checker, section);
        try expectFixtureSection(files.phase1_fixture, section);
    }
}

test "phase1 parity checker keeps artifact diff and self-test output markers" {
    const files = try readContractFiles();
    defer files.deinit();

    try expectMarker(files.parity_checker, "artifact_diff");
    try expectMarker(files.parity_checker, "--self-test");
    try expectMarker(files.parity_checker, "PHASE1_PARITY_SELF_TEST=pass");
    try expectMarker(files.parity_checker, "PHASE1_PARITY_SELF_TEST_CASE_COUNT=");
}

test "phase1 parity checker and fixture share sentinel key coverage" {
    const files = try readContractFiles();
    defer files.deinit();

    for (required_fixture_keys) |key| {
        try expectMarker(files.parity_checker, key);
        try expectMarker(files.phase1_fixture, key);
    }
}

const ContractFiles = struct {
    parity_checker: []const u8,
    phase1_fixture: []const u8,

    fn deinit(self: ContractFiles) void {
        std.testing.allocator.free(self.parity_checker);
        std.testing.allocator.free(self.phase1_fixture);
    }
};

fn readContractFiles() !ContractFiles {
    const allocator = std.testing.allocator;
    return .{
        .parity_checker = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            "scripts/zigux/check-phase1-parity.py",
            allocator,
            .limited(512 * 1024),
        ),
        .phase1_fixture = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            "zigux/tests/fixtures/phase1_helpers.json",
            allocator,
            .limited(256 * 1024),
        ),
    };
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn expectFixtureSection(phase1_fixture: []const u8, section: []const u8) !void {
    const key_start = std.mem.indexOf(u8, phase1_fixture, section) orelse return error.TestUnexpectedResult;
    var after_key = phase1_fixture[key_start + section.len ..];
    after_key = trimLeadingWhitespace(after_key);
    try std.testing.expect(std.mem.startsWith(u8, after_key, ":"));
    after_key = trimLeadingWhitespace(after_key[1..]);
    try std.testing.expect(std.mem.startsWith(u8, after_key, "{"));
}

fn trimLeadingWhitespace(input: []const u8) []const u8 {
    var index: usize = 0;
    while (index < input.len and isWhitespace(input[index])) : (index += 1) {}
    return input[index..];
}

fn isWhitespace(byte: u8) bool {
    return byte == ' ' or byte == '\n' or byte == '\r' or byte == '\t';
}
