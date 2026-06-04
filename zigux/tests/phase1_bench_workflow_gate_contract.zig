const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_bench_selftest = Command{
    .name = "Self-test current Phase 1 bench checker",
    .run = "python3 scripts/zigux/check-phase1-bench.py --self-test",
};

const phase1_bench_check = Command{
    .name = "Check current Phase 1 bench packet",
    .run = "python3 scripts/zigux/check-phase1-bench.py",
};

const phase1_bench_workflow_selftest = Command{
    .name = "Self-test current Phase 1 bench live-check workflow guard",
    .run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
};

const phase1_bench_workflow_check = Command{
    .name = "Check current Phase 1 bench live-check workflow guard packet",
    .run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
};

const phase1_find_bit_bench_selftest = Command{
    .name = "Self-test current Phase 1 find-bit bench anchor checker",
    .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
};

const phase1_find_bit_bench_check = Command{
    .name = "Check current Phase 1 find-bit bench anchor packet",
    .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
};

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn markerFor(command: Command, allocator: std.mem.Allocator) ![]u8 {
    return try std.fmt.allocPrint(
        allocator,
        "- name: {s}\n        run: {s}\n",
        .{ command.name, command.run },
    );
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, marker).?);
    return index;
}

fn commandIndex(command: Command) !usize {
    const marker = try markerFor(command, std.testing.allocator);
    defer std.testing.allocator.free(marker);
    return markerIndex(workflow_text, marker);
}

test "workflow keeps bench live-check and find-bit bench gates as exact commands" {
    _ = try commandIndex(phase1_bench_selftest);
    _ = try commandIndex(phase1_bench_check);
    _ = try commandIndex(phase1_bench_workflow_selftest);
    _ = try commandIndex(phase1_bench_workflow_check);
    _ = try commandIndex(phase1_find_bit_bench_selftest);
    _ = try commandIndex(phase1_find_bit_bench_check);

    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --allow-missing",
    );
    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --root",
    );
    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --allow-missing",
    );
}

test "bench workflow guard follows the live bench check before find-bit bench anchors" {
    const bench_selftest_index = try commandIndex(phase1_bench_selftest);
    const bench_check_index = try commandIndex(phase1_bench_check);
    const workflow_selftest_index = try commandIndex(phase1_bench_workflow_selftest);
    const workflow_check_index = try commandIndex(phase1_bench_workflow_check);
    const find_bit_selftest_index = try commandIndex(phase1_find_bit_bench_selftest);
    const find_bit_check_index = try commandIndex(phase1_find_bit_bench_check);

    try std.testing.expect(bench_selftest_index < bench_check_index);
    try std.testing.expect(bench_check_index < workflow_selftest_index);
    try std.testing.expect(workflow_selftest_index < workflow_check_index);
    try std.testing.expect(workflow_check_index < find_bit_selftest_index);
    try std.testing.expect(find_bit_selftest_index < find_bit_check_index);
}

test "bench gate window stays between route-summary and shared-reminder closure gates" {
    const route_summary_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 route summary packet\n        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n",
    );
    const bench_selftest_index = try commandIndex(phase1_bench_selftest);
    const find_bit_check_index = try commandIndex(phase1_find_bit_bench_check);
    const shared_reminder_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 shared reminder checker\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    );
    const closure_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
    );
    const smoke_index = try markerIndex(
        workflow_text,
        "- name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );

    try std.testing.expect(route_summary_index < bench_selftest_index);
    try std.testing.expect(find_bit_check_index < shared_reminder_index);
    try std.testing.expect(shared_reminder_index < closure_index);
    try std.testing.expect(closure_index < smoke_index);
}
