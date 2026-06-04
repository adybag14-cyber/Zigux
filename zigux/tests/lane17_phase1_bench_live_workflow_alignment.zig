const std = @import("std");
const workflow_options = @import("workflow_options");

const bench_self_test_step =
    "      - name: Self-test current Phase 1 bench checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test";

const bench_live_check_step =
    "      - name: Check current Phase 1 bench packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench.py";

const bench_workflow_guard_self_test_step =
    "      - name: Self-test current Phase 1 bench live-check workflow guard\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test";

const bench_workflow_guard_live_check_step =
    "      - name: Check current Phase 1 bench live-check workflow guard packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py";

const find_bit_bench_self_test_step =
    "      - name: Self-test current Phase 1 find-bit bench anchor checker\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";

const find_bit_bench_live_check_step =
    "      - name: Check current Phase 1 find-bit bench anchor packet\n" ++
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";

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

test "lane17 current workflow keeps the bench live-check guard sequence exact" {
    const workflow = workflow_options.workflow_text;

    const bench_self_test = try singleMarkerOffset(workflow, bench_self_test_step);
    const bench_live_check = try singleMarkerOffset(workflow, bench_live_check_step);
    const guard_self_test = try singleMarkerOffset(workflow, bench_workflow_guard_self_test_step);
    const guard_live_check = try singleMarkerOffset(workflow, bench_workflow_guard_live_check_step);
    const find_bit_self_test = try singleMarkerOffset(workflow, find_bit_bench_self_test_step);
    const find_bit_live_check = try singleMarkerOffset(workflow, find_bit_bench_live_check_step);

    try std.testing.expect(bench_self_test < bench_live_check);
    try std.testing.expect(bench_live_check < guard_self_test);
    try std.testing.expect(guard_self_test < guard_live_check);
    try std.testing.expect(guard_live_check < find_bit_self_test);
    try std.testing.expect(find_bit_self_test < find_bit_live_check);
}

test "lane17 workflow keeps each bench live-check guard marker unique" {
    const workflow = workflow_options.workflow_text;

    try std.testing.expectEqual(@as(usize, 1), countMarkers(workflow, bench_self_test_step));
    try std.testing.expectEqual(@as(usize, 1), countMarkers(workflow, bench_live_check_step));
    try std.testing.expectEqual(@as(usize, 1), countMarkers(workflow, bench_workflow_guard_self_test_step));
    try std.testing.expectEqual(@as(usize, 1), countMarkers(workflow, bench_workflow_guard_live_check_step));
    try std.testing.expectEqual(@as(usize, 1), countMarkers(workflow, find_bit_bench_self_test_step));
    try std.testing.expectEqual(@as(usize, 1), countMarkers(workflow, find_bit_bench_live_check_step));
}
