const std = @import("std");

const max_file_bytes = 1024 * 1024;

const Phase1Gate = struct {
    readme_marker: []const u8,
    workflow_step: []const u8,
    checker_marker: []const u8,
};

const phase1_gates = [_]Phase1Gate{
    .{
        .readme_marker = "`scripts/zigux/check-phase1-bench.py`",
        .workflow_step = "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        .checker_marker = "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    },
    .{
        .readme_marker = "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
        .workflow_step = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        .checker_marker = "\"run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\"",
    },
    .{
        .readme_marker = "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
        .workflow_step = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        .checker_marker = "\"run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\"",
    },
};

const workflow_gate_lines = [_][]const u8{
    "\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n",
    "\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    "\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
};

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "tests README names the Phase 1 workflow gate files" {
    const tests_readme = try readFixture(std.testing.allocator, "zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);

    try expectContains(tests_readme, "current direct-readback Phase 1 reminder packet:");
    try expectContains(tests_readme, "`scripts/zigux/check-phase1-bench.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase1-shared-reminder-packet.py`");
    try expectContains(tests_readme, "`.github/workflows/zigux-bootstrap.yml`");
    try expectContains(tests_readme, "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(tests_readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet");
}

test "workflow executes the Phase 1 shared reminder gates after bench self-test" {
    const bootstrap_workflow = try readFixture(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(bootstrap_workflow);

    for (workflow_gate_lines) |workflow_gate_line| {
        try expectContains(bootstrap_workflow, workflow_gate_line);
    }

    try expectOrdered(
        bootstrap_workflow,
        workflow_gate_lines[0],
        workflow_gate_lines[1],
    );
    try expectOrdered(
        bootstrap_workflow,
        workflow_gate_lines[1],
        workflow_gate_lines[2],
    );
}

test "shared reminder checker pins the tests README and workflow gate markers" {
    const shared_reminder_checker = try readFixture(std.testing.allocator, "scripts/zigux/check-phase1-shared-reminder-packet.py");
    defer std.testing.allocator.free(shared_reminder_checker);

    try expectContains(shared_reminder_checker, "\"zigux/tests/README.md\"");
    try expectContains(shared_reminder_checker, "\".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(shared_reminder_checker, "\"current direct-readback Phase 1 reminder packet:\"");
    try expectContains(shared_reminder_checker, "\"broader Phase 1 closure companions stay outside the narrow direct-readback packet");
    try expectContains(shared_reminder_checker, "PHASE1_SHARED_REMINDER_PACKET=pass");
    try expectContains(shared_reminder_checker, "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass");
    try expectContains(shared_reminder_checker, "- `scripts/zigux/check-phase1-shared-reminder-packet.py`");

    for (phase1_gates) |gate| {
        try expectContains(shared_reminder_checker, gate.checker_marker);
    }
}
