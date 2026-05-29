const std = @import("std");

const bench_self_test_step =
    "      - name: Self-test current Phase 1 bench checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test";

const bench_live_check_step =
    "      - name: Check current Phase 1 bench packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py";

const find_bit_bench_self_test_step =
    "      - name: Self-test current Phase 1 find-bit bench anchor checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";

const find_bit_bench_live_check_step =
    "      - name: Check current Phase 1 find-bit bench anchor packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";

const current_missing_handoff =
    bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

const expected_patched_handoff =
    bench_self_test_step ++
    "\n\n" ++
    bench_live_check_step ++
    "\n\n" ++
    find_bit_bench_self_test_step ++
    "\n\n" ++
    find_bit_bench_live_check_step ++
    "\n";

fn countMarkers(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn singleMarkerOffset(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowMarker;
    if (std.mem.indexOfPos(u8, haystack, first + needle.len, needle) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn appendWithBenchLiveCheck(allocator: std.mem.Allocator, workflow: []const u8) ![]u8 {
    const bench_self_test = try singleMarkerOffset(workflow, bench_self_test_step);
    const find_bit_self_test = try singleMarkerOffset(workflow, find_bit_bench_self_test_step);

    if (countMarkers(workflow, bench_live_check_step) != 0) {
        return error.LiveBenchCheckAlreadyPresent;
    }
    if (bench_self_test >= find_bit_self_test) {
        return error.WorkflowMarkerOutOfOrder;
    }

    const insert_at = bench_self_test + bench_self_test_step.len;
    return std.mem.concat(allocator, u8, &.{
        workflow[0..insert_at],
        "\n\n",
        bench_live_check_step,
        workflow[insert_at..],
    });
}

test "lane17 bench live patch applier inserts the exact workflow step" {
    const patched = try appendWithBenchLiveCheck(std.testing.allocator, current_missing_handoff);
    defer std.testing.allocator.free(patched);

    try std.testing.expectEqualStrings(expected_patched_handoff, patched);
    try std.testing.expectEqual(@as(usize, 1), countMarkers(patched, bench_live_check_step));
}

test "lane17 bench live patch applier rejects duplicate application" {
    try std.testing.expectError(
        error.LiveBenchCheckAlreadyPresent,
        appendWithBenchLiveCheck(std.testing.allocator, expected_patched_handoff),
    );
}

test "lane17 bench live patch applier rejects missing anchors" {
    const missing_bench_self_test =
        find_bit_bench_self_test_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.MissingWorkflowMarker,
        appendWithBenchLiveCheck(std.testing.allocator, missing_bench_self_test),
    );
}

test "lane17 bench live patch applier rejects reordered anchors" {
    const reordered_handoff =
        find_bit_bench_self_test_step ++
        "\n\n" ++
        bench_self_test_step ++
        "\n\n" ++
        find_bit_bench_live_check_step ++
        "\n";

    try std.testing.expectError(
        error.WorkflowMarkerOutOfOrder,
        appendWithBenchLiveCheck(std.testing.allocator, reordered_handoff),
    );
}
