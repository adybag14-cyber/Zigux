const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;
const checker_text = workflow_options.checker_text;

const WorkflowStep = struct {
    name: []const u8,
    run: []const u8,
};

const bench_self_test = WorkflowStep{
    .name = "Self-test current Phase 1 bench checker",
    .run = "zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
};

const bench_live_check = WorkflowStep{
    .name = "Check current Phase 1 bench packet",
    .run = "zig run scripts/zigux/check_phase1_bench.zig",
};

const live_guard_self_test = WorkflowStep{
    .name = "Self-test current Phase 1 bench live-check workflow guard",
    .run = "zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test",
};

const live_guard_check = WorkflowStep{
    .name = "Check current Phase 1 bench live-check workflow guard packet",
    .run = "zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig",
};

const find_bit_bench_self_test = WorkflowStep{
    .name = "Self-test current Phase 1 find-bit bench anchor checker",
    .run = "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
};

fn markerFor(step: WorkflowStep, allocator: std.mem.Allocator) ![]u8 {
    return try std.fmt.allocPrint(
        allocator,
        "- name: {s}\n        run: {s}\n",
        .{ step.name, step.run },
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, marker) orelse return error.MarkerMissing;
    try std.testing.expectEqual(first, std.mem.lastIndexOf(u8, haystack, marker).?);
    return first;
}

test "workflow keeps the Phase 1 bench live-check guard as exact commands" {
    const live_guard_self_test_marker = try markerFor(live_guard_self_test, std.testing.allocator);
    defer std.testing.allocator.free(live_guard_self_test_marker);
    const live_guard_check_marker = try markerFor(live_guard_check, std.testing.allocator);
    defer std.testing.allocator.free(live_guard_check_marker);

    try requireContains(workflow_text, live_guard_self_test_marker);
    try requireContains(workflow_text, live_guard_check_marker);
    try requireMissing(
        workflow_text,
        "run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --allow-missing",
    );
    try requireMissing(
        workflow_text,
        "run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --root",
    );
}

test "live-check guard is ordered between the bench packet and find-bit bench anchors" {
    const bench_self_test_marker = try markerFor(bench_self_test, std.testing.allocator);
    defer std.testing.allocator.free(bench_self_test_marker);
    const bench_live_check_marker = try markerFor(bench_live_check, std.testing.allocator);
    defer std.testing.allocator.free(bench_live_check_marker);
    const live_guard_self_test_marker = try markerFor(live_guard_self_test, std.testing.allocator);
    defer std.testing.allocator.free(live_guard_self_test_marker);
    const live_guard_check_marker = try markerFor(live_guard_check, std.testing.allocator);
    defer std.testing.allocator.free(live_guard_check_marker);
    const find_bit_bench_self_test_marker = try markerFor(find_bit_bench_self_test, std.testing.allocator);
    defer std.testing.allocator.free(find_bit_bench_self_test_marker);

    const bench_self_test_index = try markerIndex(workflow_text, bench_self_test_marker);
    const bench_live_check_index = try markerIndex(workflow_text, bench_live_check_marker);
    const live_guard_self_test_index = try markerIndex(workflow_text, live_guard_self_test_marker);
    const live_guard_check_index = try markerIndex(workflow_text, live_guard_check_marker);
    const find_bit_bench_self_test_index = try markerIndex(workflow_text, find_bit_bench_self_test_marker);

    try std.testing.expect(bench_self_test_index < bench_live_check_index);
    try std.testing.expect(bench_live_check_index < live_guard_self_test_index);
    try std.testing.expect(live_guard_self_test_index < live_guard_check_index);
    try std.testing.expect(live_guard_check_index < find_bit_bench_self_test_index);
}

test "live-check guard checker advertises its pass packet and required counts" {
    try requireContains(checker_text, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW=pass");
    try requireContains(checker_text, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass");
    try requireContains(checker_text, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_STEP_COUNT");
    try requireContains(checker_text, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_MARKER_COUNT");
    try requireContains(checker_text, "PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=6");
}
