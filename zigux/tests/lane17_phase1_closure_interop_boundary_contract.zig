const std = @import("std");
const options = @import("workflow_options");

const workflow_text = options.workflow_text;

const WorkflowError = error{
    MissingWorkflowMarker,
    DuplicateWorkflowMarker,
    ReorderedWorkflowMarker,
    UnexpectedWorkflowGap,
    StaleWorkflowVariant,
};

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const boundary_steps = [_]Step{
    .{
        .name = "Self-test current Phase 1 shared reminder checker",
        .run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 shared reminder packet",
        .run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 closure validator",
        .run = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "Check current Phase 1 closure packet",
        .run = "python3 scripts/zigux/validate-phase1-closure.py",
    },
    .{
        .name = "Self-test current Phase 3 interop packet",
        .run = "python3 scripts/zigux/validate_phase3_selftest.py",
    },
    .{
        .name = "Check current Phase 3 interop packet",
        .run = "python3 scripts/zigux/run-phase3-checks.py",
    },
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn stepBlock(step: Step, buffer: []u8) []const u8 {
    return std.fmt.bufPrint(
        buffer,
        "      - name: {s}\n        run: {s}",
        .{ step.name, step.run },
    ) catch unreachable;
}

fn requireOnce(haystack: []const u8, needle: []const u8) WorkflowError!usize {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowMarker;
    if (countOccurrences(haystack, needle) != 1) return error.DuplicateWorkflowMarker;
    return index;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) WorkflowError!void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.StaleWorkflowVariant;
}

fn requireNoStepBetween(haystack: []const u8, left_end: usize, right_start: usize) WorkflowError!void {
    if (std.mem.indexOf(u8, haystack[left_end..right_start], "\n      - name: ") != null) {
        return error.UnexpectedWorkflowGap;
    }
}

fn validateBoundary(haystack: []const u8) WorkflowError!void {
    var previous_start: ?usize = null;
    var previous_end: ?usize = null;

    for (boundary_steps) |step| {
        var block_buffer: [256]u8 = undefined;
        const block = stepBlock(step, &block_buffer);
        const index = try requireOnce(haystack, block);

        if (previous_start) |start| {
            if (index <= start) return error.ReorderedWorkflowMarker;
            try requireNoStepBetween(haystack, previous_end.?, index);
        }

        previous_start = index;
        previous_end = index + block.len;
    }

    try requireAbsent(haystack, "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --allow-missing");
    try requireAbsent(haystack, "        run: python3 scripts/zigux/validate-phase1-closure.py --allow-missing");
    try requireAbsent(haystack, "        run: python3 scripts/zigux/validate-phase1-closure.py --root");
    try requireAbsent(haystack, "        run: python3 scripts/zigux/run-phase3-checks.py --allow-missing");
}

test "current bootstrap keeps shared reminder, closure, and interop gates adjacent" {
    try validateBoundary(workflow_text);
}

test "shared reminder packet hands directly to the Phase 1 closure validator" {
    var shared_buffer: [256]u8 = undefined;
    var closure_buffer: [256]u8 = undefined;
    const shared_packet = stepBlock(boundary_steps[1], &shared_buffer);
    const closure_self_test = stepBlock(boundary_steps[2], &closure_buffer);

    const shared_index = try requireOnce(workflow_text, shared_packet);
    const closure_index = try requireOnce(workflow_text, closure_self_test);
    try requireNoStepBetween(workflow_text, shared_index + shared_packet.len, closure_index);
}

test "closure packet hands directly to the Phase 3 interop self-test" {
    var closure_buffer: [256]u8 = undefined;
    var interop_buffer: [256]u8 = undefined;
    const closure_packet = stepBlock(boundary_steps[3], &closure_buffer);
    const interop_self_test = stepBlock(boundary_steps[4], &interop_buffer);

    const closure_index = try requireOnce(workflow_text, closure_packet);
    const interop_index = try requireOnce(workflow_text, interop_self_test);
    try requireNoStepBetween(workflow_text, closure_index + closure_packet.len, interop_index);
}

test "contract rejects a missing closure packet" {
    const fixture =
        "      - name: Self-test current Phase 1 shared reminder checker\n" ++
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n" ++
        "      - name: Check current Phase 1 shared reminder packet\n" ++
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n" ++
        "      - name: Self-test current Phase 1 closure validator\n" ++
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n" ++
        "      - name: Self-test current Phase 3 interop packet\n" ++
        "        run: python3 scripts/zigux/validate_phase3_selftest.py\n" ++
        "      - name: Check current Phase 3 interop packet\n" ++
        "        run: python3 scripts/zigux/run-phase3-checks.py";

    try std.testing.expectError(error.MissingWorkflowMarker, validateBoundary(fixture));
}

test "contract rejects duplicate boundary commands" {
    const duplicate = workflow_text ++ "\n      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py\n";

    try std.testing.expectError(error.DuplicateWorkflowMarker, validateBoundary(duplicate));
}

test "contract rejects stale permissive closure variants" {
    const stale = workflow_text ++ "\n        run: python3 scripts/zigux/validate-phase1-closure.py --allow-missing\n";

    try std.testing.expectError(error.StaleWorkflowVariant, validateBoundary(stale));
}
