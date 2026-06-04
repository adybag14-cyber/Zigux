const std = @import("std");

const guard_paths = [_][]const u8{
    "scripts/zigux/check-phase1-bench-live-check-workflow.py",
    "../../scripts/zigux/check-phase1-bench-live-check-workflow.py",
};

fn readGuardSource() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    for (guard_paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(32 * 1024)) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn expectBefore(haystack: []const u8, left: []const u8, right: []const u8) !void {
    const left_index = std.mem.indexOf(u8, haystack, left) orelse return error.TestUnexpectedResult;
    const right_index = std.mem.indexOf(u8, haystack, right) orelse return error.TestUnexpectedResult;
    try std.testing.expect(left_index < right_index);
}

test "lane17 guard keeps the bench live workflow handoff explicit" {
    const guard_source = try readGuardSource();
    defer std.testing.allocator.free(guard_source);

    try expectContains(guard_source, "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try expectContains(guard_source, "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")");

    try expectContains(guard_source, "BENCH_SELF_TEST_STEP = \"Self-test current Phase 1 bench checker\"");
    try expectContains(guard_source, "BENCH_SELF_TEST_RUN = \"python3 scripts/zigux/check-phase1-bench.py --self-test\"");
    try expectContains(guard_source, "BENCH_LIVE_CHECK_STEP = \"Check current Phase 1 bench packet\"");
    try expectContains(guard_source, "BENCH_LIVE_CHECK_RUN = \"python3 scripts/zigux/check-phase1-bench.py\"");
    try expectContains(guard_source, "FIND_BIT_BENCH_STEP = \"Self-test current Phase 1 find-bit bench anchor checker\"");
    try expectContains(guard_source, "FIND_BIT_BENCH_RUN = \"python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\"");
}

test "lane17 guard requires exactly the intended workflow chain and marker packet" {
    const guard_source = try readGuardSource();
    defer std.testing.allocator.free(guard_source);

    try expectContains(guard_source, "REQUIRED_STEPS = (");
    try expectContains(guard_source, "REQUIRED_CHAIN = (");
    try expectContains(guard_source, "BENCH_SELF_TEST_STEP,");
    try expectContains(guard_source, "BENCH_LIVE_CHECK_STEP,");
    try expectContains(guard_source, "FIND_BIT_BENCH_STEP,");
    try expectBefore(guard_source, "BENCH_SELF_TEST_STEP,", "BENCH_LIVE_CHECK_STEP,");
    try expectBefore(guard_source, "BENCH_LIVE_CHECK_STEP,", "FIND_BIT_BENCH_STEP,");

    try expectContains(guard_source, "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS");
    try expectContains(guard_source, "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM");
    try expectContains(guard_source, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM");
    try expectContains(guard_source, "--self-test");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(guard_source, "for marker in BENCH_CHECKER_MARKERS:"));
}

test "lane17 guard self-test protects missing duplicate reordered miswired and marker failures" {
    const guard_source = try readGuardSource();
    defer std.testing.allocator.free(guard_source);

    try expectContains(guard_source, "missing live bench check");
    try expectContains(guard_source, "duplicate live bench check");
    try expectContains(guard_source, "reordered live bench check");
    try expectContains(guard_source, "miswired live bench check");
    try expectContains(guard_source, "missing bench marker");

    try expectContains(guard_source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass");
    try expectContains(guard_source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6");
    try expectContains(guard_source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW=pass");
    try expectContains(guard_source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_STEP_COUNT={len(REQUIRED_STEPS)}");
    try expectContains(guard_source, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_MARKER_COUNT={len(BENCH_CHECKER_MARKERS)}");
}
