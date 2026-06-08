const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-bench.py";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";

const IterationExpectation = struct {
    key: []const u8,
    value: []const u8,
};

const expected_iterations = [_]IterationExpectation{
    .{ .key = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS", .value = "20000" },
    .{ .key = "PHASE1_BENCH_STRING_ITERATIONS", .value = "40000" },
    .{ .key = "PHASE1_BENCH_HWEIGHT_ITERATIONS", .value = "100000" },
    .{ .key = "PHASE1_BENCH_LIST_SORT_ITERATIONS", .value = "1000" },
    .{ .key = "PHASE1_BENCH_RBTREE_ITERATIONS", .value = "4000" },
};

fn readOwned(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "checker pins the complete iteration expectation roster and special rbtree guard" {
    const allocator = std.testing.allocator;
    const checker = try readOwned(allocator, checker_path);
    defer allocator.free(checker);
    const fixture = try readOwned(allocator, expectations_path);
    defer allocator.free(fixture);

    try expectContains(checker, "EXPECTED_ITERATIONS = {");
    try expectContains(checker, "RBTREE_REQUIRED_ITERATIONS = {\"PHASE1_BENCH_RBTREE_ITERATIONS\"}");
    try expectBefore(checker, "RBTREE_REQUIRED_ITERATIONS", "def validate_expectations(expectations: object)");

    for (expected_iterations) |entry| {
        try expectContains(checker, entry.key);
        try expectContains(fixture, entry.key);
        try expectContains(fixture, entry.value);
    }

    try expectBefore(fixture, "\"iterations\": {", "\"checksums\": [");
}

test "expectation iteration diagnostics stay fail-closed and ordered" {
    const allocator = std.testing.allocator;
    const checker = try readOwned(allocator, checker_path);
    defer allocator.free(checker);

    try expectBefore(
        checker,
        "missing_rbtree_iterations = sorted(RBTREE_REQUIRED_ITERATIONS - iteration_keys)",
        "if iteration_keys != set(EXPECTED_ITERATIONS):",
    );
    try expectBefore(
        checker,
        "return (\"expectations_missing_rbtree_iterations\", missing_rbtree_iterations)",
        "return (\"expectations_missing_iterations\", missing)",
    );
    try expectBefore(
        checker,
        "return (\"expectations_unexpected_iteration\", unexpected[0])",
        "for key, expected in EXPECTED_ITERATIONS.items():",
    );
    try expectContains(checker, "return (\"expectations_iteration_value_type\", (key, type(value).__name__))");
    try expectBefore(
        checker,
        "return (\"expectations_rbtree_iteration_value\", (key, expected, value))",
        "return (\"expectations_iteration_value\", (key, expected, value))",
    );
}

test "runtime iteration diagnostics precede generic missing output handling" {
    const allocator = std.testing.allocator;
    const checker = try readOwned(allocator, checker_path);
    defer allocator.free(checker);

    try expectBefore(
        checker,
        "if key in RBTREE_REQUIRED_ITERATIONS:",
        "missing.append(key)",
    );
    try expectContains(checker, "return (\"missing_rbtree_iterations\", [key])");
    try expectContains(checker, "return (\"iteration_value_type\", (key, actual))");
    try expectBefore(
        checker,
        "return (\"rbtree_iteration_mismatch\", (key, expected, actual))",
        "return (\"iteration_mismatch\", (key, expected, actual))",
    );
    try expectBefore(
        checker,
        "missing_rbtree_iteration_output = \"\\n\".join(",
        "assert_case(kind == \"missing_rbtree_iterations\", \"missing rbtree output iteration\", (kind, payload))",
    );
    try expectBefore(
        checker,
        "missing_rbtree_iteration_expectations = base_expectations()",
        "assert_case(kind == \"expectations_missing_rbtree_iterations\", \"missing rbtree expectation iteration\", (kind, payload))",
    );
}
