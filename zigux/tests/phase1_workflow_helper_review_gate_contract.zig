const std = @import("std");
const options = @import("phase1_workflow_helper_review_gate_options");

const workflow = options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const helper_review_commands = [_]Command{
    .{
        .name = "Self-test current Phase 1 direct-owner checker",
        .run = "zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-owner markers",
        .run = "zig run scripts/zigux/check_phase1_direct_owner_markers.zig",
    },
    .{
        .name = "Self-test current Phase 1 direct-anchor manifest gate",
        .run = "zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-anchor manifest gate",
        .run = "zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig",
    },
    .{
        .name = "Self-test current Phase 1 string review checker",
        .run = "zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 string review packet",
        .run = "zig run scripts/zigux/check_phase1_string_review_packet.zig",
    },
    .{
        .name = "Self-test current Phase 1 find-bit review checker",
        .run = "zig run scripts/zigux/check_phase1_find_bit_review_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit review packet",
        .run = "zig run scripts/zigux/check_phase1_find_bit_review_packet.zig",
    },
    .{
        .name = "Self-test current Phase 1 bitmap direct-anchor checker",
        .run = "zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 bitmap direct-anchor packet",
        .run = "zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig",
    },
    .{
        .name = "Self-test current Phase 1 rbtree review checker",
        .run = "zig run scripts/zigux/check_phase1_rbtree_review_packet.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 rbtree review packet",
        .run = "zig run scripts/zigux/check_phase1_rbtree_review_packet.zig",
    },
};

fn markerFor(command: Command, allocator: std.mem.Allocator) ![]u8 {
    return try std.fmt.allocPrint(
        allocator,
        "- name: {s}\n        run: {s}\n",
        .{ command.name, command.run },
    );
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MissingWorkflowMarker;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, marker).?);
    return index;
}

fn commandIndex(command: Command) !usize {
    const marker = try markerFor(command, std.testing.allocator);
    defer std.testing.allocator.free(marker);
    return try markerIndex(workflow, marker);
}

fn requireMissing(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, workflow, needle) == null);
}

test "workflow keeps exact Phase 1 helper-review command pairs" {
    for (helper_review_commands) |command| {
        _ = try commandIndex(command);
    }

    try requireMissing("run: zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --allow-missing\n");
    try requireMissing("run: zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig -- --allow-missing\n");
    try requireMissing("run: zig run scripts/zigux/check_phase1_string_review_packet.zig -- --allow-missing\n");
    try requireMissing("run: zig run scripts/zigux/check_phase1_find_bit_review_packet.zig -- --allow-missing\n");
    try requireMissing("run: zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig -- --allow-missing\n");
    try requireMissing("run: zig run scripts/zigux/check_phase1_rbtree_review_packet.zig -- --allow-missing\n");
}

test "helper-review gates run in direct-owner to rbtree order" {
    var cursor: usize = 0;
    for (helper_review_commands) |command| {
        const index = try commandIndex(command);
        try std.testing.expect(index >= cursor);
        cursor = index;
    }
}

test "helper-review cluster stays after Phase 2 closure and before route summary" {
    const phase2_closure = try markerIndex(
        workflow,
        "- name: Check current Phase 2 closure packet\n        run: zig run scripts/zigux/validate_phase2_closure.zig\n",
    );
    const direct_owner = try commandIndex(helper_review_commands[0]);
    const rbtree_review = try commandIndex(helper_review_commands[helper_review_commands.len - 1]);
    const route_summary = try markerIndex(
        workflow,
        "- name: Self-test current Phase 1 route summary checker\n        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test\n",
    );

    try std.testing.expect(phase2_closure < direct_owner);
    try std.testing.expect(rbtree_review < route_summary);
}

test "helper-review route-summary handoff stays before bench shared reminder and closure" {
    const rbtree_review = try commandIndex(helper_review_commands[helper_review_commands.len - 1]);
    const route_summary_check = try markerIndex(
        workflow,
        "- name: Check current Phase 1 route summary packet\n        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig\n",
    );
    const bench_selftest = try markerIndex(
        workflow,
        "- name: Self-test current Phase 1 bench checker\n        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test\n",
    );
    const shared_reminder = try markerIndex(
        workflow,
        "- name: Self-test current Phase 1 shared reminder checker\n        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test\n",
    );
    const closure_check = try markerIndex(
        workflow,
        "- name: Check current Phase 1 closure packet\n        run: zig run scripts/zigux/validate_phase1_closure.zig\n",
    );

    try std.testing.expect(rbtree_review < route_summary_check);
    try std.testing.expect(route_summary_check < bench_selftest);
    try std.testing.expect(bench_selftest < shared_reminder);
    try std.testing.expect(shared_reminder < closure_check);
}
