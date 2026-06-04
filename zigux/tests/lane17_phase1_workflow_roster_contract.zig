const std = @import("std");

const workflow_path = @import("build_options").workflow_path;

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    UnexpectedPhase1StepCount,
};

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_steps = [_]Step{
    .{
        .name = "      - name: Self-test current Phase 1 direct-owner checker",
        .run = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 direct-owner markers",
        .run = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 direct-anchor manifest gate",
        .run = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 direct-anchor manifest gate",
        .run = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 string review checker",
        .run = "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 string review packet",
        .run = "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 find-bit review checker",
        .run = "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 find-bit review packet",
        .run = "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
        .run = "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bitmap direct-anchor packet",
        .run = "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 rbtree review checker",
        .run = "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 rbtree review packet",
        .run = "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 route summary checker",
        .run = "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 route summary packet",
        .run = "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bench checker",
        .run = "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bench packet",
        .run = "        run: python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bench live-check workflow guard",
        .run = "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bench live-check workflow guard packet",
        .run = "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 find-bit bench anchor checker",
        .run = "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 find-bit bench anchor packet",
        .run = "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 shared reminder checker",
        .run = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 shared reminder packet",
        .run = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "      - name: Self-test current Phase 1 closure validator",
        .run = "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 closure packet",
        .run = "        run: python3 scripts/zigux/validate-phase1-closure.py",
    },
};

fn countExactLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, line, needle)) count += 1;
    }
    return count;
}

fn countPhase1Names(haystack: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.startsWith(u8, line, "      - name: ") and
            std.mem.indexOf(u8, line, "Phase 1") != null)
        {
            count += 1;
        }
    }
    return count;
}

fn indexOfExactLine(haystack: []const u8, needle: []const u8) ?usize {
    var start: usize = 0;
    while (start <= haystack.len) {
        const end = std.mem.indexOfScalarPos(u8, haystack, start, '\n') orelse haystack.len;
        if (std.mem.eql(u8, haystack[start..end], needle)) return start;
        if (end == haystack.len) break;
        start = end + 1;
    }
    return null;
}

fn requireOnce(haystack: []const u8, needle: []const u8) WorkflowError!usize {
    const first = indexOfExactLine(haystack, needle) orelse return error.MissingMarker;
    if (countExactLines(haystack, needle) != 1) return error.DuplicateMarker;
    return first;
}

fn requireAfter(previous: *?usize, haystack: []const u8, needle: []const u8) WorkflowError!void {
    const index = try requireOnce(haystack, needle);
    if (previous.*) |previous_index| {
        if (index <= previous_index) return error.ReorderedMarker;
    }
    previous.* = index;
}

fn validatePhase1Roster(workflow: []const u8) WorkflowError!void {
    var previous: ?usize = null;
    try requireAfter(&previous, workflow, "      - name: Check current Phase 2 closure packet");
    try requireAfter(&previous, workflow, "        run: python3 scripts/zigux/validate-phase2-closure.py");

    for (phase1_steps) |step| {
        try requireAfter(&previous, workflow, step.name);
        try requireAfter(&previous, workflow, step.run);
    }

    try requireAfter(&previous, workflow, "      - name: Self-test current Phase 3 interop packet");
    try requireAfter(&previous, workflow, "        run: python3 scripts/zigux/validate_phase3_selftest.py");

    if (countPhase1Names(workflow) != phase1_steps.len) {
        return error.UnexpectedPhase1StepCount;
    }
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "current bootstrap workflow keeps the complete Phase 1 roster between Phase 2 closure and Phase 3 interop" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validatePhase1Roster(workflow);
}

test "roster contract rejects a missing live bench packet" {
    const workflow =
        \\      - name: Check current Phase 2 closure packet
        \\        run: python3 scripts/zigux/validate-phase2-closure.py
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase1Roster(workflow));
}

test "roster contract rejects duplicate Phase 1 workflow step names" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const duplicate = try std.mem.concat(std.testing.allocator, u8, &.{
        workflow,
        "\n      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
    });
    defer std.testing.allocator.free(duplicate);

    try std.testing.expectError(error.DuplicateMarker, validatePhase1Roster(duplicate));
}

test "roster contract rejects unexpected extra Phase 1 steps" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const extra = try std.mem.concat(std.testing.allocator, u8, &.{
        workflow,
        "\n      - name: Run current Phase 1 untracked helper smoke\n        run: make -C zigux phase1-untracked\n",
    });
    defer std.testing.allocator.free(extra);

    try std.testing.expectError(error.UnexpectedPhase1StepCount, validatePhase1Roster(extra));
}
