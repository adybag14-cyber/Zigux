const std = @import("std");

const bench_iterations = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const bench_checksums = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

const exact_checksum_categories = [_][]const u8{
    "BITMAP_REQUIRED_EXACT_CHECKSUMS",
    "FIND_BIT_REQUIRED_EXACT_CHECKSUMS",
    "STRING_REQUIRED_EXACT_CHECKSUMS",
    "HWEIGHT_REQUIRED_EXACT_CHECKSUMS",
    "LIST_SORT_REQUIRED_EXACT_CHECKSUMS",
    "RBTREE_REQUIRED_EXACT_CHECKSUMS",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase1 bench expectations keep the checker schema in lockstep" {
    const checker = try readFile("scripts/zigux/check-phase1-bench.py", 256 * 1024);
    defer std.testing.allocator.free(checker);
    const expectations = try readFile("zigux/tests/fixtures/phase1_bench_expectations.json", 64 * 1024);
    defer std.testing.allocator.free(expectations);

    try expectContains(expectations, "\"status\": \"pass\"");
    try expectOrdered(expectations, "\"iterations\"", "\"checksums\"");
    try expectOrdered(expectations, "\"checksums\"", "\"exact_checksums\"");

    inline for (bench_iterations) |key| {
        try expectContains(checker, key);
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(expectations, key));
    }

    inline for (bench_checksums) |key| {
        try expectContains(checker, key);
        try std.testing.expectEqual(@as(usize, 2), countOccurrences(expectations, key));
    }

    inline for (exact_checksum_categories) |category| {
        try expectContains(checker, category);
    }
}

test "phase1 bench checker still fail-closes schema drift surfaces" {
    const checker = try readFile("scripts/zigux/check-phase1-bench.py", 256 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "expectations_duplicate_keys");
    try expectContains(checker, "expectations_duplicate_iteration_keys");
    try expectContains(checker, "expectations_duplicate_checksums");
    try expectContains(checker, "expectations_duplicate_exact_checksum_keys");
    try expectContains(checker, "expectations_missing_iterations");
    try expectContains(checker, "expectations_unexpected_iteration");
    try expectContains(checker, "expectations_checksum_order");
    try expectContains(checker, "expectations_missing_exact_checksums");
    try expectContains(checker, "expectations_unexpected_exact_checksums");
    try expectContains(checker, "expectations_exact_checksum_nonpositive");
}

test "phase1 bench checker self-test covers schema drift cases" {
    const checker = try readFile("scripts/zigux/check-phase1-bench.py", 256 * 1024);
    defer std.testing.allocator.free(checker);

    try expectOrdered(
        checker,
        "duplicate_top_level_text",
        "load_expectations_text(duplicate_top_level_text)",
    );
    try expectOrdered(
        checker,
        "load_expectations_text(duplicate_top_level_text)",
        "assert_case(kind == \"expectations_duplicate_keys\"",
    );
    try expectContains(checker, "payload == [\"status\"]");

    try expectOrdered(
        checker,
        "missing_rbtree_iteration_expectations = base_expectations()",
        "del missing_rbtree_iteration_expectations[\"iterations\"][\"PHASE1_BENCH_RBTREE_ITERATIONS\"]",
    );
    try expectOrdered(
        checker,
        "del missing_rbtree_iteration_expectations[\"iterations\"][\"PHASE1_BENCH_RBTREE_ITERATIONS\"]",
        "assert_case(kind == \"expectations_missing_rbtree_iterations\"",
    );
    try expectContains(checker, "payload == [\"PHASE1_BENCH_RBTREE_ITERATIONS\"]");

    try expectOrdered(
        checker,
        "missing_rbtree_exact_expectations = base_expectations()",
        "del missing_rbtree_exact_expectations[\"exact_checksums\"][\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"]",
    );
    try expectOrdered(
        checker,
        "del missing_rbtree_exact_expectations[\"exact_checksums\"][\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"]",
        "assert_case(kind == \"expectations_checksums_rbtree_exact_required\"",
    );
    try expectContains(checker, "payload == \"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"");
    try expectOrdered(
        checker,
        "print(\"PHASE1_BENCH_CHECK_SELF_TEST=pass\")",
        "print(f\"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}\")",
    );
}
