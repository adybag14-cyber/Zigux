const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const strict_shell_steps = [_][]const u8{
    "Checkout workspace snapshot",
    "Setup pinned Zig toolchain",
    "Compile current scripts",
};

const phase1_first_step = "Self-test current Phase 1 direct-owner checker";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn stepLine(step_name: []const u8) []const u8 {
    return std.fmt.allocPrint(std.testing.allocator, "      - name: {s}", .{step_name}) catch unreachable;
}

fn indexOfStep(workflow: []const u8, step_name: []const u8) ?usize {
    const line = stepLine(step_name);
    defer std.testing.allocator.free(line);
    return std.mem.indexOf(u8, workflow, line);
}

fn requireStep(workflow: []const u8, step_name: []const u8) !usize {
    return indexOfStep(workflow, step_name) orelse error.MissingWorkflowStep;
}

fn lineAfter(workflow: []const u8, offset: usize) []const u8 {
    const end = std.mem.indexOfScalarPos(u8, workflow, offset, '\n') orelse workflow.len;
    return workflow[offset..end];
}

fn nextLineOffset(workflow: []const u8, offset: usize) ?usize {
    const end = std.mem.indexOfScalarPos(u8, workflow, offset, '\n') orelse return null;
    if (end + 1 >= workflow.len) return null;
    return end + 1;
}

fn hasStrictRunBlock(workflow: []const u8, step_name: []const u8) !bool {
    const step_offset = try requireStep(workflow, step_name);
    const next_step = std.mem.indexOfPos(u8, workflow, step_offset + 1, "\n      - name: ") orelse workflow.len;
    const block = workflow[step_offset..next_step];
    const run_offset = std.mem.indexOf(u8, block, "\n        run: |") orelse return false;
    const first_body_offset = nextLineOffset(block, run_offset + 1) orelse return false;
    const body_line = std.mem.trim(u8, lineAfter(block, first_body_offset), " \t\r\n");
    return std.mem.eql(u8, body_line, "set -euxo pipefail");
}

fn countStrictRunBlocks(workflow: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, workflow, cursor, "\n        run: |")) |run_offset| {
        const first_body_offset = nextLineOffset(workflow, run_offset + 1) orelse break;
        const body_line = std.mem.trim(u8, lineAfter(workflow, first_body_offset), " \t\r\n");
        if (std.mem.eql(u8, body_line, "set -euxo pipefail")) {
            count += 1;
        }
        cursor = first_body_offset;
    }
    return count;
}

test "checkout toolchain and compile shell blocks are fail-fast" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    for (strict_shell_steps) |step_name| {
        try std.testing.expect(try hasStrictRunBlock(workflow, step_name));
    }

    try std.testing.expectEqual(@as(usize, strict_shell_steps.len), countStrictRunBlocks(workflow));
}

test "strict setup boundary stays before the Phase 1 checker corridor" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    const phase1_start = try requireStep(workflow, phase1_first_step);
    for (strict_shell_steps) |step_name| {
        const strict_step = try requireStep(workflow, step_name);
        try std.testing.expect(strict_step < phase1_start);
    }

    const phase2_closure = try requireStep(workflow, "Check current Phase 2 closure packet");
    try std.testing.expect(phase2_closure < phase1_start);
}

test "missing strict prologue and misplaced Phase 1 start are rejected" {
    const missing_strict =
        \\      - name: Checkout workspace snapshot
        \\        run: |
        \\          tmpdir="$(mktemp -d)"
        \\
    ;
    try std.testing.expect(!try hasStrictRunBlock(missing_strict, "Checkout workspace snapshot"));

    const misplaced_phase1 =
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Compile current scripts
        \\        run: |
        \\          set -euxo pipefail
        \\
    ;
    const phase1_start = try requireStep(misplaced_phase1, phase1_first_step);
    const compile_step = try requireStep(misplaced_phase1, "Compile current scripts");
    try std.testing.expect(phase1_start < compile_step);
}
