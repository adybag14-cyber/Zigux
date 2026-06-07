const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-bench.py";
const bench_path = "zigux/tests/phase1_bench.zig";

const find_bit_checker_markers = [_][]const u8{
    "\"find_bit_bench_fn\": \"fn findBitBench() struct { checksum: u64 } {\"",
    "\"find_bit_edge_fn\": \"fn findBitEdgeBench() struct { checksum: u64 } {\"",
    "\"find_edge_checksum_print\": 'try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\\\n\", .{find_bit_edge_result.checksum});'",
    "\"boundary_next_bit\": \"checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));\"",
    "\"tail_last_bit\": \"checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));\"",
};

const rbtree_checker_markers = [_][]const u8{
    "\"rbtree_postorder_safe_fn\": \"fn rbtreePostorderSafeBench() struct { checksum: u64 } {\"",
    "\"rbtree_find_add_fn\": \"fn rbtreeFindAddBench() struct { checksum: u64 } {\"",
    "\"rbtree_duplicate_fn\": \"fn rbtreeDuplicateBench() struct { checksum: u64 } {\"",
    "\"rbtree_cached_fn\": \"fn rbtreeCachedBench() struct { checksum: u64 } {\"",
    "\"rbtree_cached_print\": 'try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\\\n\", .{rbtree_cached_result.checksum});'",
    "\"rbtree_cached_leftmost\": \"const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);\"",
};

const bench_source_markers = [_][]const u8{
    "fn findBitBench() struct { checksum: u64 } {",
    "fn findBitEdgeBench() struct { checksum: u64 } {",
    "checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
    "checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));",
    "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
    "fn rbtreeFindAddBench() struct { checksum: u64 } {",
    "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
    "fn rbtreeCachedBench() struct { checksum: u64 } {",
    "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n\", .{rbtree_cached_result.checksum});",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "checker keeps source marker validation wired to find-bit and rbtree packets" {
    const checker = try readFile(checker_path, 256 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "SOURCE_MARKER_SETS = (");
    try expectContains(checker, "FIND_BIT_REQUIRED_SOURCE_MARKERS,");
    try expectContains(checker, "RBTREE_REQUIRED_SOURCE_MARKERS,");
    try expectOrdered(checker, "FIND_BIT_REQUIRED_SOURCE_MARKERS", "RBTREE_REQUIRED_SOURCE_MARKERS");
    try expectContains(checker, "def validate_bench_source(text: str) -> tuple[str, object]:");
    try expectContains(checker, "for marker_set in SOURCE_MARKER_SETS:");
    try expectContains(checker, "return (\"bench_source_missing_markers\", missing)");
    try expectContains(checker, "return (\"bench_source_duplicate_rbtree_markers\", duplicate_rbtree_markers)");
    try expectContains(checker, "return (\"missing_bench_source_file\", path)");

    inline for (find_bit_checker_markers) |marker| {
        try expectContains(checker, marker);
    }
    inline for (rbtree_checker_markers) |marker| {
        try expectContains(checker, marker);
    }
}

test "bench source still carries the checker-owned source marker packet" {
    const bench = try readFile(bench_path, 256 * 1024);
    defer std.testing.allocator.free(bench);

    inline for (bench_source_markers) |marker| {
        try expectContains(bench, marker);
    }

    try expectOrdered(
        bench,
        "const find_bit_result = findBitBench();",
        "const find_bit_edge_result = findBitEdgeBench();",
    );
    try expectOrdered(
        bench,
        "const rbtree_result = rbtreeBench();",
        "const rbtree_cached_result = rbtreeCachedBench();",
    );
}

test "checker self-test covers missing and duplicate source marker failures" {
    const checker = try readFile(checker_path, 256 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "build_full_bench_source(omit_find_bit_label=\"find_edge_checksum_print\")");
    try expectContains(checker, "build_full_bench_source(omit_rbtree_label=\"rbtree_cached_print\")");
    try expectContains(checker, "RBTREE_REQUIRED_SOURCE_MARKERS[\"rbtree_cached_print\"]");
    try expectContains(checker, "payload == [\"find_edge_checksum_print\"]");
    try expectContains(checker, "payload == [\"rbtree_cached_print\"]");
}
