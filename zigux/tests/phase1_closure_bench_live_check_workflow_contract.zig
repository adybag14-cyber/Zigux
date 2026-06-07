const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const bench_checker_path = "scripts/zigux/check-phase1-bench.py";
const live_checker_path = "scripts/zigux/check-phase1-bench-live-check-workflow.py";
const closure_note_path = "Documentation/zigux/phase1-closure.md";

const bench_self_test_step = "- name: Self-test current Phase 1 bench checker";
const bench_self_test_run = "run: python3 scripts/zigux/check-phase1-bench.py --self-test";
const bench_live_check_step = "- name: Check current Phase 1 bench packet";
const bench_live_check_run = "run: python3 scripts/zigux/check-phase1-bench.py";
const live_guard_self_test_step = "- name: Self-test current Phase 1 bench live-check workflow guard";
const live_guard_self_test_run = "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test";
const live_guard_check_step = "- name: Check current Phase 1 bench live-check workflow guard packet";
const live_guard_check_run = "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py";
const find_bit_bench_step = "- name: Self-test current Phase 1 find-bit bench anchor checker";
const find_bit_bench_run = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(512 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireLineOnce(haystack: []const u8, line: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |candidate| {
        if (std.mem.eql(u8, std.mem.trim(u8, candidate, " \t\r"), line)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn requireOrdered(haystack: []const u8, chain: []const []const u8) !void {
    var previous: usize = 0;
    var have_previous = false;
    for (chain) |needle| {
        const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingOrderedNeedle;
        if (have_previous) {
            try std.testing.expect(index > previous);
        }
        previous = index;
        have_previous = true;
    }
}

test "workflow keeps bench self-test live-check and follow-up order explicit" {
    const workflow = try readFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try requireLineOnce(workflow, bench_self_test_step);
    try requireLineOnce(workflow, bench_self_test_run);
    try requireLineOnce(workflow, bench_live_check_step);
    try requireLineOnce(workflow, bench_live_check_run);
    try requireLineOnce(workflow, live_guard_self_test_step);
    try requireLineOnce(workflow, live_guard_self_test_run);
    try requireLineOnce(workflow, live_guard_check_step);
    try requireLineOnce(workflow, live_guard_check_run);
    try requireLineOnce(workflow, find_bit_bench_step);
    try requireLineOnce(workflow, find_bit_bench_run);
    try requireOrdered(workflow, &.{
        bench_self_test_step,
        bench_live_check_step,
        live_guard_self_test_step,
        live_guard_check_step,
        find_bit_bench_step,
    });
}

test "dedicated live-check guard pins the same workflow handoff vocabulary" {
    const checker = try readFile(live_checker_path);
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "BENCH_SELF_TEST_STEP");
    try requireContains(checker, "BENCH_LIVE_CHECK_STEP");
    try requireContains(checker, "FIND_BIT_BENCH_STEP");
    try requireContains(checker, "REQUIRED_CHAIN");
    try requireContains(checker, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass");
    try requireContains(checker, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW=pass");
}

test "live-check guard still anchors the bench checker markers it protects" {
    const live_checker = try readFile(live_checker_path);
    defer std.testing.allocator.free(live_checker);
    const bench_checker = try readFile(bench_checker_path);
    defer std.testing.allocator.free(bench_checker);

    const markers = [_][]const u8{
        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
        "--self-test",
    };
    for (markers) |marker| {
        try requireContains(live_checker, marker);
        try requireContains(bench_checker, marker);
    }
}

test "closure note keeps the bench guard role in the parked closure packet" {
    const note = try readFile(closure_note_path);
    defer std.testing.allocator.free(note);

    try requireContains(note, "PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py");
    try requireContains(note, "PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py");
    try requireContains(note, "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py");
    try requireContains(note, "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM");
    try requireContains(note, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM");
}
