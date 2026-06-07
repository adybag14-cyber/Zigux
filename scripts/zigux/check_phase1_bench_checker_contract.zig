const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-bench.py";

const expected_iterations = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const expected_checksums = [_][]const u8{
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

const find_bit_source_markers = [_][]const u8{
    "FIND_BIT_REQUIRED_SOURCE_MARKERS",
    "\"find_bit_bench_fn\"",
    "\"find_bit_edge_fn\"",
    "\"find_bit_bench_call\"",
    "\"find_bit_edge_call\"",
    "\"find_next_iterations_print\"",
    "\"find_next_checksum_print\"",
    "\"find_edge_iterations_print\"",
    "\"find_edge_checksum_print\"",
    "\"boundary_next_bit\"",
    "\"boundary_next_and_bit\"",
    "\"boundary_next_zero_bit\"",
    "\"tail_first_bit\"",
    "\"tail_first_and_bit\"",
    "\"tail_last_bit\"",
};

const rbtree_source_markers = [_][]const u8{
    "RBTREE_REQUIRED_SOURCE_MARKERS",
    "\"rbtree_bench_fn\"",
    "\"rbtree_postorder_safe_fn\"",
    "\"rbtree_find_add_fn\"",
    "\"rbtree_duplicate_fn\"",
    "\"rbtree_cached_fn\"",
    "\"rbtree_bench_call\"",
    "\"rbtree_postorder_safe_call\"",
    "\"rbtree_find_add_call\"",
    "\"rbtree_duplicate_call\"",
    "\"rbtree_cached_call\"",
    "\"rbtree_iterations_print\"",
    "\"rbtree_checksum_print\"",
    "\"rbtree_postorder_safe_print\"",
    "\"rbtree_find_add_print\"",
    "\"rbtree_duplicate_print\"",
    "\"rbtree_cached_print\"",
    "\"rbtree_postorder\"",
    "\"rbtree_find_add\"",
    "\"rbtree_duplicate_range\"",
    "\"rbtree_cached_leftmost\"",
};

fn readChecker() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase1 bench checker pins source marker rosters" {
    const checker = try readChecker();
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "SOURCE_MARKER_SETS = (");
    try expectContains(checker, "def duplicate_marker_labels(text: str, marker_set: dict[str, str]) -> list[str]:");
    try expectContains(checker, "def validate_bench_source(text: str) -> tuple[str, object]:");
    try expectContains(checker, "bench_source_missing_markers");
    try expectContains(checker, "bench_source_duplicate_rbtree_markers");

    inline for (find_bit_source_markers) |marker| {
        try expectContains(checker, marker);
    }
    inline for (rbtree_source_markers) |marker| {
        try expectContains(checker, marker);
    }
}

test "phase1 bench checker keeps expectation and output reason vocabulary" {
    const checker = try readChecker();
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_ITERATIONS = {");
    try expectContains(checker, "EXPECTED_CHECKSUMS = [");
    try expectContains(checker, "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)");
    try expectContains(checker, "exact_requirements = (");
    try expectContains(checker, "exact_categories = (");

    inline for (expected_iterations) |key| {
        try expectContains(checker, key);
    }
    inline for (expected_checksums) |key| {
        try expectContains(checker, key);
    }

    const reason_markers = [_][]const u8{
        "expectations_duplicate_keys",
        "expectations_missing_rbtree_iterations",
        "expectations_checksums_rbtree_exact_required",
        "missing_rbtree_iterations",
        "missing_rbtree_exact_checksums",
        "exact_checksum_mismatch",
        "unexpected",
        "duplicate",
    };
    inline for (reason_markers) |marker| {
        try expectContains(checker, marker);
    }
}

test "phase1 bench checker keeps self-test and runtime command envelope" {
    const checker = try readChecker();
    defer std.testing.allocator.free(checker);

    try expectBefore(checker, "parser.add_argument(\"--self-test\"", "if args.self_test:");
    try expectContains(checker, "run_self_test()");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}");

    try expectContains(checker, "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]");
    try expectContains(checker, "PHASE1_BENCH_CHECK=fail");
    try expectContains(checker, "PHASE1_BENCH_CHECK=pass");
    try expectContains(checker, "PHASE1_BENCH_EXPECTATIONS={expectations_file}");
    try expectContains(checker, "PHASE1_BENCH_SOURCE={phase1_bench}");
    try expectContains(checker, "PHASE1_BENCH_ZIG={zig}");
}
