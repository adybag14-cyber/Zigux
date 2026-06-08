const std = @import("std");

pub const default_workflow_path = ".github/workflows/zigux-bootstrap.yml";

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    MissingRun,
    NonAdjacentPair,
};

const Pair = struct {
    self_name: []const u8,
    self_run: []const u8,
    check_name: []const u8,
    check_run: []const u8,
};

const phase1_pairs = [_]Pair{
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

pub fn validateWorkflow(content: []const u8) WorkflowError!void {
    for (phase1_pairs) |pair| {
        try validatePair(content, pair);
    }
}

pub fn validateWorkflowFile(allocator: std.mem.Allocator, path: []const u8) !void {
    const content = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
    defer allocator.free(content);
    try validateWorkflow(content);
}

fn validatePair(content: []const u8, pair: Pair) WorkflowError!void {
    const self_pos = try uniqueMarker(content, pair.self_name);
    const check_pos = try uniqueMarker(content, pair.check_name);
    if (check_pos <= self_pos) return WorkflowError.NonAdjacentPair;

    const next_step = nextStepNameAfter(content, self_pos + pair.self_name.len) orelse return WorkflowError.NonAdjacentPair;
    if (!std.mem.eql(u8, trimLine(next_step), pair.check_name)) return WorkflowError.NonAdjacentPair;

    if (!hasExactLineBetween(content, pair.self_run, self_pos, check_pos)) return WorkflowError.MissingRun;

    const after_check = check_pos + pair.check_name.len;
    const next_after_check = nextStepStartAfter(content, after_check) orelse content.len;
    if (!hasExactLineBetween(content, pair.check_run, after_check, next_after_check)) return WorkflowError.MissingRun;
}

fn uniqueMarker(content: []const u8, marker: []const u8) WorkflowError!usize {
    const first = std.mem.indexOf(u8, content, marker) orelse return WorkflowError.MissingMarker;
    if (std.mem.indexOf(u8, content[first + marker.len ..], marker) != null) return WorkflowError.DuplicateMarker;
    return first;
}

fn hasExactLineBetween(content: []const u8, marker: []const u8, start: usize, end: usize) bool {
    if (end <= start) return false;
    var cursor = start;
    while (cursor < end) {
        const line_end = lineEnd(content, cursor, end);
        if (std.mem.eql(u8, trimLine(content[cursor..line_end]), marker)) return true;
        cursor = if (line_end < end) line_end + 1 else end;
    }
    return false;
}

fn nextStepNameAfter(content: []const u8, start: usize) ?[]const u8 {
    const step_start = nextStepStartAfter(content, start) orelse return null;
    const line_end_offset = std.mem.indexOfScalar(u8, content[step_start..], '\n') orelse content[step_start..].len;
    return content[step_start .. step_start + line_end_offset];
}

fn nextStepStartAfter(content: []const u8, start: usize) ?usize {
    const needle = "- name:";
    var cursor = start;
    while (std.mem.indexOf(u8, content[cursor..], needle)) |relative| {
        const pos = cursor + relative;
        if (isLineStart(content, pos)) return pos;
        cursor = pos + needle.len;
    }
    return null;
}

fn isLineStart(content: []const u8, pos: usize) bool {
    if (pos == 0) return true;
    var cursor = pos;
    while (cursor > 0 and content[cursor - 1] != '\n') : (cursor -= 1) {
        if (content[cursor - 1] != ' ') return false;
    }
    return cursor == 0 or content[cursor - 1] == '\n';
}

fn trimLine(line: []const u8) []const u8 {
    return std.mem.trim(u8, line, " \t\r");
}

fn lineEnd(content: []const u8, start: usize, end: usize) usize {
    return start + (std.mem.indexOfScalar(u8, content[start..end], '\n') orelse content[start..end].len);
}

test "current Phase 1 workflow self-test/check pairs stay adjacent" {
    try validateWorkflowFile(std.testing.allocator, workflow_path);
}

test "inserting an unrelated step between a self-test and check fails closed" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check an unrelated packet
        \\        run: python3 scripts/zigux/check-unrelated.py
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
    ;

    try std.testing.expectError(WorkflowError.NonAdjacentPair, validatePair(workflow, phase1_pairs[0]));
}

test "missing non-self-test run command fails closed" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Self-test current Phase 1 closure validator
        \\        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
        \\      - name: Check current Phase 1 closure packet
        \\        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
    ;

    try std.testing.expectError(WorkflowError.MissingRun, validatePair(workflow, phase1_pairs[11]));
}

test "duplicate Phase 1 pair names fail closed" {
    const workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
    ;

    try std.testing.expectError(WorkflowError.DuplicateMarker, validatePair(workflow, phase1_pairs[7]));
}

pub const workflow_path: []const u8 = @import("lane17_options").workflow_path;
