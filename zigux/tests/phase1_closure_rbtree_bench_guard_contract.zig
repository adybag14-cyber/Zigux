const std = @import("std");

const closure_path = "Documentation/zigux/phase1-closure.md";
const bench_checker_path = "scripts/zigux/check-phase1-bench.py";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const smoke_path = "zigux/tests/phase1_host_tools_smoke.zig";

const rbtree_bench_guard_marker =
    \\PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns
;

const rbtree_bench_checksum_markers = [_][]const u8{
    "PHASE1_BENCH_RBTREE_ITERATIONS",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

const rbtree_bench_source_markers = [_][]const u8{
    "fn rbtreeBench() struct { checksum: u64 } {",
    "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
    "fn rbtreeFindAddBench() struct { checksum: u64 } {",
    "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
    "fn rbtreeCachedBench() struct { checksum: u64 } {",
};

const workflow_markers = [_][]const u8{
    "Self-test current Phase 1 bench checker",
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
    "Check current Phase 1 bench packet",
    "python3 scripts/zigux/check-phase1-bench.py",
    "Self-test current Phase 1 closure validator",
    "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "Check current Phase 1 closure packet",
    "python3 scripts/zigux/validate-phase1-closure.py",
};

const manifest_markers = [_][]const u8{
    "\"tools/lib/rbtree.zig\"",
    "\"cached_root_transition_shared_replay_summary\"",
    "the committed Phase 1 fixture and the shared host-tools smoke route also keep the exact `cached_root_transition_serials` cached-root erase, replacement, and detach sequence aligned on current master",
    "\"shared_replay_summary\"",
    "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree",
    "\"cached_root_transition_fixture_keys\"",
    "\"cached_root_transition_serials\"",
};

const smoke_markers = [_][]const u8{
    "cached_root_transition_serials",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var offset: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[offset..], needle) orelse return error.MarkerOutOfOrder;
        offset += found + needle.len;
    }
}

test "closure note keeps rbtree bench guard tied to the current closure packet" {
    const allocator = std.testing.allocator;
    const closure = try readFile(allocator, closure_path);
    defer allocator.free(closure);

    try expectContains(closure, rbtree_bench_guard_marker);
    try expectContains(closure, "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(closure, "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try expectContains(closure, "PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py");
    try expectContains(closure, "cached_root_transition_serials");
}

test "bench checker still owns the rbtree exactness family" {
    const allocator = std.testing.allocator;
    const bench_checker = try readFile(allocator, bench_checker_path);
    defer allocator.free(bench_checker);

    try expectAll(bench_checker, &rbtree_bench_checksum_markers);
    try expectAll(bench_checker, &rbtree_bench_source_markers);
    try expectContains(bench_checker, "\"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000");
    try expectContains(bench_checker, "RBTREE_REQUIRED_EXACT_CHECKSUMS");
}

test "workflow runs the bench packet before closure validation" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectAll(workflow, &workflow_markers);
    try expectOrdered(workflow, &.{
        "Self-test current Phase 1 bench checker",
        "Check current Phase 1 bench packet",
        "Self-test current Phase 1 closure validator",
        "Check current Phase 1 closure packet",
        "Run current Phase 1 shared tests-root smoke",
    });
}

test "manifest and shared smoke keep cached-root replay evidence visible" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, manifest_path);
    defer allocator.free(manifest);
    const smoke = try readFile(allocator, smoke_path);
    defer allocator.free(smoke);

    try expectAll(manifest, &manifest_markers);
    try expectAll(smoke, &smoke_markers);
}
