const std = @import("std");
const options = @import("lane17_phase1_workflow_entry_after_phase2_options");

const workflow = options.workflow;

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase2_tail_gates = [_]Gate{
    .{
        .name = "Run current Phase 2 aggregate make route",
        .command = "make -C zigux phase2",
    },
    .{
        .name = "Validate current Phase 2 tool packet",
        .command = "python3 scripts/zigux/validate-phase2.py",
    },
    .{
        .name = "Self-test current Phase 2 closure validator",
        .command = "python3 scripts/zigux/validate-phase2-closure.py --self-test",
    },
    .{
        .name = "Check current Phase 2 closure packet",
        .command = "python3 scripts/zigux/validate-phase2-closure.py",
    },
};

const phase1_entry_gates = [_]Gate{
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
};

fn indexAfter(haystack: []const u8, needle: []const u8, offset: usize) ?usize {
    const relative = std.mem.indexOf(u8, haystack[offset..], needle) orelse return null;
    return offset + relative;
}

fn uniqueIndex(needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, workflow, needle) orelse return error.MissingWorkflowMarker;
    const after_first = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, workflow[after_first..], needle) == null);
    return first;
}

fn expectGateAfter(gate: Gate, offset: usize) !usize {
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

    const name_index = indexAfter(workflow, name_marker, offset) orelse return error.MissingWorkflowGateName;
    const command_index = indexAfter(workflow, command_marker, name_index) orelse return error.MissingWorkflowGateCommand;
    try std.testing.expect(command_index > name_index);
    return command_index + command_marker.len;
}

test "phase1 workflow entry stays after the phase2 closure tail" {
    var cursor: usize = 0;
    for (phase2_tail_gates) |gate| {
        cursor = try expectGateAfter(gate, cursor);
    }

    for (phase1_entry_gates) |gate| {
        cursor = try expectGateAfter(gate, cursor);
    }
}

test "phase1 direct-owner entry does not drift before phase2 closure" {
    const phase2_closure = try uniqueIndex("- name: Check current Phase 2 closure packet");
    const phase1_entry = try uniqueIndex("- name: Self-test current Phase 1 direct-owner checker");
    try std.testing.expect(phase2_closure < phase1_entry);

    const stale_phase1_before_closure = std.mem.indexOf(
        u8,
        workflow[0..phase2_closure],
        "check-phase1-direct-owner-markers.py",
    );
    try std.testing.expect(stale_phase1_before_closure == null);
}

test "phase2 tail and phase1 entry commands stay exact and unique" {
    inline for (phase2_tail_gates ++ phase1_entry_gates) |gate| {
        const command_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            "run: {s}\n",
            .{gate.command},
        );
        defer std.testing.allocator.free(command_marker);

        _ = try uniqueIndex(command_marker);
    }
}
