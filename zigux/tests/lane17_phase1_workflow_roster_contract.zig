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
        .run = "        run: zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 direct-owner markers",
        .run = "        run: zig run scripts/zigux/check_phase1_direct_owner_markers.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 direct-anchor manifest gate",
        .run = "        run: zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 direct-anchor manifest gate",
        .run = "        run: zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 string review checker",
        .run = "        run: zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 string review packet",
        .run = "        run: zig run scripts/zigux/check_phase1_string_review_packet.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 find-bit review checker",
        .run = "        run: zig run scripts/zigux/check_phase1_find_bit_review_packet.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 find-bit review packet",
        .run = "        run: zig run scripts/zigux/check_phase1_find_bit_review_packet.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
        .run = "        run: zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bitmap direct-anchor packet",
        .run = "        run: zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 rbtree review checker",
        .run = "        run: zig run scripts/zigux/check_phase1_rbtree_review_packet.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 rbtree review packet",
        .run = "        run: zig run scripts/zigux/check_phase1_rbtree_review_packet.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 route summary checker",
        .run = "        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 route summary packet",
        .run = "        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bench checker",
        .run = "        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bench packet",
        .run = "        run: zig run scripts/zigux/check_phase1_bench.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bench live-check workflow guard",
        .run = "        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bench live-check workflow guard packet",
        .run = "        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 find-bit bench anchor checker",
        .run = "        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 find-bit bench anchor packet",
        .run = "        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 shared reminder checker",
        .run = "        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 shared reminder packet",
        .run = "        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 closure validator",
        .run = "        run: zig run scripts/zigux/validate_phase1_closure.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 closure packet",
        .run = "        run: zig run scripts/zigux/validate_phase1_closure.zig",
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
    try requireAfter(&previous, workflow, "        run: zig run scripts/zigux/validate_phase2_closure.zig");

    for (phase1_steps) |step| {
        try requireAfter(&previous, workflow, step.name);
        try requireAfter(&previous, workflow, step.run);
    }

    try requireAfter(&previous, workflow, "      - name: Self-test current Phase 3 interop packet");
    try requireAfter(&previous, workflow, "        run: zig run scripts/zigux/validate_phase3_selftest.zig");

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
        \\        run: zig run scripts/zigux/validate_phase2_closure.zig
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase1Roster(workflow));
}

test "roster contract rejects duplicate Phase 1 workflow step names" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const duplicate = try std.mem.concat(std.testing.allocator, u8, &.{
        workflow,
        "\n      - name: Check current Phase 1 bench packet\n        run: zig run scripts/zigux/check_phase1_bench.zig\n",
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
