const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_shared_smoke = Command{
    .name = "Run current Phase 1 shared tests-root smoke",
    .run = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
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

test "workflow keeps Phase 1 shared smoke as exact tests-root command" {
    const smoke_marker = try markerFor(phase1_shared_smoke, std.testing.allocator);
    defer std.testing.allocator.free(smoke_marker);

    try requireContains(workflow_text, smoke_marker);
    try requireMissing(
        workflow_text,
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/phase1_helpers_build.zig",
    );
    try requireMissing(
        workflow_text,
        "run: zig build phase1-host-tools-smoke --build-file build.zig",
    );
}

test "Phase 1 shared smoke remains after closure validation" {
    const smoke_marker = try markerFor(phase1_shared_smoke, std.testing.allocator);
    defer std.testing.allocator.free(smoke_marker);

    const shared_reminder_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 shared reminder packet\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
    );
    const closure_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
    );
    const closure_check_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py\n",
    );
    const smoke_index = try markerIndex(workflow_text, smoke_marker);

    try std.testing.expect(shared_reminder_index < closure_selftest_index);
    try std.testing.expect(closure_selftest_index < closure_check_index);
    try std.testing.expect(closure_check_index < smoke_index);
}

test "Phase 1 shared smoke stays outside the Phase 3 interop packet" {
    const smoke_marker = try markerFor(phase1_shared_smoke, std.testing.allocator);
    defer std.testing.allocator.free(smoke_marker);

    const phase3_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n",
    );
    const phase3_check_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 3 interop packet\n        run: python3 scripts/zigux/run-phase3-checks.py\n",
    );
    const smoke_index = try markerIndex(workflow_text, smoke_marker);

    try std.testing.expect(smoke_index > phase3_selftest_index);
    try std.testing.expect(smoke_index > phase3_check_index);
}
