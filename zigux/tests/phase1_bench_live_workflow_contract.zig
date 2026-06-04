const std = @import("std");
const options = @import("phase1_bench_live_workflow_options");

const workflow = options.workflow;

const WorkflowGate = struct {
    name: []const u8,
    command: []const u8,
};

const bench_live_window = [_]WorkflowGate{
    .{
        .name = "Self-test current Phase 1 bench checker",
        .command = "python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bench packet",
        .command = "python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .name = "Self-test current Phase 1 bench live-check workflow guard",
        .command = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bench live-check workflow guard packet",
        .command = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit bench anchor checker",
        .command = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit bench anchor packet",
        .command = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 shared reminder checker",
        .command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 shared reminder packet",
        .command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 closure validator",
        .command = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "Check current Phase 1 closure packet",
        .command = "python3 scripts/zigux/validate-phase1-closure.py",
    },
    .{
        .name = "Run current Phase 1 shared tests-root smoke",
        .command = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
};

fn indexAfter(haystack: []const u8, needle: []const u8, offset: usize) ?usize {
    const relative = std.mem.indexOf(u8, haystack[offset..], needle) orelse return null;
    return offset + relative;
}

fn expectOnce(needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, workflow, needle) orelse return error.MissingWorkflowMarker;
    const next_start = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, workflow[next_start..], needle) == null);
    return first;
}

test "phase1 bench live workflow gates stay ordered before closure and smoke" {
    var cursor: usize = 0;

    for (bench_live_window) |gate| {
        const name_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            "- name: {s}",
            .{gate.name},
        );
        defer std.testing.allocator.free(name_marker);

        const command_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            "run: {s}\n",
            .{gate.command},
        );
        defer std.testing.allocator.free(command_marker);

        const name_index = indexAfter(workflow, name_marker, cursor) orelse return error.MissingWorkflowGateName;
        const command_index = indexAfter(workflow, command_marker, name_index) orelse return error.MissingWorkflowGateCommand;
        try std.testing.expect(command_index > name_index);
        cursor = command_index + command_marker.len;
    }
}

test "phase1 bench live workflow commands remain unique" {
    for (bench_live_window) |gate| {
        const command_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            "run: {s}\n",
            .{gate.command},
        );
        defer std.testing.allocator.free(command_marker);

        _ = try expectOnce(command_marker);
    }
}
