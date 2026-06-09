const std = @import("std");

const max_file_size = 512 * 1024;

const closure_path = "Documentation/zigux/phase1-closure.md";
const validator_path = "scripts/zigux/validate-phase1-closure.py";

const bench_guard_markers = [_][]const u8{
    "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "closure note keeps the bench guard markers exact and singular" {
    const closure = try readRepoFile(std.testing.allocator, closure_path);
    defer std.testing.allocator.free(closure);

    for (bench_guard_markers) |marker| {
        try expectCount(closure, marker, 1);
    }

    try expectContains(closure, "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`");
    try expectContains(closure, "when the broader expectations packet returns");
}

test "validator expected-marker table owns the same bench guard strings" {
    const validator = try readRepoFile(std.testing.allocator, validator_path);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "\"find_bit_bench_guard\":");
    try expectContains(validator, "\"rbtree_bench_guard\":");
    for (bench_guard_markers) |marker| {
        try expectContains(validator, marker);
    }
}

test "bench guard remains narrow and does not promote the broader bench packet into required files" {
    const validator = try readRepoFile(std.testing.allocator, validator_path);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")");
    try expectContains(validator, "BENCH_CHECKER_REL,");
    try expectContains(validator, "\"gap_packet\":");
    try expectNotContains(validator, "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")");
    try expectNotContains(validator, "PHASE1_BENCH_EXPECTATIONS_REL = Path(\"zigux/tests/fixtures/phase1_bench_expectations.json\")");
}

test "validator self-test still exercises missing and stale bench guard drift" {
    const validator = try readRepoFile(std.testing.allocator, validator_path);
    defer std.testing.allocator.free(validator);

    const expected_cases = [_][]const u8{
        "(\"missing_find_bit_bench_guard\"",
        "(\"missing_rbtree_bench_guard\"",
    };
    for (expected_cases) |case_name| {
        try expectContains(validator, case_name);
    }
}
