const std = @import("std");

const required_duplicate_reasons = [_][]const u8{
    "expectations_duplicate_keys",
    "expectations_duplicate_iteration_keys",
    "expectations_duplicate_exact_checksum_keys",
    "expectations_duplicate_checksums",
};

const required_json_error_markers = [_][]const u8{
    "expectations_json_error",
    "EXPECTATIONS_JSON_ERROR",
    "EXPECTATIONS_JSON_LINE",
    "EXPECTATIONS_JSON_COLUMN",
};

const exact_checksum_keys = [_][]const u8{
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

const GateFile = struct {
    contents: []u8,

    fn deinit(self: GateFile) void {
        std.testing.allocator.free(self.contents);
    }
};

fn readGateFile(path: []const u8, limit: usize) !GateFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            std.testing.allocator,
            .limited(limit),
        ),
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "bench expectations JSON guard keeps duplicate-key failures visible" {
    const checker = try readGateFile("scripts/zigux/check-phase1-bench.py", 192 * 1024);
    defer checker.deinit();
    const expectations = try readGateFile("zigux/tests/fixtures/phase1_bench_expectations.json", 64 * 1024);
    defer expectations.deinit();

    try expectContains(checker.contents, "class DuplicateTrackingDict");
    try expectContains(checker.contents, "object_pairs_hook=DuplicateTrackingDict");
    inline for (required_duplicate_reasons) |reason| {
        try expectContains(checker.contents, reason);
    }

    try expectContains(checker.contents, "duplicate_top_level_text");
    try expectContains(checker.contents, "\\\"status\\\": \\\"pass\\\"");
    try expectContains(checker.contents, "\\\"status\\\": \\\"fail\\\"");

    try expectContains(expectations.contents, "\"status\": \"pass\"");
    try expectContains(expectations.contents, "\"iterations\"");
    try expectContains(expectations.contents, "\"checksums\"");
    try expectContains(expectations.contents, "\"exact_checksums\"");

    inline for (exact_checksum_keys) |key| {
        try expectContains(checker.contents, key);
        try expectContains(expectations.contents, key);
    }
}

test "bench expectations JSON guard reports parse failures with line and column" {
    const checker = try readGateFile("scripts/zigux/check-phase1-bench.py", 192 * 1024);
    defer checker.deinit();

    inline for (required_json_error_markers) |marker| {
        try expectContains(checker.contents, marker);
    }

    try expectContains(checker.contents, "json.JSONDecodeError");
    try expectContains(checker.contents, "exc.msg");
    try expectContains(checker.contents, "exc.lineno");
    try expectContains(checker.contents, "exc.colno");
}

test "bench expectations JSON guard stays wired through closure and workflow" {
    const closure = try readGateFile("scripts/zigux/validate-phase1-closure.py", 384 * 1024);
    defer closure.deinit();
    const workflow = try readGateFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer workflow.deinit();

    try expectContains(closure.contents, "scripts/zigux/check-phase1-bench.py");
    try expectContains(closure.contents, "zigux/tests/fixtures/phase1_bench_expectations.json");
    try expectContains(closure.contents, "zigux/tests/phase1_bench.zig");
    try expectContains(closure.contents, "PHASE1_BENCH");

    if (std.mem.indexOf(u8, workflow.contents, "python3 scripts/zigux/check-phase1-bench.py --self-test")) |self_test_index| {
        const check_index = std.mem.indexOfPos(
            u8,
            workflow.contents,
            self_test_index + "python3 scripts/zigux/check-phase1-bench.py --self-test".len,
            "python3 scripts/zigux/check-phase1-bench.py",
        ) orelse return error.MissingBenchCheckStep;
        try std.testing.expect(self_test_index < check_index);
    }
    try expectOrdered(workflow.contents, "python3 scripts/zigux/check-phase1-bench.py", "python3 scripts/zigux/validate-phase1-closure.py");
}
