const std = @import("std");

const live_guard_path = "scripts/zigux/check-phase1-bench-live-check-workflow.py";

const required_step_constants = [_][]const u8{
    "BENCH_SELF_TEST_STEP = \"Self-test current Phase 1 bench checker\"",
    "BENCH_SELF_TEST_RUN = \"python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    "BENCH_LIVE_CHECK_STEP = \"Check current Phase 1 bench packet\"",
    "BENCH_LIVE_CHECK_RUN = \"python3 scripts/zigux/check-phase1-bench.py\"",
    "FIND_BIT_BENCH_STEP = \"Self-test current Phase 1 find-bit bench anchor checker\"",
    "FIND_BIT_BENCH_RUN = \"python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\"",
};

const required_step_tuple_markers = [_][]const u8{
    "(BENCH_SELF_TEST_STEP, BENCH_SELF_TEST_RUN)",
    "(BENCH_LIVE_CHECK_STEP, BENCH_LIVE_CHECK_RUN)",
    "(FIND_BIT_BENCH_STEP, FIND_BIT_BENCH_RUN)",
    "REQUIRED_CHAIN = (",
    "BENCH_SELF_TEST_STEP,\n    BENCH_LIVE_CHECK_STEP,\n    FIND_BIT_BENCH_STEP,",
};

const bench_checker_marker_contract = [_][]const u8{
    "BENCH_CHECKER_MARKERS = (",
    "\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS\"",
    "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"",
    "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"",
    "\"--self-test\"",
};

const self_test_case_markers = [_][]const u8{
    "\"missing live bench check\"",
    "\"duplicate live bench check\"",
    "\"reordered live bench check\"",
    "\"miswired live bench check\"",
    "\"missing bench marker\"",
};

const sample_root_markers = [_][]const u8{
    "def write_sample_root(root: Path) -> None:",
    "workflow_path = root / WORKFLOW_REL",
    "checker_path = root / BENCH_CHECKER_REL",
    "def expect_failure(label: str, root: Path, expected: str) -> None:",
    "if expected not in message:",
    "raise SystemExit(f\"{label}: expected validation failure\")",
};

const public_output_markers = [_][]const u8{
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass",
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6",
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW=pass",
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_STEP_COUNT",
    "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_MARKER_COUNT",
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

fn expectContainsAtLeastOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(countOccurrences(haystack, needle) >= 1);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
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

test "phase1 bench live-check checker pins required workflow handoff constants" {
    const allocator = std.testing.allocator;
    const live_guard = try readRepoFile(allocator, live_guard_path);
    defer allocator.free(live_guard);

    for (required_step_constants) |marker| {
        try expectContainsOnce(live_guard, marker);
    }
    for (required_step_tuple_markers) |marker| {
        try expectContainsAtLeastOnce(live_guard, marker);
    }

    try expectOrdered(live_guard, &[_][]const u8{
        "BENCH_SELF_TEST_STEP =",
        "BENCH_SELF_TEST_RUN =",
        "BENCH_LIVE_CHECK_STEP =",
        "BENCH_LIVE_CHECK_RUN =",
        "FIND_BIT_BENCH_STEP =",
        "FIND_BIT_BENCH_RUN =",
        "REQUIRED_STEPS = (",
        "REQUIRED_CHAIN = (",
    });
}

test "phase1 bench live-check checker preserves bench marker dependency contract" {
    const allocator = std.testing.allocator;
    const live_guard = try readRepoFile(allocator, live_guard_path);
    defer allocator.free(live_guard);

    for (bench_checker_marker_contract) |marker| {
        try expectContainsAtLeastOnce(live_guard, marker);
    }

    try expectOrdered(live_guard, &[_][]const u8{
        "BENCH_CHECKER_MARKERS = (",
        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
        "\"--self-test\",",
    });
}

test "phase1 bench live-check checker self-test keeps named negative cases" {
    const allocator = std.testing.allocator;
    const live_guard = try readRepoFile(allocator, live_guard_path);
    defer allocator.free(live_guard);

    for (sample_root_markers) |marker| {
        try expectContainsAtLeastOnce(live_guard, marker);
    }
    for (self_test_case_markers) |marker| {
        try expectContainsOnce(live_guard, marker);
    }

    try expectOrdered(live_guard, &[_][]const u8{
        "write_sample_root(root)",
        "missing live bench check",
        "duplicate live bench check",
        "reordered live bench check",
        "miswired live bench check",
        "missing bench marker",
    });
}

test "phase1 bench live-check checker keeps stable public outputs" {
    const allocator = std.testing.allocator;
    const live_guard = try readRepoFile(allocator, live_guard_path);
    defer allocator.free(live_guard);

    for (public_output_markers) |marker| {
        try expectContainsAtLeastOnce(live_guard, marker);
    }

    try expectOrdered(live_guard, &[_][]const u8{
        "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass",
        "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6",
        "PHASE1_BENCH_LIVE_CHECK_WORKFLOW=pass",
        "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_STEP_COUNT",
        "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_MARKER_COUNT",
    });
}
