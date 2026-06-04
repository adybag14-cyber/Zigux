const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_closure_selftest = Command{
    .name = "Self-test current Phase 1 closure validator",
    .run = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
};

const phase1_closure_check = Command{
    .name = "Check current Phase 1 closure packet",
    .run = "python3 scripts/zigux/validate-phase1-closure.py",
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

test "workflow keeps closure validator self-test and live packet check exact" {
    const selftest_marker = try markerFor(phase1_closure_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_closure_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    try requireContains(workflow_text, selftest_marker);
    try requireContains(workflow_text, check_marker);
    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/validate-phase1-closure.py --root",
    );
    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/validate-phase1-closure.py --allow-missing",
    );
}

test "closure live check follows shared reminder gates before phase3" {
    const selftest_marker = try markerFor(phase1_closure_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_closure_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    const shared_reminder_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 shared reminder checker\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    );
    const shared_reminder_check_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 shared reminder packet\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
    );
    const closure_selftest_index = try markerIndex(workflow_text, selftest_marker);
    const closure_check_index = try markerIndex(workflow_text, check_marker);
    const phase3_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n",
    );

    try std.testing.expect(shared_reminder_selftest_index < shared_reminder_check_index);
    try std.testing.expect(shared_reminder_check_index < closure_selftest_index);
    try std.testing.expect(closure_selftest_index < closure_check_index);
    try std.testing.expect(closure_check_index < phase3_selftest_index);
}

test "closure gate remains after route summary and before shared tests smoke" {
    const check_marker = try markerFor(phase1_closure_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    const route_summary_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 route summary packet\n        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n",
    );
    const bench_anchor_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 find-bit bench anchor packet\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\n",
    );
    const closure_index = try markerIndex(workflow_text, check_marker);
    const phase1_smoke_index = try markerIndex(
        workflow_text,
        "- name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );

    try std.testing.expect(route_summary_index < bench_anchor_index);
    try std.testing.expect(bench_anchor_index < closure_index);
    try std.testing.expect(closure_index < phase1_smoke_index);
}
