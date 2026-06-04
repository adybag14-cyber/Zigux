const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase1 closure keeps the find_bit bench guard marker tied to the current packet" {
    const closure = try readRepoFile("Documentation/zigux/phase1-closure.md", 160 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000");
    try expectContains(closure, "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM");
    try expectContains(closure, "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM");
    try expectContains(closure, "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py");
    try expectContains(closure, "PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py");
    try expectContains(closure, "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(closure, "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try expectNotContains(closure, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
}

test "phase1 bench checker keeps find_bit iterations checksums and source markers exact" {
    const checker = try readRepoFile("scripts/zigux/check-phase1-bench.py", 128 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS");
    try expectContains(checker, "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS");
    try expectContains(checker, "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM");
    try expectContains(checker, "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM");
    try expectContains(checker, "FIND_BIT_REQUIRED_EXACT_CHECKSUMS");
    try expectContains(checker, "FIND_BIT_REQUIRED_SOURCE_MARKERS");
    try expectContains(checker, "fn findBitBench() struct { checksum: u64 } {");
    try expectContains(checker, "fn findBitEdgeBench() struct { checksum: u64 } {");
    try expectContains(checker, "find_bit.findNextBit");
    try expectContains(checker, "find_bit.findNextAndBit");
    try expectContains(checker, "find_bit.findNextZeroBit");
    try expectContains(checker, "find_bit.findFirstBit");
    try expectContains(checker, "find_bit.findFirstAndBit");
    try expectContains(checker, "find_bit.findLastBit");
}

test "phase1 workflow and manifest keep the find_bit bench closure path review visible" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 128 * 1024);
    defer std.testing.allocator.free(workflow);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(workflow, "python3 scripts/zigux/check-phase1-bench.py");
    try expectContains(workflow, "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py");
    try expectContains(workflow, "python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(workflow, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");

    try expectContains(manifest, "tools/lib/find_bit.zig");
    try expectContains(manifest, "find_bit");
    try expectContains(manifest, "next_safe_step_note");
    try expectContains(manifest, "findLastBit");
    try expectContains(manifest, "clump8");
}

test "phase1 bench source still prints the find_bit steady and edge packets" {
    const bench = try readRepoFile("zigux/tests/phase1_bench.zig", 160 * 1024);
    defer std.testing.allocator.free(bench);

    try expectContains(bench, "fn findBitBench() struct { checksum: u64 } {");
    try expectContains(bench, "fn findBitEdgeBench() struct { checksum: u64 } {");
    try expectContains(bench, "const find_bit_result = findBitBench();");
    try expectContains(bench, "const find_bit_edge_result = findBitEdgeBench();");
    try expectContains(bench, "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}");
    try expectContains(bench, "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}");
    try expectContains(bench, "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}");
    try expectContains(bench, "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}");
    try expectContains(bench, "find_bit.findNextBit");
    try expectContains(bench, "find_bit.findNextAndBit");
    try expectContains(bench, "find_bit.findNextZeroBit");
    try expectContains(bench, "find_bit.findFirstBit");
    try expectContains(bench, "find_bit.findFirstAndBit");
    try expectContains(bench, "find_bit.findLastBit");
}
