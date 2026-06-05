const std = @import("std");

const GateFile = struct {
    path: []const u8,
    contents: []u8,
};

const bench_output_keys = [_][]const u8{
    "PHASE1_BENCH",
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
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

const output_guard_reasons = [_][]const u8{
    "\"duplicate\"",
    "\"unexpected\"",
    "\"status\"",
    "\"missing_rbtree_iterations\"",
    "\"rbtree_iteration_mismatch\"",
    "\"iteration_mismatch\"",
    "\"missing_rbtree_exact_checksums\"",
    "\"missing_bitmap_exact_checksums\"",
    "\"missing_find_bit_exact_checksums\"",
    "\"missing_string_exact_checksums\"",
    "\"missing_hweight_exact_checksums\"",
    "\"missing_list_sort_exact_checksums\"",
    "\"checksum_value_type\"",
    "\"nonpositive_checksum\"",
    "\"exact_checksum_mismatch\"",
    "\"missing\"",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadGateFile(path: []const u8, limit: usize) !GateFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadGateFile(file: GateFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectFileContains(file: GateFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "phase1 bench checker keeps runtime output guard reasons explicit" {
    const bench_checker = try loadGateFile("scripts/zigux/check-phase1-bench.py", 192 * 1024);
    defer unloadGateFile(bench_checker);

    try expectFileContains(bench_checker, "def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:");
    try expectFileContains(bench_checker, "def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:");
    try expectFileContains(bench_checker, "counts.get(key, 0) > 1");
    try expectFileContains(bench_checker, "key.startswith(\"PHASE1_BENCH\") and key not in required_keys");
    try expectFileContains(bench_checker, "parsed.get(\"PHASE1_BENCH\") != expectations[\"status\"]");
    try expectFileContains(bench_checker, "expected_exact = expectations[\"exact_checksums\"].get(key)");

    inline for (output_guard_reasons) |reason| {
        try expectContains(bench_checker.contents, reason);
    }

    try expectFileContains(bench_checker, "PHASE1_BENCH_CHECK=fail");
    try expectFileContains(bench_checker, "PHASE1_BENCH_CHECK_REASON={kind}");
    try expectFileContains(bench_checker, "BENCH_COMMAND_EXIT={result.returncode}");
    try expectFileContains(bench_checker, "PHASE1_BENCH_CHECK=pass");
    try expectFileContains(bench_checker, "PHASE1_BENCH_EXPECTATIONS={expectations_file}");
    try expectFileContains(bench_checker, "PHASE1_BENCH_SOURCE={phase1_bench}");
    try expectFileContains(bench_checker, "PHASE1_BENCH_ZIG={zig}");
}

test "phase1 bench output roster stays aligned with expectations fixture" {
    const bench_checker = try loadGateFile("scripts/zigux/check-phase1-bench.py", 192 * 1024);
    defer unloadGateFile(bench_checker);
    const expectations = try loadGateFile("zigux/tests/fixtures/phase1_bench_expectations.json", 64 * 1024);
    defer unloadGateFile(expectations);

    try expectFileContains(expectations, "\"status\": \"pass\"");
    try expectFileContains(expectations, "\"iterations\"");
    try expectFileContains(expectations, "\"checksums\"");
    try expectFileContains(expectations, "\"exact_checksums\"");
    try expectFileContains(bench_checker, "required_keys = {");
    try expectFileContains(bench_checker, "*expectations[\"iterations\"]");
    try expectFileContains(bench_checker, "*expectations[\"checksums\"]");
    try expectFileContains(bench_checker, "*expectations[\"exact_checksums\"]");

    inline for (bench_output_keys) |key| {
        try expectContains(bench_checker.contents, key);
        if (!std.mem.eql(u8, key, "PHASE1_BENCH")) {
            try expectContains(expectations.contents, key);
        }
    }
}

test "phase1 bench output guard is ordered before closure validation" {
    const workflow = try loadGateFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer unloadGateFile(workflow);
    const closure_validator = try loadGateFile("scripts/zigux/validate-phase1-closure.py", 256 * 1024);
    defer unloadGateFile(closure_validator);

    try expectFileContains(closure_validator, "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")");
    try expectFileContains(closure_validator, "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")");
    try expectFileContains(closure_validator, "PHASE1_BENCH_GUARD=scripts/zigux/check-phase1-bench.py");

    try expectFileContains(workflow, "Self-test current Phase 1 bench checker");
    try expectFileContains(workflow, "python3 scripts/zigux/check-phase1-bench.py --self-test");
    try expectFileContains(workflow, "Check current Phase 1 bench packet");
    try expectFileContains(workflow, "python3 scripts/zigux/check-phase1-bench.py");
    try expectFileContains(workflow, "Check current Phase 1 closure packet");
    try expectFileContains(workflow, "python3 scripts/zigux/validate-phase1-closure.py");
    try expectBefore(
        workflow.contents,
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
        "python3 scripts/zigux/check-phase1-bench.py\n",
    );
    try expectBefore(
        workflow.contents,
        "python3 scripts/zigux/check-phase1-bench.py\n",
        "python3 scripts/zigux/validate-phase1-closure.py",
    );
}
