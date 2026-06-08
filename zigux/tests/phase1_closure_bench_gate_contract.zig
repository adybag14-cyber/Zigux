const std = @import("std");

const validate_phase1_closure_path = "scripts/zigux/validate-phase1-closure.py";
const check_phase1_bench_path = "scripts/zigux/check-phase1-bench.py";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";
const bench_source_path = "zigux/tests/phase1_bench.zig";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "closure validator keeps the bench gate in the required Phase 1 packet" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, validate_phase1_closure_path);
    defer allocator.free(validator);

    try expectContains(validator, "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")");
    try expectContains(validator, "BENCH_CHECKER_REL,");
    try expectContains(validator, "\"find_bit_bench_guard\":");
    try expectContains(validator, "\"rbtree_bench_guard\":");
    try expectContains(validator, "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000");
    try expectContains(validator, "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000");
    try expectContains(validator, "PHASE1_BENCH_RBTREE_ITERATIONS=4000");
    try expectContains(validator, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM");
}

test "bench checker preserves its public pass fail and self-test markers" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, check_phase1_bench_path);
    defer allocator.free(checker);

    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT");
    try expectContains(checker, "PHASE1_BENCH_CHECK=fail");
    try expectContains(checker, "PHASE1_BENCH_CHECK=pass");
    try expectContains(checker, "PHASE1_BENCH_CHECK_REASON");
    try expectContains(checker, "EXPECTATIONS_JSON_ERROR");
    try expectContains(checker, "BENCH_COMMAND_EXIT");
    try expectContains(checker, "PHASE1_BENCH_EXPECTATIONS=");
    try expectContains(checker, "PHASE1_BENCH_SOURCE=");
    try expectContains(checker, "PHASE1_BENCH_ZIG=");
}

test "bench checker validates expectations and source before invoking Zig" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, check_phase1_bench_path);
    defer allocator.free(checker);

    try expectContains(checker, "load_runtime_expectations(expectations_file)");
    try expectContains(checker, "load_runtime_bench_source(phase1_bench)");
    try expectContains(checker, "find_zig(root, args.zig)");
    try expectContains(checker, "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]");
    try expectBefore(checker, "load_runtime_expectations(expectations_file)", "load_runtime_bench_source(phase1_bench)");
    try expectBefore(checker, "load_runtime_bench_source(phase1_bench)", "find_zig(root, args.zig)");
    try expectBefore(checker, "find_zig(root, args.zig)", "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]");
}

test "bench checker remains tied to the canonical Phase 1 bench files" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, check_phase1_bench_path);
    defer allocator.free(checker);

    try expectContains(checker, expectations_path);
    try expectContains(checker, bench_source_path);
    try expectContains(checker, "EXPECTATIONS_REL = Path(\"zigux/tests/fixtures/phase1_bench_expectations.json\")");
    try expectContains(checker, "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")");
    try expectContains(checker, "expectations_path(root)");
    try expectContains(checker, "bench_source_path(root)");
}
