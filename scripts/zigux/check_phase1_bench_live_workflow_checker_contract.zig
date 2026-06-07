const std = @import("std");
const checker_path = @import("checker_path");

const required_steps = [_][]const u8{
    "BENCH_SELF_TEST_STEP = \"Self-test current Phase 1 bench checker\"",
    "BENCH_LIVE_CHECK_STEP = \"Check current Phase 1 bench packet\"",
    "FIND_BIT_BENCH_STEP = \"Self-test current Phase 1 find-bit bench anchor checker\"",
    "REQUIRED_CHAIN = (",
    "BENCH_SELF_TEST_STEP,",
    "BENCH_LIVE_CHECK_STEP,",
    "FIND_BIT_BENCH_STEP,",
};

const required_run_lines = [_][]const u8{
    "BENCH_SELF_TEST_RUN = \"python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    "BENCH_LIVE_CHECK_RUN = \"python3 scripts/zigux/check-phase1-bench.py\"",
    "FIND_BIT_BENCH_RUN = \"python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\"",
};

const required_markers = [_][]const u8{
    "\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS\"",
    "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"",
    "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"",
    "\"--self-test\"",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectBefore(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "bench live workflow checker keeps the required step chain explicit" {
    const source = try readFile(std.testing.allocator, checker_path.value);
    defer std.testing.allocator.free(source);

    for (required_steps) |marker| {
        try expectContains(source, marker);
    }
    for (required_run_lines) |marker| {
        try expectContains(source, marker);
    }

    try expectBefore(source, "BENCH_SELF_TEST_STEP,", "BENCH_LIVE_CHECK_STEP,");
    try expectBefore(source, "BENCH_LIVE_CHECK_STEP,", "FIND_BIT_BENCH_STEP,");
}

test "bench checker markers remain part of the live handoff guard" {
    const source = try readFile(std.testing.allocator, checker_path.value);
    defer std.testing.allocator.free(source);

    try expectContains(source, "BENCH_CHECKER_MARKERS = (");
    for (required_markers) |marker| {
        try expectContains(source, marker);
    }
    try expectContains(source, "for marker in BENCH_CHECKER_MARKERS:");
}

test "checker self-test still covers missing duplicate reordered miswired and marker failures" {
    const source = try readFile(std.testing.allocator, checker_path.value);
    defer std.testing.allocator.free(source);

    const cases = [_][]const u8{
        "missing live bench check",
        "duplicate live bench check",
        "reordered live bench check",
        "miswired live bench check",
        "missing bench marker",
    };

    try expectContains(source, "def run_self_test() -> None:");
    for (cases) |case| {
        try expectContains(source, case);
    }
    try expectContains(source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass");
    try expectContains(source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6");
}
