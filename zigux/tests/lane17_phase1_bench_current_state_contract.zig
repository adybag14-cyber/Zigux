const std = @import("std");

const workflow_current =
    \\      - name: Self-test current Phase 1 route summary checker
    \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
    \\
    \\      - name: Check current Phase 1 route summary packet
    \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py
    \\
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
    \\
    \\      - name: Self-test current Phase 1 bench live-check workflow guard
    \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test
    \\
    \\      - name: Check current Phase 1 bench live-check workflow guard packet
    \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    \\
    \\      - name: Self-test current Phase 1 shared reminder checker
    \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
;

const guard_checker_current =
    \\BENCH_SELF_TEST_STEP = "Self-test current Phase 1 bench checker"
    \\BENCH_SELF_TEST_RUN = "python3 scripts/zigux/check-phase1-bench.py --self-test"
    \\BENCH_LIVE_CHECK_STEP = "Check current Phase 1 bench packet"
    \\BENCH_LIVE_CHECK_RUN = "python3 scripts/zigux/check-phase1-bench.py"
    \\FIND_BIT_BENCH_STEP = "Self-test current Phase 1 find-bit bench anchor checker"
    \\FIND_BIT_BENCH_RUN = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test"
    \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS
    \\PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM
    \\PHASE1_BENCH_RBTREE_CACHED_CHECKSUM
    \\PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6
;

const required_workflow_chain = [_][]const u8{
    "Self-test current Phase 1 route summary checker",
    "Check current Phase 1 route summary packet",
    "Self-test current Phase 1 bench checker",
    "Check current Phase 1 bench packet",
    "Self-test current Phase 1 bench live-check workflow guard",
    "Check current Phase 1 bench live-check workflow guard packet",
    "Self-test current Phase 1 find-bit bench anchor checker",
    "Check current Phase 1 find-bit bench anchor packet",
    "Self-test current Phase 1 shared reminder checker",
};

const required_run_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
};

const required_guard_markers = [_][]const u8{
    "BENCH_LIVE_CHECK_STEP = \"Check current Phase 1 bench packet\"",
    "BENCH_LIVE_CHECK_RUN = \"python3 scripts/zigux/check-phase1-bench.py\"",
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn countTrimmedLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireLineOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLines(haystack, needle));
}

fn requireOrdered(haystack: []const u8, chain: []const []const u8) !void {
    var previous: usize = 0;
    var seen_any = false;
    for (chain) |needle| {
        const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowItem;
        if (seen_any) {
            try std.testing.expect(index > previous);
        }
        previous = index;
        seen_any = true;
    }
}

fn requireWorkflowState(workflow: []const u8) !void {
    for (required_workflow_chain) |step| {
        try requireOnce(workflow, step);
    }
    for (required_run_lines) |run_line| {
        try requireLineOnce(workflow, run_line);
    }
    try requireOrdered(workflow, &required_workflow_chain);
}

fn requireGuardCheckerState(checker: []const u8) !void {
    for (required_guard_markers) |marker| {
        try requireOnce(checker, marker);
    }
}

test "lane17 current bench workflow state keeps live check between self-test and find-bit anchors" {
    try requireWorkflowState(workflow_current);
}

test "lane17 bench live-check workflow guard checker pins the current live-check surface" {
    try requireGuardCheckerState(guard_checker_current);
}

test "lane17 current workflow contract rejects old missing live bench packet gap" {
    const old_gap =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    ;
    try std.testing.expectError(error.TestExpectedEqual, requireWorkflowState(old_gap));
}

test "lane17 current workflow contract rejects duplicate live bench packet checks" {
    const duplicate_live_check = workflow_current ++
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
    ;
    try std.testing.expectError(error.TestExpectedEqual, requireWorkflowState(duplicate_live_check));
}

test "lane17 guard checker contract rejects dropped rbtree bench marker" {
    const missing_marker =
        \\BENCH_LIVE_CHECK_STEP = "Check current Phase 1 bench packet"
        \\BENCH_LIVE_CHECK_RUN = "python3 scripts/zigux/check-phase1-bench.py"
        \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS
        \\PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM
        \\PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6
    ;
    try std.testing.expectError(error.TestExpectedEqual, requireGuardCheckerState(missing_marker));
}
