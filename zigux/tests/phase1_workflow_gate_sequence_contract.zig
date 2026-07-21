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
        .command = "zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-owner markers",
        .command = "zig run scripts/zigux/check_phase1_direct_owner_markers.zig",
    },
    .{
        .name = "Self-test current Phase 1 direct-anchor manifest gate",
        .command = "zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-anchor manifest gate",
        .command = "zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig",
    },
    .{
        .name = "Self-test current Phase 1 string review checker",
        .command = "zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 string review packet",
        .command = "zig run scripts/zigux/check_phase1_string_review_packet.zig",
    },
    .{
        .name = "Self-test current Phase 1 find-bit review checker",
        .command = "zig run scripts/zigux/check_phase1_find_bit_review_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit review packet",
        .command = "zig run scripts/zigux/check_phase1_find_bit_review_packet.zig",
    },
    .{
        .name = "Self-test current Phase 1 bitmap direct-anchor checker",
        .command = "zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 bitmap direct-anchor packet",
        .command = "zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig",
    },
    .{
        .name = "Self-test current Phase 1 rbtree review checker",
        .command = "zig run scripts/zigux/check_phase1_rbtree_review_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 rbtree review packet",
        .command = "zig run scripts/zigux/check_phase1_rbtree_review_packet.zig",
    },
    .{
        .name = "Self-test current Phase 1 route summary checker",
        .command = "zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 route summary packet",
        .command = "zig run scripts/zigux/check_phase1_route_summary_counts.zig",
    },
    .{
        .name = "Self-test current Phase 1 bench checker",
        .command = "zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
    },
    .{
        .name = "Self-test current Phase 1 find-bit bench anchor checker",
        .command = "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit bench anchor packet",
        .command = "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig",
    },
    .{
        .name = "Self-test current Phase 1 shared reminder checker",
        .command = "zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 shared reminder packet",
        .command = "zig run scripts/zigux/check_phase1_shared_reminder_packet.zig",
    },
    .{
        .name = "Self-test current Phase 1 closure validator",
        .command = "zig run scripts/zigux/validate_phase1_closure.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 closure packet",
        .command = "zig run scripts/zigux/validate_phase1_closure.zig",
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
