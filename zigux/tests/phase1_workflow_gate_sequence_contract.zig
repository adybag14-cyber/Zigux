const std = @import("std");
const options = @import("phase1_workflow_gate_sequence_options");

const workflow = options.workflow;

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase1_gates = [_]Gate{
    .{
        .name = "Self-test current Phase 1 direct-owner checker",
        .command = "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-owner markers",
        .command = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "Self-test current Phase 1 direct-anchor manifest gate",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-anchor manifest gate",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "Self-test current Phase 1 string review checker",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 string review packet",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit review checker",
        .command = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit review packet",
        .command = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 bitmap direct-anchor checker",
        .command = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bitmap direct-anchor packet",
        .command = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 rbtree review checker",
        .command = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 rbtree review packet",
        .command = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 route summary checker",
        .command = "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "Check current Phase 1 route summary packet",
        .command = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .name = "Self-test current Phase 1 bench checker",
        .command = "python3 scripts/zigux/check-phase1-bench.py --self-test",
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

fn expectUnique(needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, workflow, needle) orelse return error.MissingWorkflowMarker;
    const after_first = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, workflow[after_first..], needle) == null);
    return first;
}

test "phase1 bootstrap workflow keeps helper gates ordered before shared smoke" {
    var cursor: usize = 0;
    for (phase1_gates) |gate| {
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

test "phase1 workflow gate commands stay single-owner checks" {
    for (phase1_gates) |gate| {
        const command_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            "run: {s}\n",
            .{gate.command},
        );
        defer std.testing.allocator.free(command_marker);

        _ = try expectUnique(command_marker);
    }
}
