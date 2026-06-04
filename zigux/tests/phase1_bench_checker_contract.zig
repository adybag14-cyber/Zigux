const std = @import("std");
const options = @import("phase1_bench_checker_contract_options");

const checker_text = options.checker_text;
const expectations_text = @embedFile("fixtures/phase1_bench_expectations.json");
const bench_text = @embedFile("phase1_bench.zig");

const IterationGate = struct {
    key: []const u8,
    value: []const u8,
};

const iteration_gates = [_]IterationGate{
    .{ .key = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_STRING_ITERATIONS", .value = "40000" },
    .{ .key = "PHASE1_BENCH_HWEIGHT_ITERATIONS", .value = "100000" },
    .{ .key = "PHASE1_BENCH_LIST_SORT_ITERATIONS", .value = "1000" },
    .{ .key = "PHASE1_BENCH_RBTREE_ITERATIONS", .value = "4000" },
};

const checksum_gates = [_][]const u8{
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactOccurrences(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    try std.testing.expectEqual(expected_count, count);
}

test "bench checker pins the live Phase 1 gate inputs" {
    try expectContains(checker_text, "EXPECTATIONS_REL = Path(\"zigux/tests/fixtures/phase1_bench_expectations.json\")");
    try expectContains(checker_text, "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")");
    try expectContains(checker_text, "EXPECTED_ITERATIONS = {");
    try expectContains(checker_text, "EXPECTED_CHECKSUMS = [");
    try expectContains(checker_text, "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)");
    try expectContains(checker_text, "RBTREE_REQUIRED_ITERATIONS = {\"PHASE1_BENCH_RBTREE_ITERATIONS\"}");
    try expectContains(checker_text, "SOURCE_MARKER_SETS = (");
    try expectContains(checker_text, "FIND_BIT_REQUIRED_SOURCE_MARKERS,");
    try expectContains(checker_text, "RBTREE_REQUIRED_SOURCE_MARKERS,");

    for (iteration_gates) |gate| {
        try expectContains(checker_text, gate.key);
    }
    for (checksum_gates) |key| {
        try expectContains(checker_text, key);
    }
}

test "bench expectations fixture keeps exact Phase 1 iterations and checksums" {
    try expectContains(expectations_text, "\"status\": \"pass\"");
    try expectContains(expectations_text, "\"iterations\": {");
    try expectContains(expectations_text, "\"checksums\": [");
    try expectContains(expectations_text, "\"exact_checksums\": {");

    for (iteration_gates) |gate| {
        try expectContains(expectations_text, gate.key);
        try expectContains(expectations_text, gate.value);
    }
    for (checksum_gates) |key| {
        try expectExactOccurrences(expectations_text, key, 2);
    }
}

test "bench source still emits the checked runtime fields" {
    try expectContains(bench_text, "const iterations_bitmap_weight: u64 = 20000;");
    try expectContains(bench_text, "const iterations_bitmap_window: u64 = 20000;");
    try expectContains(bench_text, "const iterations_find_bit: u64 = 20000;");
    try expectContains(bench_text, "const iterations_find_bit_edge: u64 = 20000;");
    try expectContains(bench_text, "const iterations_string: u64 = 40000;");
    try expectContains(bench_text, "const iterations_hweight: u64 = 100000;");
    try expectContains(bench_text, "const iterations_list_sort: u64 = 1000;");
    try expectContains(bench_text, "const iterations_rbtree: u64 = 4000;");

    for (checksum_gates) |key| {
        try expectContains(bench_text, key);
    }
}

test "find_bit and rbtree bench packets stay source-marker visible" {
    const source_markers = [_][]const u8{
        "fn findBitBench() struct { checksum: u64 } {",
        "fn findBitEdgeBench() struct { checksum: u64 } {",
        "const find_bit_result = findBitBench();",
        "const find_bit_edge_result = findBitEdgeBench();",
        "fn rbtreeBench() struct { checksum: u64 } {",
        "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
        "fn rbtreeFindAddBench() struct { checksum: u64 } {",
        "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
        "fn rbtreeCachedBench() struct { checksum: u64 } {",
        "const rbtree_result = rbtreeBench();",
        "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
        "const rbtree_find_add_result = rbtreeFindAddBench();",
        "const rbtree_duplicate_result = rbtreeDuplicateBench();",
        "const rbtree_cached_result = rbtreeCachedBench();",
    };

    for (source_markers) |marker| {
        try expectContains(checker_text, marker);
        try expectContains(bench_text, marker);
    }
}
