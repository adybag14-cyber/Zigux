const std = @import("std");

const closure_path = "Documentation/zigux/phase1-closure.md";
const bench_checker_path = "scripts/zigux/check-phase1-bench.py";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";
const bench_source_path = "zigux/tests/phase1_bench.zig";

const iteration_markers = [_]struct {
    key: []const u8,
    value: []const u8,
    const_name: []const u8,
}{
    .{ .key = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS", .value = "20000", .const_name = "iterations_bitmap_weight" },
    .{ .key = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS", .value = "20000", .const_name = "iterations_bitmap_window" },
    .{ .key = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS", .value = "20000", .const_name = "iterations_find_bit" },
    .{ .key = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS", .value = "20000", .const_name = "iterations_find_bit_edge" },
    .{ .key = "PHASE1_BENCH_STRING_ITERATIONS", .value = "40000", .const_name = "iterations_string" },
    .{ .key = "PHASE1_BENCH_HWEIGHT_ITERATIONS", .value = "100000", .const_name = "iterations_hweight" },
    .{ .key = "PHASE1_BENCH_LIST_SORT_ITERATIONS", .value = "1000", .const_name = "iterations_list_sort" },
    .{ .key = "PHASE1_BENCH_RBTREE_ITERATIONS", .value = "4000", .const_name = "iterations_rbtree" },
};

const checksum_keys = [_][]const u8{
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

const exact_checksum_pairs = [_]struct {
    key: []const u8,
    value: []const u8,
}{
    .{ .key = "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", .value = "100000" },
    .{ .key = "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", .value = "120000" },
    .{ .key = "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", .value = "3780000" },
    .{ .key = "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", .value = "4020000" },
    .{ .key = "PHASE1_BENCH_STRING_CHECKSUM", .value = "320000" },
    .{ .key = "PHASE1_BENCH_HWEIGHT_CHECKSUM", .value = "6800000" },
    .{ .key = "PHASE1_BENCH_LIST_SORT_CHECKSUM", .value = "10000" },
    .{ .key = "PHASE1_BENCH_RBTREE_CHECKSUM", .value = "24000" },
    .{ .key = "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM", .value = "24000" },
    .{ .key = "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM", .value = "8000" },
    .{ .key = "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", .value = "24000" },
    .{ .key = "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", .value = "4000" },
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOccursOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |idx| {
        count += 1;
        rest = rest[idx + needle.len ..];
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

test "closure note keeps bench checker and broader bench packet parked together" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, closure_path);
    defer allocator.free(closure);

    try requireContains(closure, "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`");
    try requireContains(closure, "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`");
    try requireContains(closure, "zigux/tests/phase1_bench.zig");
    try requireContains(closure, "zigux/tests/fixtures/phase1_bench_expectations.json");
    try requireContains(closure, "scripts/zigux/check-phase1-bench.py");
    try requireContains(closure, "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`");
}

test "bench checker owns the exact iteration and checksum roster" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, bench_checker_path);
    defer allocator.free(checker);

    try requireContains(checker, "EXPECTED_ITERATIONS = {");
    for (iteration_markers) |marker| {
        var expected_line_buf: [128]u8 = undefined;
        const expected_line = try std.fmt.bufPrint(&expected_line_buf, "\"{s}\": {s}", .{ marker.key, marker.value });
        try requireContains(checker, expected_line);
    }

    try requireContains(checker, "EXPECTED_CHECKSUMS = [");
    try requireContains(checker, "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)");
    for (checksum_keys) |key| {
        var expected_key_buf: [128]u8 = undefined;
        const expected_key = try std.fmt.bufPrint(&expected_key_buf, "\"{s}\"", .{key});
        try requireContains(checker, expected_key);
    }

    try requireContains(checker, "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {");
    try requireContains(checker, "RBTREE_REQUIRED_EXACT_CHECKSUMS = {");
    try requireContains(checker, "SOURCE_MARKER_SETS = (");
    try requireContains(checker, "FIND_BIT_REQUIRED_SOURCE_MARKERS,");
    try requireContains(checker, "RBTREE_REQUIRED_SOURCE_MARKERS,");
}

test "expectations fixture matches the checker roster and exact checksum packet" {
    const allocator = std.testing.allocator;
    const expectations = try readRepoFile(allocator, expectations_path);
    defer allocator.free(expectations);

    try requireContains(expectations, "\"status\": \"pass\"");
    for (iteration_markers) |marker| {
        var expected_pair_buf: [128]u8 = undefined;
        const expected_pair = try std.fmt.bufPrint(&expected_pair_buf, "\"{s}\": {s}", .{ marker.key, marker.value });
        try requireOccursOnce(expectations, expected_pair);
    }
    for (checksum_keys) |key| {
        var expected_key_buf: [128]u8 = undefined;
        const expected_key = try std.fmt.bufPrint(&expected_key_buf, "\"{s}\"", .{key});
        try requireContains(expectations, expected_key);
    }
    for (exact_checksum_pairs) |pair| {
        var expected_pair_buf: [128]u8 = undefined;
        const expected_pair = try std.fmt.bufPrint(&expected_pair_buf, "\"{s}\": {s}", .{ pair.key, pair.value });
        try requireOccursOnce(expectations, expected_pair);
    }
}

test "bench source prints the same runtime packet the checker validates" {
    const allocator = std.testing.allocator;
    const bench = try readRepoFile(allocator, bench_source_path);
    defer allocator.free(bench);

    try requireContains(bench, "pub fn main(init: std.process.Init) !void {");
    try requireContains(bench, "try stdout_writer.interface.print(\"PHASE1_BENCH=pass\\n\", .{});");
    try requireContains(bench, "fn findBitBench() struct { checksum: u64 } {");
    try requireContains(bench, "fn findBitEdgeBench() struct { checksum: u64 } {");
    try requireContains(bench, "fn rbtreeBench() struct { checksum: u64 } {");
    try requireContains(bench, "fn rbtreePostorderSafeBench() struct { checksum: u64 } {");
    try requireContains(bench, "fn rbtreeFindAddBench() struct { checksum: u64 } {");
    try requireContains(bench, "fn rbtreeDuplicateBench() struct { checksum: u64 } {");
    try requireContains(bench, "fn rbtreeCachedBench() struct { checksum: u64 } {");

    for (iteration_markers) |marker| {
        var const_line_buf: [128]u8 = undefined;
        const const_line = try std.fmt.bufPrint(&const_line_buf, "const {s}: u64 = {s};", .{ marker.const_name, marker.value });
        try requireContains(bench, const_line);

        var print_line_buf: [192]u8 = undefined;
        const print_line = try std.fmt.bufPrint(&print_line_buf, "try stdout_writer.interface.print(\"{s}={{d}}\\n\"", .{marker.key});
        try requireContains(bench, print_line);
    }

    for (checksum_keys) |key| {
        var print_line_buf: [192]u8 = undefined;
        const print_line = try std.fmt.bufPrint(&print_line_buf, "try stdout_writer.interface.print(\"{s}={{d}}\\n\"", .{key});
        try requireContains(bench, print_line);
    }
}
