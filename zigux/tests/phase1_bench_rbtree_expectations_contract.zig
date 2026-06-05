const std = @import("std");

const max_file_bytes = 256 * 1024;

const root_files = .{
    .bench_source = "zigux/tests/phase1_bench.zig",
    .expectations = "zigux/tests/fixtures/phase1_bench_expectations.json",
    .checker = "scripts/zigux/check-phase1-bench.py",
};

const rbtree_iteration_key = "PHASE1_BENCH_RBTREE_ITERATIONS";
const rbtree_iteration_value = "4000";

const rbtree_checksum_keys = [_][]const u8{
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

const rbtree_exact_expectations = [_][]const u8{
    "\"PHASE1_BENCH_RBTREE_CHECKSUM\": 24000",
    "\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\": 24000",
    "\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM\": 8000",
    "\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\": 24000",
    "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\": 4000",
};

const source_markers = [_][]const u8{
    "const iterations_rbtree: u64 = 4000;",
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
    "rbtree.matchIterator(&duplicate_key, &root, TreeEntry.keyCmp)",
    "rbtree.eraseCached(&entries[1].node, &cached_root)",
};

const source_print_markers = [_][]const u8{
    "PHASE1_BENCH_RBTREE_ITERATIONS={d}",
    "PHASE1_BENCH_RBTREE_CHECKSUM={d}",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}",
};

const checker_markers = [_][]const u8{
    "RBTREE_REQUIRED_ITERATIONS = {\"PHASE1_BENCH_RBTREE_ITERATIONS\"}",
    "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
    "\"expectations_checksums_rbtree_exact_required\", RBTREE_REQUIRED_EXACT_CHECKSUMS",
    "return (\"expectations_missing_rbtree_iterations\", missing_rbtree_iterations)",
    "return (\"expectations_rbtree_iteration_value\", (key, expected, value))",
    "return (\"missing_rbtree_iterations\", [key])",
    "(\"missing_rbtree_exact_checksums\", RBTREE_REQUIRED_EXACT_CHECKSUMS)",
    "return (\"rbtree_iteration_mismatch\", (key, expected, actual))",
    "bench_source_duplicate_rbtree_markers",
};

fn readRootFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_file_bytes));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse {
        try std.testing.expect(false);
        return;
    };
    try std.testing.expect(std.mem.indexOfPos(u8, haystack, first + needle.len, needle) == null);
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, marker) orelse {
            try std.testing.expect(false);
            return;
        };
        cursor = found + marker.len;
    }
}

fn requireSourcePacket(source: []const u8) !void {
    for (source_markers) |marker| {
        try requireExactlyOnce(source, marker);
    }
    for (source_print_markers) |marker| {
        try requireContains(source, marker);
    }
    try requireOrdered(source, &.{
        "const rbtree_result = rbtreeBench();",
        "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
        "const rbtree_find_add_result = rbtreeFindAddBench();",
        "const rbtree_duplicate_result = rbtreeDuplicateBench();",
        "const rbtree_cached_result = rbtreeCachedBench();",
    });
}

fn requireExpectationsPacket(expectations: []const u8) !void {
    try requireContains(expectations, "\"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000");
    try requireOrdered(expectations, &rbtree_checksum_keys);
    for (rbtree_exact_expectations) |marker| {
        try requireContains(expectations, marker);
    }
}

fn requireCheckerPacket(checker: []const u8) !void {
    for (checker_markers) |marker| {
        try requireContains(checker, marker);
    }
    for (rbtree_checksum_keys) |key| {
        try requireContains(checker, key);
    }
    try requireOrdered(checker, &.{
        "(\"missing_rbtree_exact_checksums\", RBTREE_REQUIRED_EXACT_CHECKSUMS)",
        "(\"missing_bitmap_exact_checksums\", BITMAP_REQUIRED_EXACT_CHECKSUMS)",
        "(\"missing_find_bit_exact_checksums\", FIND_BIT_REQUIRED_EXACT_CHECKSUMS)",
    });
}

test "phase1 bench rbtree expectations packet is present in live root" {
    const allocator = std.testing.allocator;

    const source = try readRootFile(allocator, root_files.bench_source);
    defer allocator.free(source);
    const expectations = try readRootFile(allocator, root_files.expectations);
    defer allocator.free(expectations);
    const checker = try readRootFile(allocator, root_files.checker);
    defer allocator.free(checker);

    try requireSourcePacket(source);
    try requireExpectationsPacket(expectations);
    try requireCheckerPacket(checker);
}

test "contract catches missing rbtree source and expectation markers" {
    try std.testing.expectError(error.TestUnexpectedResult, requireSourcePacket(
        "const iterations_rbtree: u64 = 4000;\n" ++
            "fn rbtreeBench() struct { checksum: u64 } {\n" ++
            "fn rbtreePostorderSafeBench() struct { checksum: u64 } {\n",
    ));

    try std.testing.expectError(error.TestUnexpectedResult, requireExpectationsPacket(
        "\"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000\n" ++
            "\"PHASE1_BENCH_RBTREE_CHECKSUM\"\n" ++
            "\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\"\n",
    ));
}

test "contract catches missing checker rbtree failure buckets" {
    var checker = std.ArrayList(u8).empty;
    defer checker.deinit(std.testing.allocator);
    try checker.appendSlice(
        std.testing.allocator,
        "RBTREE_REQUIRED_ITERATIONS = {\"PHASE1_BENCH_RBTREE_ITERATIONS\"}\n",
    );
    try checker.appendSlice(std.testing.allocator, "RBTREE_REQUIRED_EXACT_CHECKSUMS = {\n");
    try checker.appendSlice(
        std.testing.allocator,
        "\"expectations_checksums_rbtree_exact_required\", RBTREE_REQUIRED_EXACT_CHECKSUMS\n",
    );

    try std.testing.expectError(error.TestUnexpectedResult, requireCheckerPacket(checker.items));
}

test "rbtree checksum roster stays stable" {
    try std.testing.expectEqual(@as(usize, 5), rbtree_checksum_keys.len);
    try std.testing.expectEqualStrings("PHASE1_BENCH_RBTREE_ITERATIONS", rbtree_iteration_key);
    try std.testing.expectEqualStrings("4000", rbtree_iteration_value);
}
