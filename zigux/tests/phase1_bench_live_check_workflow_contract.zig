const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const live_guard_path = "scripts/zigux/check-phase1-bench-live-check-workflow.py";
const bench_checker_path = "scripts/zigux/check-phase1-bench.py";

const bench_self_test_step = "Self-test current Phase 1 bench checker";
const bench_self_test_run = "python3 scripts/zigux/check-phase1-bench.py --self-test";
const bench_live_check_step = "Check current Phase 1 bench packet";
const bench_live_check_run = "python3 scripts/zigux/check-phase1-bench.py";
const live_guard_self_test_step = "Self-test current Phase 1 bench live-check workflow guard";
const live_guard_self_test_run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test";
const live_guard_check_step = "Check current Phase 1 bench live-check workflow guard packet";
const live_guard_check_run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py";
const find_bit_bench_step = "Self-test current Phase 1 find-bit bench anchor checker";

const workflow_step_chain = [_][]const u8{
    bench_self_test_step,
    bench_live_check_step,
    live_guard_self_test_step,
    live_guard_check_step,
    find_bit_bench_step,
};

const required_workflow_run_lines = [_][]const u8{
    bench_self_test_run,
    bench_live_check_run,
    live_guard_self_test_run,
    live_guard_check_run,
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
};

const live_guard_contract_markers = [_][]const u8{
    "BENCH_SELF_TEST_STEP = \"Self-test current Phase 1 bench checker\"",
    "BENCH_SELF_TEST_RUN = \"python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    "BENCH_LIVE_CHECK_STEP = \"Check current Phase 1 bench packet\"",
    "BENCH_LIVE_CHECK_RUN = \"python3 scripts/zigux/check-phase1-bench.py\"",
    "FIND_BIT_BENCH_STEP = \"Self-test current Phase 1 find-bit bench anchor checker\"",
    "REQUIRED_CHAIN = (",
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6",
};

const live_guard_self_test_case_markers = [_][]const u8{
    "missing live bench check",
    "duplicate live bench check",
    "reordered live bench check",
    "miswired live bench check",
    "missing bench marker",
};

const bench_checker_markers = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
    "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT",
};

fn readRepoFile(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        relative_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

fn countTrimmedLineOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn expectLineOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLineOccurrences(haystack, needle));
}

fn expectContainsAtLeastOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(countOccurrences(haystack, needle) >= 1);
}

fn expectOrdered(haystack: []const u8, chain: []const []const u8) !void {
    var previous: usize = 0;
    var have_previous = false;
    for (chain) |needle| {
        const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingOrderedMarker;
        if (have_previous) {
            try std.testing.expect(index > previous);
        }
        previous = index;
        have_previous = true;
    }
}

test "phase1 bench live-check workflow guard sits between bench check and find-bit bench anchors" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    for (workflow_step_chain) |step_name| {
        try expectContainsOnce(workflow, step_name);
    }

    for (required_workflow_run_lines) |run_line| {
        var buffer: [160]u8 = undefined;
        const line = try std.fmt.bufPrint(&buffer, "run: {s}", .{run_line});
        try expectLineOnce(workflow, line);
    }

    try expectOrdered(workflow, &workflow_step_chain);
}

test "phase1 bench live-check Python guard still pins the same workflow handoff" {
    const allocator = std.testing.allocator;
    const live_guard = try readRepoFile(allocator, live_guard_path);
    defer allocator.free(live_guard);

    for (live_guard_contract_markers) |marker| {
        try expectContainsAtLeastOnce(live_guard, marker);
    }

    for (live_guard_self_test_case_markers) |marker| {
        try expectContainsAtLeastOnce(live_guard, marker);
    }

    try expectOrdered(live_guard, &[_][]const u8{
        "BENCH_SELF_TEST_STEP",
        "BENCH_LIVE_CHECK_STEP",
        "FIND_BIT_BENCH_STEP",
    });
}

test "phase1 bench checker still exposes the markers consumed by the live-check guard" {
    const allocator = std.testing.allocator;
    const bench_checker = try readRepoFile(allocator, bench_checker_path);
    defer allocator.free(bench_checker);

    for (bench_checker_markers) |marker| {
        try expectContainsAtLeastOnce(bench_checker, marker);
    }

    try expectOrdered(bench_checker, &[_][]const u8{
        "EXPECTED_ITERATIONS",
        "EXPECTED_CHECKSUMS",
        "run_self_test",
        "PHASE1_BENCH_CHECK=pass",
    });
}
