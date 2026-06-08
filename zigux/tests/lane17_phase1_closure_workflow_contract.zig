const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const closure_ladder = [_]Command{
    .{
        .name = "Self-test current Phase 1 direct-owner checker",
        .run = "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-owner markers",
        .run = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "Self-test current Phase 1 direct-anchor manifest gate",
        .run = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-anchor manifest gate",
        .run = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "Self-test current Phase 1 string review checker",
        .run = "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 string review packet",
        .run = "python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit review checker",
        .run = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit review packet",
        .run = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 bitmap direct-anchor checker",
        .run = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bitmap direct-anchor packet",
        .run = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 rbtree review checker",
        .run = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 rbtree review packet",
        .run = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 route summary checker",
        .run = "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "Check current Phase 1 route summary packet",
        .run = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .name = "Self-test current Phase 1 bench checker",
        .run = "python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bench packet",
        .run = "python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .name = "Self-test current Phase 1 bench live-check workflow guard",
        .run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bench live-check workflow guard packet",
        .run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit bench anchor checker",
        .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit bench anchor packet",
        .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 shared reminder checker",
        .run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 shared reminder packet",
        .run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 closure validator",
        .run = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "Check current Phase 1 closure packet",
        .run = "python3 scripts/zigux/validate-phase1-closure.py",
    },
};

const smoke_command = Command{
    .name = "Run current Phase 1 shared tests-root smoke",
    .run = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

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

fn requireOrdered(commands: []const Command, haystack: []const u8) !void {
    var previous: ?usize = null;
    for (commands) |command| {
        const marker = try markerFor(command, std.testing.allocator);
        defer std.testing.allocator.free(marker);
        const current = try markerIndex(haystack, marker);
        if (previous) |last| {
            try std.testing.expect(last < current);
        }
        previous = current;
    }
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "workflow keeps each Phase 1 closure command as a unique exact marker" {
    for (closure_ladder) |command| {
        const marker = try markerFor(command, std.testing.allocator);
        defer std.testing.allocator.free(marker);
        _ = try markerIndex(workflow_text, marker);
    }

    const smoke_marker = try markerFor(smoke_command, std.testing.allocator);
    defer std.testing.allocator.free(smoke_marker);
    _ = try markerIndex(workflow_text, smoke_marker);
}

test "Phase 1 closure workflow ladder stays in self-test then packet-check order" {
    try requireOrdered(&closure_ladder, workflow_text);
}

test "Phase 1 closure packet check stays before Phase 3 and after shared reminder" {
    const shared_reminder_marker = try markerFor(closure_ladder[21], std.testing.allocator);
    defer std.testing.allocator.free(shared_reminder_marker);
    const closure_check_marker = try markerFor(closure_ladder[23], std.testing.allocator);
    defer std.testing.allocator.free(closure_check_marker);
    const phase3_marker =
        "- name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n";

    const shared_reminder_index = try markerIndex(workflow_text, shared_reminder_marker);
    const closure_check_index = try markerIndex(workflow_text, closure_check_marker);
    const phase3_index = try markerIndex(workflow_text, phase3_marker);

    try std.testing.expect(shared_reminder_index < closure_check_index);
    try std.testing.expect(closure_check_index < phase3_index);
}

test "Phase 1 shared smoke remains after Phase 3 shared tests-root routes" {
    const phase3_test_marker =
        "- name: Run current Phase 3 shared tests-root packet\n        run: zig build phase3-test --build-file zigux/tests/build.zig\n";
    const phase3_dump_marker =
        "- name: Run current Phase 3 ABI dump replay\n        run: zig build phase3-dump --build-file zigux/tests/build.zig\n";
    const smoke_marker = try markerFor(smoke_command, std.testing.allocator);
    defer std.testing.allocator.free(smoke_marker);

    const phase3_test_index = try markerIndex(workflow_text, phase3_test_marker);
    const phase3_dump_index = try markerIndex(workflow_text, phase3_dump_marker);
    const smoke_index = try markerIndex(workflow_text, smoke_marker);

    try std.testing.expect(phase3_test_index < phase3_dump_index);
    try std.testing.expect(phase3_dump_index < smoke_index);
}

test "workflow avoids stale broad Phase 1 aggregate routes" {
    try requireMissing(workflow_text, "run: make -C zigux phase1\n");
    try requireMissing(workflow_text, "run: make -C zigux phase1-validate\n");
    try requireMissing(workflow_text, "run: make -C zigux phase1-test\n");
    try requireMissing(workflow_text, "run: make -C zigux phase1-bench\n");
}
