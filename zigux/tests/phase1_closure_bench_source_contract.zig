const std = @import("std");

const bench_source_path = "zigux/tests/phase1_bench.zig";
const bench_build_path = "zigux/tests/phase1_bench_build.zig";
const bench_checker_path = "scripts/zigux/check-phase1-bench.py";
const closure_note_path = "Documentation/zigux/phase1-closure.md";

const bench_iteration_markers = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const bench_checksum_markers = [_][]const u8{
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

const helper_module_markers = [_][]const u8{
    "../../tools/lib/find_bit.zig",
    "../../tools/lib/bitmap.zig",
    "../../tools/lib/string.zig",
    "../../tools/lib/cmdline.zig",
    "../../tools/lib/hweight.zig",
    "../../tools/lib/list_sort.zig",
    "../../tools/lib/rbtree.zig",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |pos| {
        count += 1;
        start = pos + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_pos = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_pos = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_pos < later_pos);
}

test "phase1 bench source emits the current closure output roster" {
    const bench_source = try readRepoFile(bench_source_path, 128 * 1024);
    defer std.testing.allocator.free(bench_source);

    try expectContains(bench_source, "const iterations_bitmap_weight: u64 = 20000;");
    try expectContains(bench_source, "const iterations_bitmap_window: u64 = 20000;");
    try expectContains(bench_source, "const iterations_find_bit: u64 = 20000;");
    try expectContains(bench_source, "const iterations_find_bit_edge: u64 = 20000;");
    try expectContains(bench_source, "const iterations_string: u64 = 40000;");
    try expectContains(bench_source, "const iterations_hweight: u64 = 100000;");
    try expectContains(bench_source, "const iterations_list_sort: u64 = 1000;");
    try expectContains(bench_source, "const iterations_rbtree: u64 = 4000;");

    try expectContains(bench_source, "fn bitmapWeightBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn bitmapWindowBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn findBitBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn findBitEdgeBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn stringBench() !struct { checksum: u64 } {");
    try expectContains(bench_source, "fn hweightBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn listSortBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn rbtreeBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn rbtreePostorderSafeBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn rbtreeFindAddBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn rbtreeDuplicateBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn rbtreeCachedBench() struct { checksum: u64 } {");

    try expectContains(bench_source, "PHASE1_BENCH=pass");
    for (bench_iteration_markers) |marker| {
        try expectContains(bench_source, marker);
    }
    for (bench_checksum_markers) |marker| {
        try expectContains(bench_source, marker);
    }
}

test "phase1 bench checker keeps source markers and exact checksums fail closed" {
    const checker = try readRepoFile(bench_checker_path, 160 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")");
    try expectContains(checker, "SOURCE_MARKER_SETS");
    try expectContains(checker, "validate_bench_source");
    try expectContains(checker, "load_runtime_bench_source");
    try expectContains(checker, "bench_source_missing_markers");
    try expectContains(checker, "bench_source_duplicate_rbtree_markers");
    try expectContains(checker, "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)");
    try expectContains(checker, "RBTREE_REQUIRED_EXACT_CHECKSUMS");
    try expectContains(checker, "FIND_BIT_REQUIRED_SOURCE_MARKERS");
    try expectContains(checker, "RBTREE_REQUIRED_SOURCE_MARKERS");

    for (bench_iteration_markers) |marker| {
        try expectContains(checker, marker);
    }
    for (bench_checksum_markers) |marker| {
        try expectContains(checker, marker);
    }

    try expectBefore(
        checker,
        "kind, payload = load_runtime_bench_source(phase1_bench)",
        "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]",
    );
}

test "phase1 bench build wrapper stays scoped to the focused bench executable" {
    const build_file = try readRepoFile(bench_build_path, 64 * 1024);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, ".root_source_file = b.path(\"phase1_bench.zig\")");
    try expectContains(build_file, ".name = \"phase1-bench\"");
    try expectContains(build_file, "const bench_step = b.step(");
    try expectContains(build_file, "\"bench\"");
    try expectContains(build_file, "const test_step = b.step(");
    try expectContains(build_file, "\"test\"");
    try expectContains(build_file, "b.default_step.dependOn(test_step);");

    for (helper_module_markers) |marker| {
        try expectContains(build_file, marker);
    }
    try expectContains(build_file, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(build_file, "string_module.addImport(\"cmdline\", cmdline_module);");
}

test "phase1 closure note parks bench source as a broader companion with explicit guards" {
    const closure_note = try readRepoFile(closure_note_path, 160 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "zigux/tests/phase1_bench.zig");
    try expectContains(closure_note, "PHASE1_CURRENT_GAP_PACKET");
    try expectContains(closure_note, "PHASE1_FIND_BIT_BENCH_GUARD");
    try expectContains(closure_note, "PHASE1_RBTREE_BENCH_GUARD");
    try expectContains(closure_note, "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000");
    try expectContains(closure_note, "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000");
    try expectContains(closure_note, "PHASE1_BENCH_RBTREE_ITERATIONS=4000");
    try expectContains(closure_note, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM");
    try expectContains(closure_note, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker");
}
