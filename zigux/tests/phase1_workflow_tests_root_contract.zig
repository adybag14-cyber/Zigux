const std = @import("std");
const options = @import("phase1_workflow_tests_root_options");

const workflow = options.workflow;
const tests_readme = options.tests_readme;

const ReminderGate = struct {
    path: []const u8,
    workflow_command: []const u8,
};

const reminder_gates = [_]ReminderGate{
    .{
        .path = "scripts/zigux/check-phase1-direct-owner-markers.py",
        .workflow_command = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        .workflow_command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .path = "scripts/zigux/check-phase1-bench.py",
        .workflow_command = "python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .path = "scripts/zigux/check-phase1-shared-reminder-packet.py",
        .workflow_command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .path = "scripts/zigux/validate-phase1-closure.py",
        .workflow_command = "python3 scripts/zigux/validate-phase1-closure.py",
    },
};

const workflow_gate_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
    "python3 scripts/zigux/check-phase1-bench.py",
    "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectUnique(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    try std.testing.expect(std.mem.indexOf(u8, haystack[first + needle.len ..], needle) == null);
    return first;
}

test "phase1 tests-root reminder names workflow-backed gate packet" {
    try expectContains(tests_readme, ".github/workflows/zigux-bootstrap.yml");
    try expectContains(tests_readme, "zigux/tests/phase1_host_tools_smoke.zig");
    try expectContains(tests_readme, "zigux/tests/build.zig");
    try expectContains(tests_readme, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");

    for (reminder_gates) |gate| {
        try expectContains(tests_readme, gate.path);
        try expectContains(workflow, gate.workflow_command);
    }
}

test "phase1 workflow keeps bench and closure gates before shared smoke" {
    var cursor: usize = 0;
    for (workflow_gate_commands) |command| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "run: {s}\n", .{command});
        defer std.testing.allocator.free(marker);

        const found = std.mem.indexOf(u8, workflow[cursor..], marker) orelse return error.MissingWorkflowCommand;
        cursor += found + marker.len;
    }
}

test "phase1 workflow gate commands remain single live packet owners" {
    for (workflow_gate_commands) |command| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "run: {s}\n", .{command});
        defer std.testing.allocator.free(marker);

        _ = try expectUnique(workflow, marker);
    }
}
