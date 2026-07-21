const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_route_summary_selftest = Command{
    .name = "Self-test current Phase 1 route summary checker",
    .run = "zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test",
};

const phase1_route_summary_check = Command{
    .name = "Check current Phase 1 route summary packet",
    .run = "zig run scripts/zigux/check_phase1_route_summary_counts.zig",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

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

test "workflow keeps route-summary self-test and packet check as exact run lines" {
    const selftest_marker = try markerFor(phase1_route_summary_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_route_summary_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    try requireContains(workflow_text, selftest_marker);
    try requireContains(workflow_text, check_marker);
    try requireMissing(
        workflow_text,
        "run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --root",
    );
    try requireMissing(
        workflow_text,
        "run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --allow-missing",
    );
}

test "route-summary live check follows its self-test before bench gates" {
    const selftest_marker = try markerFor(phase1_route_summary_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_route_summary_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    const selftest_index = try markerIndex(workflow_text, selftest_marker);
    const check_index = try markerIndex(workflow_text, check_marker);
    const bench_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 bench checker\n        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test\n",
    );
    const find_bit_bench_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 find-bit bench anchor checker\n        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test\n",
    );

    try std.testing.expect(selftest_index < check_index);
    try std.testing.expect(check_index < bench_selftest_index);
    try std.testing.expect(bench_selftest_index < find_bit_bench_index);
}

test "route-summary gate stays after helper review gates and before closure/smoke" {
    const check_marker = try markerFor(phase1_route_summary_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    const rbtree_review_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 rbtree review packet\n        run: zig run scripts/zigux/check_phase1_rbtree_review_packet.zig\n",
    );
    const route_summary_index = try markerIndex(workflow_text, check_marker);
    const shared_reminder_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 shared reminder checker\n        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test\n",
    );
    const closure_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 closure validator\n        run: zig run scripts/zigux/validate_phase1_closure.zig -- --self-test\n",
    );
    const smoke_index = try markerIndex(
        workflow_text,
        "- name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );

    try std.testing.expect(rbtree_review_index < route_summary_index);
    try std.testing.expect(route_summary_index < shared_reminder_index);
    try std.testing.expect(shared_reminder_index < closure_index);
    try std.testing.expect(closure_index < smoke_index);
}
