const std = @import("std");
const options = @import("lane17_phase1_bench_live_guard_bootstrap_integration_options");

const workflow = options.workflow;

const Step = struct {
    name: []const u8,
    command: []const u8,
};

const bench_guard_steps = [_]Step{
    .{
        .name = "Self-test current Phase 1 bench checker",
        .command = "zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 bench packet",
        .command = "zig run scripts/zigux/check_phase1_bench.zig",
    },
    .{
        .name = "Self-test current Phase 1 bench live-check workflow guard",
        .command = "zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 bench live-check workflow guard packet",
        .command = "zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig",
    },
    .{
        .name = "Self-test current Phase 1 find-bit bench anchor checker",
        .command = "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit bench anchor packet",
        .command = "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig",
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

fn nameMarker(step: Step) ![]u8 {
    return std.fmt.allocPrint(std.testing.allocator, "- name: {s}", .{step.name});
}

fn commandMarker(step: Step) ![]u8 {
    return std.fmt.allocPrint(std.testing.allocator, "run: {s}\n", .{step.command});
}

test "phase1 bench live-check workflow guard integration stays ordered" {
    var cursor: usize = 0;
    for (bench_guard_steps) |step| {
        const name_marker = try nameMarker(step);
        defer std.testing.allocator.free(name_marker);

        const command_marker = try commandMarker(step);
        defer std.testing.allocator.free(command_marker);

        const name_index = indexAfter(workflow, name_marker, cursor) orelse return error.MissingWorkflowStepName;
        const command_index = indexAfter(workflow, command_marker, name_index) orelse return error.MissingWorkflowStepCommand;
        try std.testing.expect(command_index > name_index);
        cursor = command_index + command_marker.len;
    }
}

test "phase1 bench live-check workflow guard commands stay unique" {
    for (bench_guard_steps) |step| {
        const command_marker = try commandMarker(step);
        defer std.testing.allocator.free(command_marker);

        _ = try expectUnique(command_marker);
    }
}

test "phase1 bench live-check guard is not a substitute for the live bench packet" {
    const bench_live_check = try expectUnique("run: zig run scripts/zigux/check_phase1_bench.zig\n");
    const guard_self_test = try expectUnique("run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test\n");
    const guard_live_check = try expectUnique("run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig\n");

    try std.testing.expect(bench_live_check < guard_self_test);
    try std.testing.expect(guard_self_test < guard_live_check);
}
