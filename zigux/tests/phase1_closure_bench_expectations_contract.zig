const std = @import("std");

const RequiredFile = struct {
    path: []const u8,
    markers: []const []const u8,
};

const closure_markers = [_][]const u8{
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
};

const checker_markers = [_][]const u8{
    "EXPECTATIONS_REL = Path(\"zigux/tests/fixtures/phase1_bench_expectations.json\")",
    "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")",
    "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000",
    "\"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000",
    "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"",
    "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
    "FIND_BIT_REQUIRED_SOURCE_MARKERS = {",
    "RBTREE_REQUIRED_SOURCE_MARKERS = {",
    "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
    "print(\"PHASE1_BENCH_CHECK=pass\")",
};

const expectations_markers = [_][]const u8{
    "\"status\": \"pass\"",
    "\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS\": 20000",
    "\"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS\": 20000",
    "\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000",
    "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000",
    "\"PHASE1_BENCH_STRING_ITERATIONS\": 40000",
    "\"PHASE1_BENCH_HWEIGHT_ITERATIONS\": 100000",
    "\"PHASE1_BENCH_LIST_SORT_ITERATIONS\": 1000",
    "\"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000",
    "\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\": 100000",
    "\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\": 120000",
    "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\": 3780000",
    "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\": 4020000",
    "\"PHASE1_BENCH_STRING_CHECKSUM\": 320000",
    "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\": 6800000",
    "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\": 10000",
    "\"PHASE1_BENCH_RBTREE_CHECKSUM\": 24000",
    "\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\": 24000",
    "\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM\": 8000",
    "\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\": 24000",
    "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\": 4000",
};

const bench_source_markers = [_][]const u8{
    "const iterations_find_bit: u64 = 20000;",
    "const iterations_find_bit_edge: u64 = 20000;",
    "const iterations_rbtree: u64 = 4000;",
    "fn findBitBench() struct { checksum: u64 } {",
    "fn findBitEdgeBench() struct { checksum: u64 } {",
    "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
    "fn rbtreeFindAddBench() struct { checksum: u64 } {",
    "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
    "fn rbtreeCachedBench() struct { checksum: u64 } {",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\\\n\", .{find_bit_edge_result.checksum});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\\\n\", .{rbtree_cached_result.checksum});",
};

const build_wrapper_markers = [_][]const u8{
    ".root_source_file = b.path(\"phase1_closure_bench_expectations_contract.zig\")",
    ".name = \"phase1-closure-bench-expectations-contract\"",
    "\"phase1-closure-bench-expectations-contract\"",
    "b.step(\"test\"",
};

const required_files = [_]RequiredFile{
    .{ .path = "Documentation/zigux/phase1-closure.md", .markers = &closure_markers },
    .{ .path = "scripts/zigux/check-phase1-bench.py", .markers = &checker_markers },
    .{ .path = "zigux/tests/fixtures/phase1_bench_expectations.json", .markers = &expectations_markers },
    .{ .path = "zigux/tests/phase1_bench.zig", .markers = &bench_source_markers },
    .{ .path = "zigux/tests/phase1_closure_bench_expectations_contract_build.zig", .markers = &build_wrapper_markers },
};

fn repoPath(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    return try allocator.dupe(u8, relative_path);
}

fn readRepoFile(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const path = try repoPath(allocator, relative_path);
    defer allocator.free(path);
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

test "phase1 closure bench expectations packet stays aligned" {
    const allocator = std.testing.allocator;
    for (required_files) |file| {
        const text = try readRepoFile(allocator, file.path);
        defer allocator.free(text);
        for (file.markers) |marker| {
            try expectMarker(text, marker);
        }
    }
}

test "bench expectations keep one complete checksum roster" {
    const allocator = std.testing.allocator;
    const text = try readRepoFile(allocator, "zigux/tests/fixtures/phase1_bench_expectations.json");
    defer allocator.free(text);

    const required_checksum_names = [_][]const u8{
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

    for (required_checksum_names) |name| {
        var occurrences: usize = 0;
        var rest = text;
        while (std.mem.indexOf(u8, rest, name)) |index| {
            occurrences += 1;
            rest = rest[index + name.len ..];
        }
        try std.testing.expectEqual(@as(usize, 2), occurrences);
    }
}
