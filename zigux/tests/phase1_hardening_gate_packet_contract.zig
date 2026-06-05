const std = @import("std");

const GateFile = struct {
    path: []const u8,
    contents: []u8,
};

const required_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const bench_iterations = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const bench_checksums = [_][]const u8{
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

fn optionalIndex(haystack: []const u8, needle: []const u8) ?usize {
    return std.mem.indexOf(u8, haystack, needle);
}

test "phase1 hardening gate packet keeps bench and manifest surfaces aligned" {
    const bench_checker = try loadGateFile("scripts/zigux/check-phase1-bench.py", 192 * 1024);
    defer unloadGateFile(bench_checker);
    const manifest = try loadGateFile("zigux/tests/fixtures/phase1_helper_manifest.json", 512 * 1024);
    defer unloadGateFile(manifest);
    const expectations = try loadGateFile("zigux/tests/fixtures/phase1_bench_expectations.json", 64 * 1024);
    defer unloadGateFile(expectations);

    try expectFileContains(manifest, "\"phase\": \"Phase 1\"");
    try expectFileContains(manifest, "\"status\": \"closed\"");
    try expectFileContains(manifest, "\"helper_count\": 13");
    try expectFileContains(manifest, "\"shared_replay_parked_helpers\"");
    try expectFileContains(manifest, "\"direct_anchor_followup_helpers\"");
    try expectFileContains(manifest, "\"anti_overlap_rule\"");

    inline for (required_helpers) |helper| {
        try expectContains(manifest.contents, helper);
    }

    try expectFileContains(expectations, "\"status\": \"pass\"");
    try expectFileContains(expectations, "\"exact_checksums\"");
    inline for (bench_iterations) |key| {
        try expectContains(bench_checker.contents, key);
        try expectContains(expectations.contents, key);
    }
    inline for (bench_checksums) |key| {
        try expectContains(bench_checker.contents, key);
        try expectContains(expectations.contents, key);
    }

    try expectFileContains(bench_checker, "EXPECTED_ITERATIONS");
    try expectFileContains(bench_checker, "REQUIRED_EXACT_CHECKSUMS");
    try expectContains(bench_checker.contents, "FIND_BIT");
    try expectContains(bench_checker.contents, "RBTREE");
    try expectContains(bench_checker.contents, "SOURCE_MARKER");
    try expectFileContains(bench_checker, "expectations_duplicate_exact_checksum_keys");
}

test "phase1 hardening gate packet remains wired through closure validator and workflow" {
    const closure_validator = try loadGateFile("scripts/zigux/validate-phase1-closure.py", 256 * 1024);
    defer unloadGateFile(closure_validator);
    const workflow = try loadGateFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer unloadGateFile(workflow);

    const required_paths = [_][]const u8{
        "scripts/zigux/check-phase1-bench.py",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        "zigux/tests/phase1_bench.zig",
        ".github/workflows/zigux-bootstrap.yml",
    };
    inline for (required_paths) |path| {
        try expectContains(closure_validator.contents, path);
    }

    const closure_markers = [_][]const u8{
        "PHASE1_BENCH",
        "PHASE1_HELPER_COUNT=13",
        "scripts/zigux/check-phase1-bench.py",
        "zigux/tests/fixtures/phase1_bench_expectations.json",
    };
    inline for (closure_markers) |marker| {
        try expectContains(closure_validator.contents, marker);
    }

    const workflow_steps = [_][]const u8{
        "scripts/zigux/check-phase1-bench.py",
        "python3 scripts/zigux/validate-phase1-closure.py",
    };
    inline for (workflow_steps) |step| {
        try expectContains(workflow.contents, step);
    }

    if (optionalIndex(workflow.contents, "python3 scripts/zigux/check-phase1-bench.py --self-test")) |bench_selftest| {
        if (optionalIndex(workflow.contents, "python3 scripts/zigux/check-phase1-bench.py")) |bench_check| {
            try std.testing.expect(bench_selftest < bench_check);
        }
    }
}
