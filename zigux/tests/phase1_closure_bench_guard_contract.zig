const std = @import("std");
const data = @import("phase1_closure_bench_guard_data");

const MissingMarker = error{MissingMarker};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) return MissingMarker.MissingMarker;
}

test "closure note and validator agree on the bench guard markers" {
    const find_bit_guard = "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`";
    const rbtree_guard = "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`";
    const find_bit_anchor_guard = "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`";

    try expectContains(data.closure_note, find_bit_guard);
    try expectContains(data.closure_note, rbtree_guard);
    try expectContains(data.closure_note, find_bit_anchor_guard);

    try expectContains(data.closure_validator, "\"find_bit_bench_guard\":");
    try expectContains(data.closure_validator, find_bit_guard);
    try expectContains(data.closure_validator, "\"rbtree_bench_guard\":");
    try expectContains(data.closure_validator, rbtree_guard);
    try expectContains(data.closure_validator, "\"find_bit_bench_anchor_guard\":");
    try expectContains(data.closure_validator, find_bit_anchor_guard);
}

test "bench checker keeps the find_bit runtime packet explicit" {
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\"");
    try expectContains(data.bench_checker, "FIND_BIT_REQUIRED_EXACT_CHECKSUMS");
    try expectContains(data.bench_checker, "fn findBitBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "fn findBitEdgeBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "const find_bit_result = findBitBench();");
    try expectContains(data.bench_checker, "const find_bit_edge_result = findBitEdgeBench();");
    try expectContains(data.bench_checker, "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}");
    try expectContains(data.bench_checker, "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}");
}

test "bench checker keeps the rbtree runtime packet explicit" {
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_RBTREE_CHECKSUM\"");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\"");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM\"");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\"");
    try expectContains(data.bench_checker, "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"");
    try expectContains(data.bench_checker, "RBTREE_REQUIRED_ITERATIONS");
    try expectContains(data.bench_checker, "RBTREE_REQUIRED_EXACT_CHECKSUMS");
    try expectContains(data.bench_checker, "fn rbtreeBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "fn rbtreePostorderSafeBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "fn rbtreeFindAddBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "fn rbtreeDuplicateBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "fn rbtreeCachedBench() struct { checksum: u64 } {");
    try expectContains(data.bench_checker, "PHASE1_BENCH_RBTREE_ITERATIONS={d}");
    try expectContains(data.bench_checker, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}");
}
