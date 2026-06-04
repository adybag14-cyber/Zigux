const std = @import("std");
const workflow_options = @import("workflow_options");

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

test "lane17 current workflow keeps the bench live-check gap exact" {
    const workflow = workflow_options.workflow_text;

    const bench_self_test = try singleMarkerOffset(workflow, bench_self_test_step);
    const find_bit_self_test = try singleMarkerOffset(workflow, find_bit_bench_self_test_step);
    const find_bit_live_check = try singleMarkerOffset(workflow, find_bit_bench_live_check_step);

    try std.testing.expectEqual(@as(usize, 0), countMarkers(workflow, bench_live_check_step));
    try std.testing.expect(bench_self_test < find_bit_self_test);
    try std.testing.expect(find_bit_self_test < find_bit_live_check);
}

test "lane17 patch target inserts one live bench check before find-bit bench anchors" {
    const workflow = workflow_options.workflow_text;

    const bench_self_test = try singleMarkerOffset(workflow, bench_self_test_step);
    const find_bit_self_test = try singleMarkerOffset(workflow, find_bit_bench_self_test_step);
    const insert_at = bench_self_test + bench_self_test_step.len;

    const patched = try std.mem.concat(std.testing.allocator, u8, &.{
        workflow[0..insert_at],
        "\n\n",
        bench_live_check_step,
        workflow[insert_at..],
    });
    defer std.testing.allocator.free(patched);

    const patched_bench_self_test = try singleMarkerOffset(patched, bench_self_test_step);
    const patched_bench_live_check = try singleMarkerOffset(patched, bench_live_check_step);
    const patched_find_bit_self_test = try singleMarkerOffset(patched, find_bit_bench_self_test_step);
    const patched_find_bit_live_check = try singleMarkerOffset(patched, find_bit_bench_live_check_step);

    try std.testing.expect(patched_bench_self_test < patched_bench_live_check);
    try std.testing.expect(patched_bench_live_check < patched_find_bit_self_test);
    try std.testing.expect(patched_find_bit_self_test < patched_find_bit_live_check);
    try std.testing.expect(find_bit_self_test > insert_at);
}
