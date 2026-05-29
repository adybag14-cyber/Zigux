const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Gate = struct {
    step: []const u8,
    command: []const u8,
};

const phase1_gates = [_]Gate{
    .{
        .step = "Self-test current Phase 1 bench checker",
        .command = "python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .step = "Self-test current Phase 1 shared reminder checker",
        .command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .step = "Check current Phase 1 shared reminder packet",
        .command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkflow() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

test "bootstrap workflow keeps the Phase 1 helper gate commands visible" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    for (phase1_gates) |gate| {
        try expectContains(workflow, gate.step);
        try expectContains(workflow, gate.command);
    }
}

test "shared reminder gate follows the bench checker in workflow order" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const bench_index = std.mem.indexOf(u8, workflow, phase1_gates[0].step).?;
    const reminder_selftest_index = std.mem.indexOf(u8, workflow, phase1_gates[1].step).?;
    const reminder_packet_index = std.mem.indexOf(u8, workflow, phase1_gates[2].step).?;

    try std.testing.expect(bench_index < reminder_selftest_index);
    try std.testing.expect(reminder_selftest_index < reminder_packet_index);
}
