const std = @import("std");

pub const default_workflow_path = ".github/workflows/zigux-bootstrap.yml";

const WorkflowOrderError = error{
    MissingPhase2Boundary,
    MissingPhase3Boundary,
    MissingStep,
    DuplicateStep,
    MissingRun,
    DuplicateRun,
    WrongOrder,
};

const StepPair = struct {
    self_name: []const u8,
    self_run: []const u8,
    check_name: []const u8,
    check_run: []const u8,
};

const phase2_closure_boundary = "- name: Check current Phase 2 closure packet";
const phase3_start_boundary = "- name: Self-test current Phase 3 interop packet";

const phase1_pairs = [_]StepPair{
    .{
        .self_name = "- name: Self-test current Phase 1 direct-owner checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        .check_name = "- name: Check current Phase 1 direct-owner markers",
        .check_run = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 direct-anchor manifest gate",
        .self_run = "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        .check_name = "- name: Check current Phase 1 direct-anchor manifest gate",
        .check_run = "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 string review checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        .check_name = "- name: Check current Phase 1 string review packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 find-bit review checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        .check_name = "- name: Check current Phase 1 find-bit review packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 bitmap direct-anchor checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
        .check_name = "- name: Check current Phase 1 bitmap direct-anchor packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 rbtree review checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
        .check_name = "- name: Check current Phase 1 rbtree review packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 route summary checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        .check_name = "- name: Check current Phase 1 route summary packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 bench checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        .check_name = "- name: Check current Phase 1 bench packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 bench live-check workflow guard",
        .self_run = "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
        .check_name = "- name: Check current Phase 1 bench live-check workflow guard packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 find-bit bench anchor checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        .check_name = "- name: Check current Phase 1 find-bit bench anchor packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 shared reminder checker",
        .self_run = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        .check_name = "- name: Check current Phase 1 shared reminder packet",
        .check_run = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .self_name = "- name: Self-test current Phase 1 closure validator",
        .self_run = "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        .check_name = "- name: Check current Phase 1 closure packet",
        .check_run = "run: python3 scripts/zigux/validate-phase1-closure.py",
    },
};

pub fn validateWorkflow(content: []const u8) WorkflowOrderError!void {
    var previous = try uniqueLine(
        content,
        phase2_closure_boundary,
        WorkflowOrderError.MissingPhase2Boundary,
        WorkflowOrderError.DuplicateStep,
    );

    for (phase1_pairs) |pair| {
        const self_name = try uniqueLine(content, pair.self_name, WorkflowOrderError.MissingStep, WorkflowOrderError.DuplicateStep);
        const self_run = try uniqueLine(content, pair.self_run, WorkflowOrderError.MissingRun, WorkflowOrderError.DuplicateRun);
        const check_name = try uniqueLine(content, pair.check_name, WorkflowOrderError.MissingStep, WorkflowOrderError.DuplicateStep);
        const check_run = try uniqueLine(content, pair.check_run, WorkflowOrderError.MissingRun, WorkflowOrderError.DuplicateRun);

        if (!(previous < self_name and self_name < self_run and self_run < check_name and check_name < check_run)) {
            return WorkflowOrderError.WrongOrder;
        }
        previous = check_run;
    }

    const phase3_start = try uniqueLine(
        content,
        phase3_start_boundary,
        WorkflowOrderError.MissingPhase3Boundary,
        WorkflowOrderError.DuplicateStep,
    );
    if (!(previous < phase3_start)) return WorkflowOrderError.WrongOrder;
}

pub fn validateWorkflowFile(allocator: std.mem.Allocator, path: []const u8) !void {
    const content = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
    defer allocator.free(content);
    try validateWorkflow(content);
}

fn uniqueLine(content: []const u8, marker: []const u8, missing: WorkflowOrderError, duplicate: WorkflowOrderError) WorkflowOrderError!usize {
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

fn lineEnd(content: []const u8, start: usize, end: usize) usize {
    return start + (std.mem.indexOfScalar(u8, content[start..end], '\n') orelse content[start..end].len);
}

fn trimLine(line: []const u8) []const u8 {
    return std.mem.trim(u8, line, " \t\r");
}

test "current Phase 1 workflow pairs stay ordered between Phase 2 and Phase 3" {
    try validateWorkflowFile(std.testing.allocator, workflow_path);
}

test "live check cannot precede its self-test pair" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Check current Phase 2 closure packet
        \\        run: python3 scripts/zigux/validate-phase2-closure.py
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Self-test current Phase 3 interop packet
        \\        run: python3 scripts/zigux/validate_phase3_selftest.py
    ;

    try std.testing.expectError(WorkflowOrderError.WrongOrder, validateWorkflow(workflow));
}

test "duplicate pair steps fail closed" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Check current Phase 2 closure packet
        \\        run: python3 scripts/zigux/validate-phase2-closure.py
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Self-test current Phase 3 interop packet
        \\        run: python3 scripts/zigux/validate_phase3_selftest.py
    ;

    try std.testing.expectError(WorkflowOrderError.DuplicateStep, validateWorkflow(workflow));
}

test "phase2 closure boundary is required before Phase 1 pairs" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Self-test current Phase 3 interop packet
        \\        run: python3 scripts/zigux/validate_phase3_selftest.py
    ;

    try std.testing.expectError(WorkflowOrderError.MissingPhase2Boundary, validateWorkflow(workflow));
}

pub const workflow_path: []const u8 = @import("lane17_options").workflow_path;
