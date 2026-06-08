const std = @import("std");

pub const default_workflow_path = ".github/workflows/zigux-bootstrap.yml";

const WorkflowError = error{
    MissingStep,
    DuplicateStep,
    MissingRun,
    MultiLineRun,
    DisplacedRun,
};

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_steps = [_]Step{
    .{
        .name = "- name: Self-test current Phase 1 direct-owner checker",
        .run = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 direct-owner markers",
        .run = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 direct-anchor manifest gate",
        .run = "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 direct-anchor manifest gate",
        .run = "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 string review checker",
        .run = "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 string review packet",
        .run = "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 find-bit review checker",
        .run = "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 find-bit review packet",
        .run = "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 bitmap direct-anchor checker",
        .run = "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 bitmap direct-anchor packet",
        .run = "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 rbtree review checker",
        .run = "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 rbtree review packet",
        .run = "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 route summary checker",
        .run = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 route summary packet",
        .run = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 bench checker",
        .run = "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 bench packet",
        .run = "run: python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 bench live-check workflow guard",
        .run = "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 bench live-check workflow guard packet",
        .run = "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 find-bit bench anchor checker",
        .run = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 find-bit bench anchor packet",
        .run = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 shared reminder checker",
        .run = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 shared reminder packet",
        .run = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "- name: Self-test current Phase 1 closure validator",
        .run = "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "- name: Check current Phase 1 closure packet",
        .run = "run: python3 scripts/zigux/validate-phase1-closure.py",
    },
};

pub fn validateWorkflow(content: []const u8) WorkflowError!void {
    for (phase1_steps) |step| {
        try validateCommandSlot(content, step);
    }
}

pub fn validateWorkflowFile(allocator: std.mem.Allocator, path: []const u8) !void {
    const content = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
    defer allocator.free(content);
    try validateWorkflow(content);
}

fn validateCommandSlot(content: []const u8, step: Step) WorkflowError!void {
    const step_pos = try uniqueLine(content, step.name, WorkflowError.MissingStep, WorkflowError.DuplicateStep);
    const step_end = lineEnd(content, step_pos, content.len);
    const next_line = firstNonEmptyLineAfter(content, step_end) orelse return WorkflowError.MissingRun;
    const trimmed = trimLine(next_line);

    if (std.mem.eql(u8, trimmed, "run: |")) return WorkflowError.MultiLineRun;
    if (!std.mem.eql(u8, trimmed, step.run)) return WorkflowError.DisplacedRun;

    const next_step = nextStepStartAfter(content, step_end) orelse content.len;
    if (countExactLinesBetween(content, step.run, step_end, next_step) != 1) return WorkflowError.MissingRun;
}

fn uniqueLine(content: []const u8, marker: []const u8, missing: WorkflowError, duplicate: WorkflowError) WorkflowError!usize {
    var cursor: usize = 0;
    var found: ?usize = null;
    while (cursor < content.len) {
        const end = lineEnd(content, cursor, content.len);
        if (std.mem.eql(u8, trimLine(content[cursor..end]), marker)) {
            if (found != null) return duplicate;
            found = cursor;
        }
        cursor = if (end < content.len) end + 1 else content.len;
    }
    return found orelse missing;
}

fn countExactLinesBetween(content: []const u8, marker: []const u8, start: usize, end: usize) usize {
    if (end <= start) return 0;
    var count: usize = 0;
    var cursor = start;
    while (cursor < end) {
        const line_end = lineEnd(content, cursor, end);
        if (std.mem.eql(u8, trimLine(content[cursor..line_end]), marker)) count += 1;
        cursor = if (line_end < end) line_end + 1 else end;
    }
    return count;
}

fn firstNonEmptyLineAfter(content: []const u8, start: usize) ?[]const u8 {
    var cursor = if (start < content.len and content[start] == '\n') start + 1 else start;
    while (cursor < content.len) {
        const end = lineEnd(content, cursor, content.len);
        const trimmed = trimLine(content[cursor..end]);
        if (trimmed.len != 0) return content[cursor..end];
        cursor = if (end < content.len) end + 1 else content.len;
    }
    return null;
}

fn nextStepStartAfter(content: []const u8, start: usize) ?usize {
    var cursor = start;
    while (cursor < content.len) {
        const end = lineEnd(content, cursor, content.len);
        if (std.mem.startsWith(u8, trimLine(content[cursor..end]), "- name:")) return cursor;
        cursor = if (end < content.len) end + 1 else content.len;
    }
    return null;
}

fn lineEnd(content: []const u8, start: usize, end: usize) usize {
    return start + (std.mem.indexOfScalar(u8, content[start..end], '\n') orelse content[start..end].len);
}

fn trimLine(line: []const u8) []const u8 {
    return std.mem.trim(u8, line, " \t\r");
}

test "current Phase 1 workflow steps use immediate single-line run slots" {
    try validateWorkflowFile(std.testing.allocator, workflow_path);
}

test "multi-line run blocks are rejected for Phase 1 checker steps" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: |
        \\          python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;

    try std.testing.expectError(WorkflowError.MultiLineRun, validateCommandSlot(workflow, phase1_steps[0]));
}

test "displaced command lines are rejected even when the exact command appears later" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Check current Phase 1 bench packet
        \\        env:
        \\          ZIGUX_PHASE: phase1
        \\        run: python3 scripts/zigux/check-phase1-bench.py
    ;

    try std.testing.expectError(WorkflowError.DisplacedRun, validateCommandSlot(workflow, phase1_steps[15]));
}

test "duplicate step names fail closed" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Check current Phase 1 closure packet
        \\        run: python3 scripts/zigux/validate-phase1-closure.py
        \\      - name: Check current Phase 1 closure packet
        \\        run: python3 scripts/zigux/validate-phase1-closure.py
    ;

    try std.testing.expectError(WorkflowError.DuplicateStep, validateCommandSlot(workflow, phase1_steps[23]));
}

pub const workflow_path: []const u8 = @import("lane17_options").workflow_path;
