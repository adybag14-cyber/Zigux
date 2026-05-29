const std = @import("std");
const testing = std.testing;

fn readCheckerSource() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        "scripts/zigux/check-phase1-bench.py",
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(checker_source: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

test "phase1 bench checker keeps self-test cli and success packet" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "--self-test");
    try expectContains(checker_source, "Run checker self-test cases without invoking Zig.");
    try expectContains(checker_source, "if args.self_test:");
    try expectContains(checker_source, "run_self_test()");
    try expectContains(checker_source, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try expectContains(checker_source, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=");
}

test "phase1 bench checker self-test covers local root and source drift" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "validate_bench_source");
    try expectContains(checker_source, "missing_bitmap_source_markers");
    try expectContains(checker_source, "missing_find_bit_source_markers");
    try expectContains(checker_source, "missing_string_source_markers");
    try expectContains(checker_source, "missing_rbtree_source_markers");
    try expectContains(checker_source, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM");
}

test "phase1 bench checker preserves fail-closed expectation diagnostics" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "EXPECTATIONS_JSON_ERROR={exc.msg}");
    try expectContains(checker_source, "EXPECTATIONS_JSON_LINE={exc.lineno}");
    try expectContains(checker_source, "EXPECTATIONS_JSON_COLUMN={exc.colno}");
    try expectContains(checker_source, "expectations_duplicate_keys");
    try expectContains(checker_source, "expectations_duplicate_checksums");
    try expectContains(checker_source, "expectations_missing_exact_checksums");
    try expectContains(checker_source, "missing_exact_checksums");
}
