const std = @import("std");

const bench_source = @embedFile("phase1_bench.zig");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, bench_source, needle) != null);
}

fn expectOrdered(needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const offset = std.mem.indexOf(u8, bench_source[cursor..], needle) orelse return error.BenchSourceMarkerOutOfOrder;
        cursor += offset + needle.len;
    }
}

test "phase1 bench source keeps iteration budget constants" {
    const markers = [_][]const u8{
        "const iterations_bitmap_weight: u64 = 20000;",
        "const iterations_bitmap_window: u64 = 20000;",
        "const iterations_find_bit: u64 = 20000;",
        "const iterations_find_bit_edge: u64 = 20000;",
        "const iterations_string: u64 = 40000;",
        "const iterations_hweight: u64 = 100000;",
        "const iterations_list_sort: u64 = 1000;",
        "const iterations_rbtree: u64 = 4000;",
    };

    for (markers) |marker| {
        try expectContains(marker);
    }
}

test "phase1 bench source keeps helper-specific topology anchors" {
    const markers = [_][]const u8{
        "fn bitmapWeightBench() struct { checksum: u64 } {",
        "fn bitmapWindowBench() struct { checksum: u64 } {",
        "checksum +%= @intCast(bitmap.weightedOr(&dst, &lhs, &rhs, nbits));",
        "checksum +%= @intCast(bitmap.weightedXor(&dst, &lhs, &rhs, nbits));",
        "fn findBitBench() struct { checksum: u64 } {",
        "checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
        "fn findBitEdgeBench() struct { checksum: u64 } {",
        "checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));",
        "fn stringBench() !struct { checksum: u64 } {",
        "const enabled = try string.strtobool(if (even) \"on\" else \"0\");",
        "const parsed = string.memparse(if (even) \"64K rest\" else \"-17 tail\");",
        "fn hweightBench() struct { checksum: u64 } {",
        "checksum +%= @intCast(hweight.hweightLong(0xf0f0));",
        "fn listSortBench() struct { checksum: u64 } {",
        "list_sort.listSort(null, &head, ListEntry.cmp);",
        "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
        "var node = rbtree.firstPostorder(&root);",
        "fn rbtreeFindAddBench() struct { checksum: u64 } {",
        "const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp);",
        "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
        "var iter = rbtree.matchIterator(&duplicate_key, &root, TreeEntry.keyCmp);",
        "fn rbtreeCachedBench() struct { checksum: u64 } {",
        "var cached_root = rbtree.RootCached.init();",
        "_ = rbtree.addCached(&entry.node, &cached_root, TreeEntry.less);",
        "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
    };

    for (markers) |marker| {
        try expectContains(marker);
    }
}

test "phase1 bench main keeps call order before output packet labels" {
    try expectOrdered(&[_][]const u8{
        "const bitmap_weight_result = bitmapWeightBench();",
        "const bitmap_window_result = bitmapWindowBench();",
        "const find_bit_result = findBitBench();",
        "const find_bit_edge_result = findBitEdgeBench();",
        "const string_result = try stringBench();",
        "const hweight_result = hweightBench();",
        "const list_sort_result = listSortBench();",
        "const rbtree_result = rbtreeBench();",
        "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
        "const rbtree_find_add_result = rbtreeFindAddBench();",
        "const rbtree_duplicate_result = rbtreeDuplicateBench();",
        "const rbtree_cached_result = rbtreeCachedBench();",
        "PHASE1_BENCH=pass",
        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}",
        "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}",
        "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}",
        "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}",
        "PHASE1_BENCH_STRING_ITERATIONS={d}",
        "PHASE1_BENCH_HWEIGHT_ITERATIONS={d}",
        "PHASE1_BENCH_LIST_SORT_ITERATIONS={d}",
        "PHASE1_BENCH_RBTREE_ITERATIONS={d}",
        "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}",
        "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={d}",
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}",
        "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}",
        "PHASE1_BENCH_STRING_CHECKSUM={d}",
        "PHASE1_BENCH_HWEIGHT_CHECKSUM={d}",
        "PHASE1_BENCH_LIST_SORT_CHECKSUM={d}",
        "PHASE1_BENCH_RBTREE_CHECKSUM={d}",
        "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}",
        "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}",
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}",
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}",
    });
}
