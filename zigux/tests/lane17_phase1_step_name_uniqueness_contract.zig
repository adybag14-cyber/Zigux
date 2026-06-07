const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Step = struct {
    name: []const u8,
    offset: usize,
};

const phase1_corridor = [_][]const u8{
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 direct-anchor manifest gate",
    "Check current Phase 1 direct-anchor manifest gate",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 find-bit review checker",
    "Check current Phase 1 find-bit review packet",
    "Self-test current Phase 1 bitmap direct-anchor checker",
    "Check current Phase 1 bitmap direct-anchor packet",
    "Self-test current Phase 1 rbtree review checker",
    "Check current Phase 1 rbtree review packet",
    "Self-test current Phase 1 route summary checker",
    "Check current Phase 1 route summary packet",
    "Self-test current Phase 1 bench checker",
    "Check current Phase 1 bench packet",
    "Self-test current Phase 1 bench live-check workflow guard",
    "Check current Phase 1 bench live-check workflow guard packet",
    "Self-test current Phase 1 find-bit bench anchor checker",
    "Check current Phase 1 find-bit bench anchor packet",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 closure validator",
    "Check current Phase 1 closure packet",
};

const phase1_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-string-review-packet.py",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py",
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
};

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn extractStepName(line: []const u8) ?[]const u8 {
    const trimmed = std.mem.trim(u8, line, " \t\r");
    if (!std.mem.startsWith(u8, trimmed, "- name: ")) return null;
    return std.mem.trim(u8, trimmed["- name: ".len..], " \t\r");
}

fn collectSteps(allocator: std.mem.Allocator, workflow: []const u8) ![]Step {
    var steps = std.ArrayList(Step).empty;
    var line_start: usize = 0;
    while (line_start <= workflow.len) {
        const line_end = std.mem.indexOfScalarPos(u8, workflow, line_start, '\n') orelse workflow.len;
        const line = workflow[line_start..line_end];
        if (extractStepName(line)) |name| {
            try steps.append(allocator, .{
                .name = name,
                .offset = line_start,
            });
        }
        if (line_end == workflow.len) break;
        line_start = line_end + 1;
    }
    return steps.toOwnedSlice(allocator);
}

fn requireUniqueStepNames(steps: []const Step) !void {
    for (steps, 0..) |left, left_index| {
        for (steps[left_index + 1 ..]) |right| {
            if (std.mem.eql(u8, left.name, right.name)) return error.DuplicateWorkflowStepName;
        }
    }
}

fn findStep(steps: []const Step, name: []const u8) !Step {
    var found: ?Step = null;
    for (steps) |step| {
        if (std.mem.eql(u8, step.name, name)) {
            if (found != null) return error.DuplicateWorkflowStepName;
            found = step;
        }
    }
    return found orelse error.MissingWorkflowStep;
}

fn requireContainsAfter(workflow: []const u8, step: Step, command: []const u8) !void {
    const command_offset = std.mem.indexOfPos(u8, workflow, step.offset, command) orelse return error.MissingWorkflowCommand;
    if (command_offset <= step.offset) return error.WorkflowCommandBeforeStep;
}

fn expectPhase1Corridor(workflow: []const u8, steps: []const Step) !void {
    var previous: ?usize = null;
    inline for (phase1_corridor, phase1_commands) |name, command| {
        const step = try findStep(steps, name);
        if (previous) |previous_offset| {
            if (previous_offset >= step.offset) return error.WorkflowStepOutOfOrder;
        }
        try requireContainsAfter(workflow, step, command);
        previous = step.offset;
    }
}

test "phase1 workflow corridor step names stay unique and ordered" {
    const allocator = std.testing.allocator;
    const workflow = try loadWorkflow(allocator);
    defer allocator.free(workflow);

    const steps = try collectSteps(allocator, workflow);
    defer allocator.free(steps);

    try requireUniqueStepNames(steps);
    try expectPhase1Corridor(workflow, steps);
}

test "duplicate step names fail the uniqueness check" {
    const fixture =
        \\steps:
        \\  - name: Check current Phase 1 bench packet
        \\    run: python3 scripts/zigux/check-phase1-bench.py
        \\  - name: Check current Phase 1 bench packet
        \\    run: python3 scripts/zigux/check-phase1-bench.py
    ;
    const steps = try collectSteps(std.testing.allocator, fixture);
    defer std.testing.allocator.free(steps);

    try std.testing.expectError(error.DuplicateWorkflowStepName, requireUniqueStepNames(steps));
}

test "swapped corridor steps fail the ordering check" {
    const fixture =
        \\steps:
        \\  - name: Check current Phase 1 direct-owner markers
        \\    run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\  - name: Self-test current Phase 1 direct-owner checker
        \\    run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;
    const steps = try collectSteps(std.testing.allocator, fixture);
    defer std.testing.allocator.free(steps);

    try std.testing.expectError(error.WorkflowStepOutOfOrder, expectPhase1Corridor(fixture, steps));
}
