const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-bench.py";

const ExactChecksumDiagnostic = struct {
    kind: []const u8,
    print_marker: []const u8,
};

const exact_checksum_diagnostics = [_]ExactChecksumDiagnostic{
    .{
        .kind = "expectations_duplicate_exact_checksum_keys",
        .print_marker = "DUPLICATE_EXPECTATION_EXACT_CHECKSUM_KEYS_START",
    },
    .{
        .kind = "expectations_exact_checksum_key_type",
        .print_marker = "EXPECTATIONS_EXACT_CHECKSUM_KEY_TYPE",
    },
    .{
        .kind = "expectations_exact_checksum_value_type",
        .print_marker = "EXPECTATIONS_EXACT_CHECKSUM_VALUE_TYPE",
    },
    .{
        .kind = "expectations_exact_checksum_nonpositive",
        .print_marker = "EXPECTATIONS_EXACT_CHECKSUM_NONPOSITIVE_KEY",
    },
    .{
        .kind = "expectations_exact_checksum_not_listed",
        .print_marker = "EXPECTATIONS_EXACT_CHECKSUM_NOT_LISTED",
    },
    .{
        .kind = "expectations_missing_find_bit_exact_checksums",
        .print_marker = "MISSING_EXPECTATION_FIND_BIT_EXACT_CHECKSUMS_START",
    },
    .{
        .kind = "expectations_missing_exact_checksums",
        .print_marker = "MISSING_EXPECTATION_EXACT_CHECKSUMS_START",
    },
    .{
        .kind = "expectations_unexpected_exact_checksums",
        .print_marker = "UNEXPECTED_EXPECTATION_EXACT_CHECKSUMS_START",
    },
};

fn readChecker() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        std.testing.allocator,
        .limited(192 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    try std.testing.expect(try indexOfRequired(haystack, before) < try indexOfRequired(haystack, after));
}

test "phase1 bench checker exposes exact-checksum expectation diagnostics" {
    const checker = try readChecker();
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "exact_checksums = expectations.get('exact_checksums')");
    try expectContains(checker, "DuplicateTrackingDict) and exact_checksums.duplicate_keys");
    try expectContains(checker, "actual_exact_checksum_keys = set()");
    try expectContains(checker, "if key not in actual_checksum_set:");
    try expectContains(checker, "missing_find_bit_exact_checksums = sorted(REQUIRED_FIND_BIT_EXACT_CHECKSUMS - actual_exact_checksum_keys)");
    try expectContains(checker, "missing_exact_checksums = sorted(REQUIRED_EXACT_CHECKSUMS - actual_exact_checksum_keys)");
    try expectContains(checker, "unexpected_exact_checksums = sorted(actual_exact_checksum_keys - REQUIRED_EXACT_CHECKSUMS)");

    inline for (exact_checksum_diagnostics) |diagnostic| {
        try expectContains(checker, diagnostic.kind);
        try expectContains(checker, diagnostic.print_marker);
    }
}

test "phase1 bench checker keeps exact-checksum validation fail-closed before bench execution" {
    const checker = try readChecker();
    defer std.testing.allocator.free(checker);

    const validation_start = "exact_checksums = expectations.get('exact_checksums')";
    const command_start = "result = subprocess.run([";
    try expectBefore(checker, validation_start, command_start);

    const ordering = [_][]const u8{
        "expectations_exact_checksums_type",
        "expectations_duplicate_exact_checksum_keys",
        "expectations_exact_checksum_key_type",
        "expectations_exact_checksum_value_type",
        "expectations_exact_checksum_nonpositive",
        "expectations_exact_checksum_not_listed",
        "expectations_missing_find_bit_exact_checksums",
        "expectations_missing_exact_checksums",
        "expectations_unexpected_exact_checksums",
        "return ('pass', expectations)",
    };
    inline for (ordering[0 .. ordering.len - 1], ordering[1..]) |before, after| {
        try expectBefore(checker, before, after);
    }
}

test "phase1 bench checker mirrors exact-checksum diagnostics in self-test cases" {
    const checker = try readChecker();
    defer std.testing.allocator.free(checker);

    const self_test_start = try indexOfRequired(checker, "def run_self_test() -> None:");
    const self_test = checker[self_test_start..];

    try expectContains(self_test, "missing_find_bit_exact_expectations");
    try expectContains(self_test, "expectations_missing_find_bit_exact_checksums");
    try expectContains(self_test, "missing_exact_expectations");
    try expectContains(self_test, "expectations_missing_exact_checksums");
    try expectContains(self_test, "unexpected_exact_expectations");
    try expectContains(self_test, "expectations_unexpected_exact_checksums");
    try expectContains(self_test, "duplicate_root_expectations");
    try expectContains(self_test, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=");

    try expectBefore(self_test, "expectations_missing_find_bit_exact_checksums", "expectations_missing_exact_checksums");
    try expectBefore(self_test, "expectations_missing_exact_checksums", "expectations_unexpected_exact_checksums");
}
